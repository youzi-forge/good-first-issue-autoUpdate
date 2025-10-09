#!/usr/bin/env python3
"""
Find site-wide "good first issue" issues filed within the last N days,
but only from repositories with >= MIN_STARS.

Uses GitHub GraphQL API so we can fetch repository stargazerCount together
with issues (fewer requests than REST) and paginates across date buckets
to avoid the 1000-result cap of GitHub search.

Usage:
  export GITHUB_TOKEN=ghp_xxx_or_fine_grained_token
  python github_good_first_issue_finder.py --days 90 --min-stars 300 --state open --chunk-days 7 --out good_first_issues.md

Notes:
- Qualifiers used per request: label:"good first issue" (and other variants) is:open created:YYYY-MM-DD..YYYY-MM-DD archived:false
- Replace --state with "all" to include closed issues as well.
- GraphQL rate limit is respected via headers (X-RateLimit-Remaining/Reset) and simple backoff.
"""

import os
import sys
import time
import argparse
import datetime as dt
import requests
from collections import defaultdict

GQL_ENDPOINT = "https://api.github.com/graphql"
"""
Network settings: conservative timeouts and bounded retries to avoid
indefinite hangs while being polite to the GitHub API.
"""
REQUEST_TIMEOUT = (10, 30)  # (connect, read) seconds
MAX_RETRIES = 5
BACKOFF_INITIAL = 1.0  # seconds
BACKOFF_MAX = 60.0     # cap backoff growth

LABEL_VARIANTS = (
    "good first issue",
    "good-first-issue",
    "first-timers-only",
)
_label_terms = [f'label:"{name}"' for name in LABEL_VARIANTS]

def gh_post(token: str, query: str, variables: dict):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
        "User-Agent": "good-first-issue-finder/1.0"
    }
    payload = {"query": query, "variables": variables}
    attempt = 0
    backoff = BACKOFF_INITIAL
    while True:
        # Network call with timeout and basic retry for transient failures
        try:
            resp = requests.post(
                GQL_ENDPOINT, headers=headers, json=payload, timeout=REQUEST_TIMEOUT
            )
        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES:
                wait = backoff
                print(
                    f"[net] Timeout; retrying in {wait:.1f}s (attempt {attempt+1}/{MAX_RETRIES})",
                    file=sys.stderr,
                    flush=True,
                )
                time.sleep(wait)
                attempt += 1
                backoff = min(backoff * 2, BACKOFF_MAX)
                continue
            raise
        except requests.exceptions.RequestException as e:
            if attempt < MAX_RETRIES:
                wait = backoff
                print(
                    f"[net] Request error: {e}; retrying in {wait:.1f}s (attempt {attempt+1}/{MAX_RETRIES})",
                    file=sys.stderr,
                    flush=True,
                )
                time.sleep(wait)
                attempt += 1
                backoff = min(backoff * 2, BACKOFF_MAX)
                continue
            raise
        # Handle primary/secondary rate limits
        if resp.status_code == 429:
            ra = resp.headers.get("Retry-After")
            try:
                wait = int(ra) if ra is not None else 30
            except ValueError:
                wait = 30
            print(f"[rate-limit] 429 Too Many Requests; waiting {wait}s...", file=sys.stderr, flush=True)
            time.sleep(wait)
            continue
        if resp.status_code == 403 and (
            "rate limit" in resp.text.lower()
            or "secondary rate" in resp.text.lower()
            or resp.headers.get("X-RateLimit-Remaining") == "0"
        ):
            reset = resp.headers.get("X-RateLimit-Reset")
            if reset and reset.isdigit():
                wait = max(0, int(reset) - int(time.time()) + 1)
            else:
                wait = 30
            print(f"[rate-limit] Waiting {wait}s...", file=sys.stderr, flush=True)
            time.sleep(wait)
            continue
        # Retry on transient 5xx responses with backoff
        if 500 <= resp.status_code < 600:
            if attempt < MAX_RETRIES:
                wait = backoff
                print(
                    f"[server] {resp.status_code} from GitHub; retrying in {wait:.1f}s...",
                    file=sys.stderr,
                    flush=True,
                )
                time.sleep(wait)
                attempt += 1
                backoff = min(backoff * 2, BACKOFF_MAX)
                continue
        resp.raise_for_status()
        data = resp.json()
        if "errors" in data:
            # Some transient errors can be retried
            msg = str(data["errors"])
            if "Something went wrong while executing your query" in msg or "timed out" in msg:
                if attempt < MAX_RETRIES:
                    wait = backoff
                    print(
                        f"[gql] Transient GraphQL error; retrying in {wait:.1f}s...",
                        file=sys.stderr,
                        flush=True,
                    )
                    time.sleep(wait)
                    attempt += 1
                    backoff = min(backoff * 2, BACKOFF_MAX)
                    continue
                raise RuntimeError(f"GraphQL errors after retries: {msg}")
            raise RuntimeError(f"GraphQL errors: {msg}")
        return data, resp.headers

