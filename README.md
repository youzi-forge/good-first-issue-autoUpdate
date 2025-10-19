# Good First Issues — Auto-Updated

[![Update List](https://github.com/youzi-forge/good-first-issue-autoUpdate/actions/workflows/update-good-first-issues.yml/badge.svg)](https://github.com/youzi-forge/good-first-issue-autoUpdate/actions/workflows/update-good-first-issues.yml)
[![Deploy Pages](https://github.com/youzi-forge/good-first-issue-autoUpdate/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/youzi-forge/good-first-issue-autoUpdate/actions/workflows/deploy-pages.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Find recently opened, beginner‑friendly issues in popular GitHub repositories.

This repo publishes a regularly auto‑updated list of issues labeled like `good first issue` (including `good-first-issue` and `first-timers-only`). CI builds the full list and serves it on GitHub Pages. Locally you can customize filters via script arguments.

- View the live list (updates every 3 days):
  https://youzi-forge.github.io/good-first-issue-autoUpdate/
  · Last updated: <!--LAST_UPDATED-->2025-10-19 04:30 UTC<!--/LAST_UPDATED-->

## At a Glance
- Update cadence: every 3 days (via GitHub Actions)
- Default filters (for the published list): last 90 days, repositories ≥1000★, open issues
- Sorting: repositories by stars (desc, then name asc); issues by last updated (desc)
- Label variants matched: `good first issue`, `good-first-issue`, `first-timers-only`

---

## Project Info
- Live site: https://youzi-forge.github.io/good-first-issue-autoUpdate/ · Last updated: <!--LAST_UPDATED-->2025-10-09 11:49 UTC<!--/LAST_UPDATED-->
- Workflows: [Update list](.github/workflows/update-good-first-issues.yml), [Deploy Pages](.github/workflows/deploy-pages.yml)
- License: [MIT](LICENSE)
- Releases: https://github.com/youzi-forge/good-first-issue-autoUpdate/releases

---

## How It Works
- Fetches issues via GitHub GraphQL Search within rolling time windows to avoid the 1000‑result cap (default window: 5 days per request, with automatic splitting near high‑volume periods).
- Filters by time window: uses creation date (`created:`) by default; switch to `--date-field updated` if needed.
- Sorts per‑repo issues by last updated time (updatedAt desc; fallback createdAt).
- Supports scoping to one organization via `--org ORGNAME`.
- Filters by stars via `--min-stars/--max-stars` (CI uses ≥1000★ by default).
- Publishes the full list to GitHub Pages; README focuses on usage and links.

## Quick Start (Local)

Linux/macOS
```bash
python -m pip install -r requirements.txt
export GITHUB_TOKEN=ghp_xxx
python github_good_first_issue_finder.py --days 90 --min-stars 300 --max-stars 2000 --state open --chunk-days 5 --out good_first_issues.md
# Scope to one org (optional):
python github_good_first_issue_finder.py --days 30 --min-stars 300 --state open --chunk-days 5 --org stdlib-js --out good_first_issues.md
# Use updated date field (optional):
python github_good_first_issue_finder.py --days 30 --min-stars 300 --state open --chunk-days 5 --date-field updated --out good_first_issues.md
# Build local HTML for preview (optional):
python scripts/build_site.py --input good_first_issues.md --outdir _site --title "Good First Issues"
# Then open _site/index.html in your browser
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
# Build local HTML for preview (optional):
py -3 scripts/build_site.py --input good_first_issues.md --outdir _site --title "Good First Issues"
# Then open _site/index.html
```

## Defaults
- CI (published list): `--min-stars 1000`, `--chunk-days 5`, `--days 90`, `--state open`
- Script defaults: `--min-stars 300`, `--chunk-days 5`, `--days 90`, `--state open`
- `--max-stars` is optional; omit it for no upper bound

## CLI Options

- `--days` (int, default `90`): Number of past days to search.
- `--date-field` (`created`|`updated`, default `created`): Which timestamp the search window applies to.
- `--min-stars` (int, default `300`): Minimum repository stars to include.
- `--max-stars` (int, optional): Maximum repository stars; must be `>= --min-stars` if provided.
- `--state` (`open`|`all`, default `open`): Whether to include closed issues.
- `--chunk-days` (int, default `5`): Initial days per search window; autosplitting may refine windows near high‑volume periods.
- `--no-auto-chunk` (flag): Disable autosplitting.
- `--cap-per-query` (int, default `950`): Target maximum matches per label per window before splitting.
- `--org` (string, optional): Scope search to a single organization (e.g., `stdlib-js`).
- `--out` (path, default `good_first_issues.md`): Output Markdown file.
- `GITHUB_TOKEN` (env): Required GitHub token. A Personal access token (classic) is recommended for broad public search.

## Troubleshooting

- No or too few results
  - Verify `GITHUB_TOKEN` is set and is a classic PAT. Fine‑grained tokens can restrict search scope.
  - Reduce `--chunk-days` (e.g., `5` → `2` or `1`) to lower per-query volume.
  - Try `--date-field updated` if you care about recent activity rather than creation date.
  - Use `--org ORGNAME` to limit scope and avoid hitting API caps.
- Output too large
  - Increase `--min-stars`, set `--max-stars`, reduce `--days`, or scope with `--org`.
- Logs show `issueCount` near 1000 but `scanned` ~1000
  - GitHub caps each search at ~1000 accessible results. Shrink `--chunk-days` and/or add `--org`.
- Rate limiting
  - The script backs off automatically. If it pauses, let it continue or rerun later.
