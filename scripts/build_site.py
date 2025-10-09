#!/usr/bin/env python3
"""
Build a minimal static site for the generated Good First Issues Markdown.

Usage:
  python scripts/build_site.py --input good_first_issues.md --outdir _site \
         --title "Good First Issues"

Notes:
- Attempts to use the 'markdown' library if available; otherwise falls back to a
  very simple preformatted rendering so that CI/local runs still succeed.
"""

import argparse
import pathlib
import sys
import html
import datetime as dt


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <style>
      :root {{
        --fg: #111;
        --bg: #ffffff;
        --muted: #666;
        --accent: #0969da;
        --border: #e5e7eb;
      }}
      @media (prefers-color-scheme: dark) {{
        :root {{
          --fg: #e5e7eb;
          --bg: #0b0d11;
          --muted: #9ca3af;
          --accent: #4ea1ff;
          --border: #1f2937;
        }}
      }}
      body {{
        margin: 0;
        background: var(--bg);
        color: var(--fg);
        font: 16px/1.55 -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, Noto Sans, Apple Color Emoji, Segoe UI Emoji, Segoe UI Symbol;
      }}
      .wrap {{
        max-width: 980px;
        margin: 0 auto;
        padding: 24px 16px 80px;
      }}
      header {{
        border-bottom: 1px solid var(--border);
        padding-bottom: 12px;
        margin-bottom: 24px;
      }}
      h1 {{ font-size: 1.6rem; margin: 0 0 6px 0; }}
      .meta {{ color: var(--muted); font-size: 0.92rem; }}
      a {{ color: var(--accent); text-decoration: none; }}
      a:hover {{ text-decoration: underline; }}
      code, pre {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, Liberation Mono, monospace; }}
      pre {{ background: rgba(127,127,127,.08); padding: 12px; border-radius: 8px; overflow: auto; }}
      .content h2 {{ margin-top: 1.5em; border-bottom: 1px dotted var(--border); padding-bottom: 4px; }}
      .content li {{ margin: 4px 0; }}
      .notice {{ background: rgba(9,105,218,0.08); border: 1px solid var(--border); padding: 10px 12px; border-radius: 8px; }}
    </style>
  </head>
  <body>
    <div class="wrap">
      <header>
        <h1>{title}</h1>
        <div class="meta">Generated at: {ts}</div>
        <p class="meta">This page is built from the repository's generated Markdown.</p>
      </header>

      <div class="content">
        {body}
      </div>

      <footer class="meta" style="margin-top:40px;">
        <p>Made with ❤️ · <a href="https://github.com/">GitHub</a> Pages</p>
      </footer>
    </div>
  </body>
  </html>
"""


def md_to_html(md_text: str) -> str:
    """Convert Markdown to HTML, prefer 'markdown' library if available."""
    try:
        import markdown  # type: ignore
        return markdown.markdown(md_text, extensions=["extra", "sane_lists", "tables"])  # pragma: no cover
    except Exception:
        # ultra-simple fallback: escape and wrap in <pre>
        return f"<pre>{html.escape(md_text)}</pre>"


def main() -> int:
    ap = argparse.ArgumentParser(description="Build a static HTML page from a Markdown file.")
    ap.add_argument("--input", default="good_first_issues.md", help="Input Markdown file (default: good_first_issues.md)")
    ap.add_argument("--outdir", default="_site", help="Output directory (default: _site)")
    ap.add_argument("--title", default="Good First Issues", help="Page title")
    args = ap.parse_args()

    in_path = pathlib.Path(args.input)
    if not in_path.exists():
        print(f"ERROR: input file not found: {in_path}", file=sys.stderr)
        return 2

    md_text = in_path.read_text(encoding="utf-8")
    body_html = md_to_html(md_text)
    ts = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    html_out = HTML_TEMPLATE.format(title=args.title, ts=ts, body=body_html)

    outdir = pathlib.Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    out_file = outdir / "index.html"
    out_file.write_text(html_out, encoding="utf-8")
    print(f"Wrote {out_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

