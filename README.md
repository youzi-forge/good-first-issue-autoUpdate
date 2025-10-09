# Good First Issues — Auto-Updated

This repository publishes a **regularly auto‑updated list of `good first issue`‑style issues** across GitHub (covering the labels `good first issue`, `good-first-issue`, and `first-timers-only`), limited to repositories with **≥1000⭐ by default** and issues **opened within the last 90 days**.

> Auto-updated by GitHub Actions every 3 days. Configure thresholds in the workflow or script args.

---

<!--START_GOOD_FIRST_ISSUES-->
*(first run has no data yet; this section will be filled by the workflow)*
<!--END_GOOD_FIRST_ISSUES-->

---

## How it works
- Uses GitHub GraphQL Search to fetch issues whose labels include `good first issue`, `good-first-issue`, or `first-timers-only`, within rolling time windows to avoid the 1000-result cap. Default window is 5 days per request.
- Filters by time window: by default uses creation date (created:). You can switch to updated date using `--date-field updated`.
- Display order: per-repo issues are sorted by last updated time (updatedAt desc), with createdAt as fallback.
- Optionally scope to one organization via `--org ORGNAME` to narrow results.
- Filters by repo stars via `--min-stars/--max-stars` (CI defaults to ≥1000★).
- Renders grouped Markdown here in README.

## Local run

Linux/macOS
```bash
python -m pip install -r requirements.txt
export GITHUB_TOKEN=ghp_xxx
python github_good_first_issue_finder.py --days 90 --min-stars 300 --max-stars 2000 --state open --chunk-days 5 --out good_first_issues.md
# Scope to one org (optional):
python github_good_first_issue_finder.py --days 30 --min-stars 300 --state open --chunk-days 5 --org stdlib-js --out good_first_issues.md
# Use updated date field (optional):
python github_good_first_issue_finder.py --days 30 --min-stars 300 --state open --chunk-days 5 --date-field updated --out good_first_issues.md
python scripts/insert_section.py --readme README.md --input good_first_issues.md
```

Windows (PowerShell)
```powershell
py -3 -m pip install -r requirements.txt
$env:GITHUB_TOKEN = 'ghp_xxx'
py -3 github_good_first_issue_finder.py --days 90 --min-stars 300 --max-stars 2000 --state open --chunk-days 5 --out good_first_issues.md
# Scope to one org (optional):
py -3 github_good_first_issue_finder.py --days 30 --min-stars 300 --state open --chunk-days 5 --org stdlib-js --out good_first_issues.md
# Use updated date field (optional):
py -3 github_good_first_issue_finder.py --days 30 --min-stars 300 --state open --chunk-days 5 --date-field updated --out good_first_issues.md
py -3 scripts/insert_section.py --readme README.md --input good_first_issues.md
```

- Notes
  - `--max-stars` is optional; omit it for “no upper bound”.
  - CI defaults use `--min-stars 1000` and `--chunk-days 5` to reduce output size and avoid the 1000-result cap per query.
