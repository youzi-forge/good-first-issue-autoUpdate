# Good First Issues — Auto-Updated

[![Update List](https://github.com/youzi-forge/good-first-issue-autoUpdate/actions/workflows/update-good-first-issues.yml/badge.svg)](https://github.com/youzi-forge/good-first-issue-autoUpdate/actions/workflows/update-good-first-issues.yml)
[![Deploy Pages](https://github.com/youzi-forge/good-first-issue-autoUpdate/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/youzi-forge/good-first-issue-autoUpdate/actions/workflows/deploy-pages.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Find recently opened, beginner‑friendly issues in popular GitHub repositories.

This repo publishes a regularly auto‑updated list of issues labeled like `good first issue` (including `good-first-issue` and `first-timers-only`). CI builds the full list and serves it on GitHub Pages. Locally you can customize filters via script arguments.

- View the live list (updates every 3 days):
  https://youzi-forge.github.io/good-first-issue-autoUpdate/
  · Last updated: <!--LAST_UPDATED-->2026-01-10 04:42 UTC<!--/LAST_UPDATED-->

## At a Glance
- Update cadence: every 3 days (via GitHub Actions)
- Default filters (for the published list): last 90 days, repositories ≥1000★, open issues
- Sorting: repositories by stars (desc, then name asc); issues by last updated (desc)
- Label variants matched: `good first issue`, `good-first-issue`, `first-timers-only`

---

## Project Info
- Live site: https://youzi-forge.github.io/good-first-issue-autoUpdate/ · Last updated: <!--LAST_UPDATED-->2026-01-10 04:42 UTC<!--/LAST_UPDATED-->
- Workflows: [Update list](.github/workflows/update-good-first-issues.yml), [Deploy Pages](.github/workflows/deploy-pages.yml)
- License: [MIT](LICENSE)
- Releases: https://github.com/youzi-forge/good-first-issue-autoUpdate/releases

---

## How It Works
- Fetches issues via GitHub GraphQL Search within rolling time windows to avoid the 1000‑result cap (default window: 5 days per request, with automatic splitting near high‑volume periods).
- Filters by time window: uses creation date (`created:`) by default; switch to `--date-field updated` if needed.
- Groups issues by repository and sorts: repositories by stars (desc), issues within each repo by last updated time (desc).
- Supports scoping to one organization via `--org ORGNAME`.
- Filters by stars via `--min-stars/--max-stars` (CI uses ≥1000★ by default).
- Publishes a modern React-based web app to GitHub Pages with interactive search, filters, and pagination.
- For local use, generates a standalone HTML file with embedded data (no dependencies required).

## Quick Start (Local)

### Option 1: Interactive React UI (Recommended)
Run the crawler with `--json` flag to automatically generate a standalone HTML file:

**Linux/macOS:**
```bash
python3 -m pip install -r requirements.txt
export GITHUB_TOKEN=ghp_xxx
python3 github_good_first_issue_finder.py --days 90 --min-stars 300 --json --out my_data.json
```

**What gets generated:**
- `my_data.json` - Structured data (intermediate file, used to generate HTML)
- `_site/index.html` - **Standalone HTML** with embedded React UI and data

**To view:**
```bash
open _site/index.html  # macOS
# or double-click the file in your file explorer
```

**Windows (PowerShell):**
```powershell
py -3 -m pip install -r requirements.txt
$env:GITHUB_TOKEN = 'ghp_xxx'
py -3 github_good_first_issue_finder.py --days 90 --min-stars 300 --json --out my_data.json
start _site/index.html
```

**About the generated files:**
- **`_site/index.html`**: This is what you open in your browser. It's a complete, self-contained webpage with:
  - Full React UI (search, filters, pagination, dark mode)
  - Your custom-crawled data already embedded inside
  - Works offline, no dependencies needed
  - Can be shared as a single file
- **`my_data.json`**: Intermediate data file used to generate the HTML. You can delete it after the HTML is created, or keep it for future reference.

### Option 2: Markdown Output (Simple)
For quick text-based viewing:
```bash
python3 github_good_first_issue_finder.py --days 90 --min-stars 300 --out good_first_issues.md
# View in terminal or text editor
```

### Option 3: UI Development/Preview (No API Token Required)
If you just want to preview the UI or work on frontend development without running the crawler:

```bash
# Use the existing sample data in the repo
python3 scripts/build_standalone.py --data frontend/public/data.json

# Open the generated HTML
open _site/index.html
```

This is useful for:
- **Frontend developers**: Test UI changes without crawling data
- **Contributors**: Preview the interface before making changes
- **Quick demo**: See what the app looks like without setting up a GitHub token

### Advanced Examples
```bash
# Scope to one organization:
python3 github_good_first_issue_finder.py \
  --days 30 \
  --min-stars 300 \
  --state open \
  --chunk-days 5 \
  --org stdlib-js \
  --json --out data.json

# Use updated date field instead of created:
python3 github_good_first_issue_finder.py \
  --days 30 \
  --min-stars 300 \
  --state open \
  --chunk-days 5 \
  --date-field updated \
  --json --out data.json

# Set star range (min and max):
python3 github_good_first_issue_finder.py \
  --days 90 \
  --min-stars 300 \
  --max-stars 2000 \
  --state open \
  --chunk-days 5 \
  --json --out data.json

# Full parameter example (all common options):
python3 github_good_first_issue_finder.py \
  --days 60 \
  --min-stars 500 \
  --max-stars 5000 \
  --state open \
  --chunk-days 3 \
  --org facebook \
  --date-field updated \
  --json \
  --out my_custom_data.json

# Markdown output instead of JSON/HTML:
python3 github_good_first_issue_finder.py \
  --days 90 \
  --min-stars 1000 \
  --state open \
  --out good_first_issues.md
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
- `--out` (path, default `good_first_issues.md`): Output file path. Extension determines format (`.md` for Markdown, `.json` for JSON).
- `--json` (flag): Output JSON format and automatically generate standalone HTML (`_site/index.html`). When used, `--out` should specify the JSON file path.
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