GQL_SEARCH = """
query SearchIssues($q:String!, $after:String) {
  search(query:$q, type:ISSUE, first:100, after:$after) {
    issueCount
    pageInfo { hasNextPage endCursor }
    nodes {
      ... on Issue {
        title
        number
        url
        createdAt
        state
        repository {
          nameWithOwner
          url
          stargazerCount
          isArchived
        }
        labels(first: 10) {
          nodes { name }
        }
      }
    }
  }
}
"""

def build_query_for_window(start_date: dt.date, end_date: dt.date, state: str, label: str, org: str | None = None) -> str:
    # Inclusive day range like 2025-07-01..2025-07-07
    date_range = f"{start_date.isoformat()}..{end_date.isoformat()}"
    state_qual = " is:open" if state.lower() == "open" else ""
    # Use a single label per query (avoid OR grouping quirks) and restrict to issues only
    org_qual = f" org:{org}" if org else ""
    q = f'label:"{label}" is:issue{state_qual}{org_qual} created:{date_range} archived:false'
    return q

def daterange_chunks(days_back: int, chunk_days: int):
    today = dt.date.today()
    start = today - dt.timedelta(days=days_back)
    # build [start..start+chunk-1], [next..], ... until today
    current = start
    while current <= today:
        end = min(current + dt.timedelta(days=chunk_days-1), today)
        yield current, end
        current = end + dt.timedelta(days=1)

def collect_issues(token: str, days_back: int, min_stars: int, max_stars: int | None, state: str, chunk_days: int, org: str | None = None):
    grouped = defaultdict(list)  # repo_full_name -> list of issues
    repo_star = {}  # repo_full_name -> star count
    total_seen = 0
    seen_issue_urls = set()
    for idx, (s, e) in enumerate(daterange_chunks(days_back, chunk_days), start=1):
        print(f"[info] Window {idx}: {s} → {e}", file=sys.stderr, flush=True)
        window_seen = 0
        for label in LABEL_VARIANTS:
            q = build_query_for_window(s, e, state, label, org)
            after = None
            label_seen = 0
            first_page = True
            while True:
                data, headers = gh_post(token, GQL_SEARCH, {"q": q, "after": after})
                search = data["data"]["search"]
                nodes = search["nodes"]
                if first_page:
                    print(
                        f"[info]   Label '{label}': issueCount={search.get('issueCount', 'n/a')}",
                        file=sys.stderr,
                        flush=True,
                    )
                    first_page = False
                for node in nodes:
                    # Skip non-Issue nodes (GraphQL returns PRs in type:ISSUE unless restricted by is:issue)
                    if not isinstance(node, dict) or "repository" not in node:
                        continue
                    repo = node["repository"]
                    if repo.get("isArchived"):
                        continue
                    url = node.get("url")
                    if not url:
                        continue
                    if url in seen_issue_urls:
                        continue
                    seen_issue_urls.add(url)
                    full = repo.get("nameWithOwner", "")
                    stars = int((repo.get("stargazerCount") or 0))
                    repo_star[full] = stars
                    if stars >= min_stars and (max_stars is None or stars <= max_stars):
                        grouped[full].append({
                            "title": node.get("title", ""),
                            "number": node.get("number", 0),
                            "url": url,
                            "createdAt": node.get("createdAt", ""),
                            "state": node.get("state", ""),
                            "labels": [lab["name"] for lab in (node.get("labels", {}) or {}).get("nodes", [])],
                            "repo_url": repo.get("url", ""),
                            "stars": stars
                        })
                total_seen += len(nodes)
                window_seen += len(nodes)
                label_seen += len(nodes)
                if not search["pageInfo"]["hasNextPage"]:
                    break
                after = search["pageInfo"]["endCursor"]
            print(
                f"[info]     Finished label '{label}': scanned {label_seen} issues",
                file=sys.stderr,
                flush=True,
            )
        # Simple polite pacing between windows
        time.sleep(0.3)
        print(
            f"[info]   Completed window {idx}: scanned {window_seen} issues; repos matched so far {len(grouped)}",
            file=sys.stderr,
            flush=True,
        )
    return grouped, repo_star, total_seen

