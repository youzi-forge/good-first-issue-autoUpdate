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


HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <style>
      :root {{
        --fg: #111;
        --bg: #f8fafc;
        --muted: #5f6368;
        --accent: #0969da;
        --border: #e2e8f0;
        --card: #ffffff;
        --shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
      }}
      @media (prefers-color-scheme: dark) {{
        :root {{
          --fg: #e5e7eb;
          --bg: #05070c;
          --muted: #9ca3af;
          --accent: #4ea1ff;
          --border: #1f2937;
          --card: #0f172a;
          --shadow: 0 12px 28px rgba(0, 0, 0, 0.65);
        }}
      }}
      * {{
        box-sizing: border-box;
      }}
      body {{
        margin: 0;
        font: 16px/1.55 -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, Noto Sans, Apple Color Emoji, Segoe UI Emoji, Segoe UI Symbol;
        background: var(--bg);
        color: var(--fg);
        min-height: 100vh;
      }}
      a {{
        color: var(--accent);
        text-decoration: none;
      }}
      a:hover {{
        text-decoration: underline;
      }}
      code, pre {{
        font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, Liberation Mono, monospace;
      }}
      pre {{
        background: rgba(127, 127, 127, 0.08);
        padding: 12px;
        border-radius: 8px;
        overflow: auto;
      }}
      .wrap {{
        max-width: 1100px;
        margin: 0 auto;
        padding: 24px 16px 80px;
      }}
      .page-header {{
        margin-bottom: 32px;
      }}
      .hero {{
        border-bottom: 1px solid var(--border);
        padding-bottom: 16px;
        margin-bottom: 16px;
      }}
      .hero h1 {{
        font-size: 1.9rem;
        margin: 0 0 8px 0;
      }}
      .meta {{
        color: var(--muted);
        font-size: 0.95rem;
      }}
      .toolbar {{
        position: sticky;
        top: 0;
        z-index: 10;
        background: var(--bg);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 16px;
        box-shadow: var(--shadow);
      }}
      .toolbar-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 16px;
      }}
      .toolbar-field label {{
        display: block;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 6px;
        color: var(--muted);
      }}
      .toolbar-field input,
      .toolbar-field select {{
        width: 100%;
        border: 1px solid var(--border);
        background: var(--card);
        color: var(--fg);
        border-radius: 10px;
        padding: 10px 12px;
        font-size: 0.95rem;
      }}
      .toolbar-field input:focus,
      .toolbar-field select:focus {{
        outline: 2px solid var(--accent);
        outline-offset: 2px;
      }}
      .toolbar-actions {{
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        align-items: flex-end;
      }}
      .toolbar-actions button {{
        border: 1px solid var(--border);
        background: var(--card);
        color: var(--fg);
        padding: 10px 16px;
        border-radius: 999px;
        font-size: 0.95rem;
        cursor: pointer;
        transition: background 0.2s ease, border-color 0.2s ease;
      }}
      .toolbar-actions button:hover {{
        background: rgba(9, 105, 218, 0.08);
        border-color: var(--accent);
      }}
      .toolbar-actions button:focus {{
        outline: 2px solid var(--accent);
        outline-offset: 2px;
      }}
      .toolbar-status {{
        margin-top: 14px;
        font-size: 0.9rem;
        color: var(--muted);
      }}
      main {{
        display: block;
      }}
      .content {{
        margin-top: 24px;
      }}
      .content h1:first-of-type {{
        margin-top: 0;
      }}
      .content h2 {{
        margin-top: 2rem;
        padding-bottom: 8px;
        border-bottom: 1px solid var(--border);
        font-size: 1.25rem;
      }}
      .content ul {{
        list-style: none;
        padding-left: 0;
        margin: 0.6rem 0 1.6rem 0;
      }}
      .content li {{
        margin: 0;
        padding: 12px 14px;
        border-radius: 12px;
        border: 1px solid var(--border);
        background: var(--card);
        box-shadow: var(--shadow);
        margin-bottom: 10px;
      }}
      .content li a {{
        font-weight: 600;
      }}
      .content li code {{
        background: rgba(15, 23, 42, 0.08);
        padding: 2px 6px;
        border-radius: 6px;
        font-size: 0.9rem;
      }}
      .muted {{
        color: var(--muted);
      }}
      .notice {{
        background: rgba(9, 105, 218, 0.08);
        border: 1px solid var(--border);
        padding: 12px 14px;
        border-radius: 12px;
        margin-top: 16px;
      }}
      .repo-card {{
        border: 1px solid var(--border);
        border-radius: 16px;
        margin-bottom: 18px;
        background: var(--card);
        box-shadow: var(--shadow);
        overflow: hidden;
      }}
      .repo-summary {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 20px;
        cursor: pointer;
      }}
      .repo-summary h3 {{
        margin: 0;
        font-size: 1.2rem;
      }}
      .repo-meta {{
        font-size: 0.95rem;
        color: var(--muted);
      }}
      .repo-body {{
        padding: 0 20px 20px 20px;
      }}
      .issue-item {{
        padding: 14px 0;
        border-bottom: 1px solid var(--border);
      }}
      .issue-item:last-child {{
        border-bottom: 0;
      }}
      .label-badges {{
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 6px;
      }}
      .label-badge {{
        font-size: 0.78rem;
        padding: 2px 10px;
        border-radius: 999px;
        border: 1px solid var(--border);
        background: rgba(9, 105, 218, 0.08);
      }}
      .sr-only {{
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        border: 0;
      }}
      @media (max-width: 720px) {{
        .toolbar {{
          position: static;
        }}
        .toolbar-actions {{
          flex-direction: column;
          align-items: stretch;
        }}
        .content li {{
          padding: 10px 12px;
        }}
      }}
    </style>
  </head>
  <body>
    <div class="wrap">
      <header class="page-header" aria-label="Project overview">
        <div class="hero">
          <h1>{title}</h1>
          <div class="meta">Generated at: {ts}</div>
          <p class="meta">This page is built from the repository's generated Markdown.</p>
        </div>
      <section class="toolbar" aria-label="Issue controls">
          <div class="toolbar-grid">
            <div class="toolbar-field">
              <label for="search-input">Search</label>
              <input id="search-input" type="search" placeholder="Search repositories or issues">
            </div>
            <div class="toolbar-field">
              <label for="label-input">Labels</label>
              <input id="label-input" type="text" placeholder="label-a, label-b">
            </div>
          </div>
          <div class="toolbar-actions" aria-label="Visibility controls">
            <button type="button" id="expand-all">Expand all</button>
            <button type="button" id="collapse-all">Collapse all</button>
          </div>
          <div class="toolbar-status" id="toolbar-status" aria-live="polite">
            Showing all repositories · interactive controls activate once JavaScript loads.
          </div>
        </section>
        <noscript>
          <p class="notice">
            Interactive filtering requires JavaScript. The full issue list is still available below.
          </p>
        </noscript>
      </header>

      <main id="app">
        <div class="content" id="issue-content">
          {body}
        </div>
      </main>

      <footer class="meta" style="margin-top:40px;">
        <p>Made with ❤️ · <a href="https://github.com/">GitHub</a> Pages</p>
      </footer>
    </div>
    <script>
    (function () {{
      function onReady(fn) {{
        if (document.readyState === 'loading') {{
          document.addEventListener('DOMContentLoaded', fn, {{ once: true }});
        }} else {{
          fn();
        }}
      }}

      function slugify(s) {{
        return (s || '')
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, '-')
          .replace(/(^-|-$)/g, '');
      }}

      onReady(function initRepoCards() {{
        var content = document.getElementById('issue-content');
        if (!content) return;
        // Find top-level H2s (repositories)
        var h2s = Array.prototype.filter.call(content.children, function (el) {{ return el.tagName === 'H2'; }});
        if (!h2s.length) return; // e.g., no markdown conversion or empty dataset

        var desktop = window.matchMedia('(min-width: 900px)').matches;
        var repoCount = 0;
        var issueTotal = 0;

        h2s.forEach(function (h2) {{
          var raw = (h2.textContent || '').trim();
          var m = raw.match(/^(.+?)\\s*⭐\\s*(\\d+)/);
          var repoName = m ? m[1].trim() : raw;
          var stars = m ? parseInt(m[2], 10) : null;

          var details = document.createElement('details');
          details.className = 'repo-card';
          if (desktop) details.setAttribute('open', '');

          var summary = document.createElement('summary');
          summary.className = 'repo-summary';

          var h3 = document.createElement('h3');
          h3.textContent = repoName;

          var meta = document.createElement('div');
          meta.className = 'repo-meta';
          meta.textContent = stars ? ('⭐ ' + stars) : '';

          summary.appendChild(h3);
          summary.appendChild(meta);

          var body = document.createElement('div');
          body.className = 'repo-body';

          // Insert card before the H2, then move subsequent nodes until the next H2
          content.insertBefore(details, h2);
          details.appendChild(summary);
          details.appendChild(body);
          h2.remove();

          var ptr = details.nextElementSibling;
          while (ptr && ptr.tagName !== 'H2') {{
            var next = ptr.nextElementSibling;
            body.appendChild(ptr);
            ptr = next;
          }}

          var count = body.querySelectorAll('ul > li').length;
          issueTotal += count;
          repoCount += 1;
          var extra = count ? (' · ' + count + ' issue' + (count === 1 ? '' : 's')) : '';
          meta.textContent = (stars ? ('⭐ ' + stars) : '') + extra;

          details.id = 'repo-' + slugify(repoName);
        }});

        var status = document.getElementById('toolbar-status');
        if (status) {{
          status.textContent = 'Loaded ' + repoCount + ' repositories · ' + issueTotal + ' issues';
        }}
      }});
    }})();
    </script>
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
