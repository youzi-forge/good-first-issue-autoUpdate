# Good First Issues — Daily Auto-Updated

This repository publishes a **daily-updated list of `good first issue`-style issues** across GitHub (covering the labels `good first issue`, `good-first-issue`, and `first-timers-only`), limited to repositories with **≥300⭐** and issues **opened within the last 90 days**.

> Auto-updated by GitHub Actions once a day. Configure thresholds in the workflow or script args.

---

<!--START_GOOD_FIRST_ISSUES-->
*(first run has no data yet; this section will be filled by the workflow)*
<!--END_GOOD_FIRST_ISSUES-->

---

## How it works
- Uses GitHub GraphQL Search to fetch issues whose labels include `good first issue`, `good-first-issue`, or `first-timers-only`, within rolling time windows to avoid the 1000-result cap.
- Filters to repositories with at least 300 stars.
- Renders grouped Markdown here in README.

## Local run

Linux/macOS
```bash
python -m pip install -r requirements.txt
export GITHUB_TOKEN=ghp_xxx
python github_good_first_issue_finder.py --days 90 --min-stars 300 --state open --chunk-days 7 --out good_first_issues.md
python scripts/insert_section.py --readme README.md --input good_first_issues.md
```

Windows (PowerShell)
```powershell
py -3 -m pip install -r requirements.txt
$env:GITHUB_TOKEN = 'ghp_xxx'
py -3 github_good_first_issue_finder.py --days 90 --min-stars 300 --state open --chunk-days 7 --out good_first_issues.md
py -3 scripts/insert_section.py --readme README.md --input good_first_issues.md
```