def render_markdown(grouped, repo_star, title: str):
    lines = [f"# {title}", "", f"_Generated at: {dt.datetime.utcnow().isoformat()}Z_  ", ""]
    # order repos by stars desc
    repos_sorted = sorted(grouped.items(), key=lambda kv: (repo_star.get(kv[0], 0), kv[0]), reverse=True)
    for full, issues in repos_sorted:
        stars = repo_star.get(full, 0)
        repo_url = issues[0]["repo_url"] if issues else ""
        lines.append(f"## {full}  ⭐ {stars}")
        if repo_url:
            lines.append(f"[Repository]({repo_url})")
        lines.append("")
        # sort issues by createdAt desc
        issues_sorted = sorted(issues, key=lambda it: it["createdAt"], reverse=True)
        for it in issues_sorted:
            labels = ", ".join(it["labels"]) if it["labels"] else "-"
            lines.append(f"- [{it['title']}]({it['url']})  `#{it['number']}` · {it['createdAt']} · labels: {labels}")
        lines.append("")
    if not repos_sorted:
        lines.append("> No matching issues found.")
    return "\n".join(lines)

def main():
    ap = argparse.ArgumentParser(description="Find 'good first issue' in repos with >= N stars (GraphQL).")
    ap.add_argument("--days", type=int, default=90, help="How many past days to search (default: 90).")
    ap.add_argument("--min-stars", type=int, default=300, help="Minimum repo stars (default: 300).")
    ap.add_argument("--max-stars", type=int, default=None, help="Optional maximum repo stars (default: no upper bound).")
    ap.add_argument("--state", type=str, default="open", choices=["open","all"], help="Open only or all issues.")
    ap.add_argument("--chunk-days", type=int, default=5, help="Days per search window to bypass 1000-cap (default: 5).")
    ap.add_argument("--org", type=str, default=None, help="Optional organization to scope the search (e.g., 'stdlib-js').")
    ap.add_argument("--out", type=str, default="good_first_issues.md", help="Output Markdown file.")
    args = ap.parse_args()

    errors = []
    if args.days <= 0:
        errors.append("--days must be > 0")
    if args.chunk_days <= 0:
        errors.append("--chunk-days must be > 0")
    if args.min_stars < 0:
        errors.append("--min-stars must be >= 0")
    if args.max_stars is not None and args.max_stars < args.min_stars:
        errors.append("--max-stars must be >= --min-stars")
    if errors:
        for msg in errors:
            print(f"ERROR: {msg}", file=sys.stderr)
        sys.exit(2)

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("ERROR: Please set GITHUB_TOKEN environment variable.", file=sys.stderr)
        sys.exit(2)

    print(
        "[info] Starting fetch: days={} min-stars={} max-stars={} state={} chunk={} org={}".format(
            args.days,
            args.min_stars,
            (args.max_stars if args.max_stars is not None else '∞'),
            args.state,
            args.chunk_days,
            (args.org or '-')
        ),
        file=sys.stderr,
        flush=True,
    )

    grouped, repo_star, total_seen = collect_issues(
        token=token,
        days_back=args.days,
        min_stars=args.min_stars,
        max_stars=args.max_stars,
        state=args.state,
        chunk_days=args.chunk_days,
        org=args.org
    )
    if args.max_stars is None:
        title = f"Good First Issues (last {args.days} days, repos ≥ {args.min_stars}★, state={args.state})"
    else:
        title = f"Good First Issues (last {args.days} days, {args.min_stars}★–{args.max_stars}★, state={args.state})"
    md = render_markdown(grouped, repo_star, title)
    print(
        f"[info] Writing results to {args.out} (repos matched: {len(grouped)}, issues scanned: ~{total_seen})",
        file=sys.stderr,
        flush=True,
    )
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Wrote {args.out}. Scanned issues: ~{total_seen}. Repositories matched: {len(grouped)}")
    # Also print a short preview to stdout
    print("\n--- Preview ---\n")
    print("\n".join(md.splitlines()[:40]))

if __name__ == "__main__":
    main()
