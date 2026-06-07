# Good First Issues — Auto-Updated

[![Update List](https://github.com/youzi-forge/good-first-issue-autoUpdate/actions/workflows/update-good-first-issues.yml/badge.svg)](https://github.com/youzi-forge/good-first-issue-autoUpdate/actions/workflows/update-good-first-issues.yml)
[![Deploy Pages](https://github.com/youzi-forge/good-first-issue-autoUpdate/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/youzi-forge/good-first-issue-autoUpdate/actions/workflows/deploy-pages.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Find recently opened, beginner-friendly issues in popular GitHub repositories.

This repo publishes a regularly auto-updated list of issues labeled like `good first issue` (including `good-first-issue` and `first-timers-only`). CI builds the full list and serves it on GitHub Pages. Locally, you can customize filters via script arguments.

- View the live list (updates every 3 days):
  https://youzi-forge.github.io/good-first-issue-autoUpdate/
  · Last updated: <!--LAST_UPDATED-->2026-06-07 06:08 UTC<!--/LAST_UPDATED-->

## At a Glance
- Update cadence: every 3 days (via GitHub Actions)
- Default filters (for the published list): last 90 days, repositories ≥1000★, open issues
- Sorting: repositories by stars (desc, then name asc); issues by last updated (desc)
- Label variants matched: `good first issue`, `good-first-issue`, `first-timers-only`

---

## Project Info
- Live site: https://youzi-forge.github.io/good-first-issue-autoUpdate/ · Last updated: <!--LAST_UPDATED-->2026-06-07 06:08 UTC<!--/LAST_UPDATED-->
- Workflows: [Update list](.github/workflows/update-good-first-issues.yml), [Deploy Pages](.github/workflows/deploy-pages.yml)
- License: [MIT](LICENSE)
- Releases: https://github.com/youzi-forge/good-first-issue-autoUpdate/releases

---

## How It Works
- Fetches issues via GitHub GraphQL Search within rolling time windows to avoid the 1000-result cap (default window: 5 days per request, with automatic splitting near high-volume periods).
- Filters by time window: uses creation date (`created:`) by default; switch to `--date-field updated` if needed.
- Groups issues by repository and sorts: repositories by stars (desc), issues within each repo by last updated time (desc).
- Supports limiting results to a single organisation via `--org ORGNAME`.
- Filters by stars via `--min-stars/--max-stars` (CI uses ≥1000★ by default).
- Publishes a modern React-based web app to GitHub Pages with interactive search, filters, and pagination.
- For local use, generates a standalone HTML file with embedded data (no dependencies required).

## Quick Start (Local)

### Option 1: Interactive React UI (Recommended)
Run the crawler with `--json` to generate structured data, and refresh the standalone HTML after a frontend build.

**One-time frontend setup for generating standalone HTML output:**
```bash
cd frontend
npm ci
npm run build
cd ..
