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
      /* Scoped link styles */
      .content a {{
        color: var(--accent);
        text-decoration: none;
      }}
      .content a:hover {{
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
        margin-top: 6px;
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
      .pagination-bar {{
        margin-top: 16px;
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        align-items: center;
        justify-content: space-between;
      }}
      .pagination-left,
      .pagination-right,
      .pagination-center {{
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
      }}
      .pagination-button {{
        border: 1px solid var(--border);
        background: var(--card);
        color: var(--fg);
        border-radius: 10px;
        padding: 8px 14px;
        font-size: 0.9rem;
        cursor: pointer;
        transition: background 0.2s ease, border-color 0.2s ease;
      }}
      .pagination-button:hover:not(:disabled) {{
        background: rgba(9, 105, 218, 0.08);
        border-color: var(--accent);
      }}
      .pagination-button:disabled {{
        opacity: 0.4;
        cursor: not-allowed;
      }}
      .pagination-input {{
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.9rem;
      }}
      .pagination-input input {{
        width: 70px;
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 6px 8px;
        background: var(--card);
        color: var(--fg);
      }}
      .pagination-input input:focus {{
        outline: 2px solid var(--accent);
        outline-offset: 2px;
      }}
      .pagination-size label {{
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: var(--muted);
      }}
      .pagination-size select {{
        border: 1px solid var(--border);
        background: var(--card);
        color: var(--fg);
        border-radius: 10px;
        padding: 8px 10px;
        font-size: 0.95rem;
      }}
      .pagination-size select:focus {{
        outline: 2px solid var(--accent);
        outline-offset: 2px;
      }}
      .page-counts {{
        margin-top: 6px;
        font-size: 0.9rem;
        color: var(--muted);
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
        gap: 16px;
      }}
      .repo-title-row {{
        display: flex;
        align-items: center;
        gap: 10px;
        flex: 1 1 auto;
        min-width: 0;
      }}
      .repo-right {{
        display: flex;
        align-items: center;
        gap: 12px;
        flex-shrink: 0;
        color: var(--muted);
      }}
      .repo-summary h3 {{
        margin: 0;
        font-size: 1.2rem;
        flex: 0 0 auto;
      }}
      .repo-summary h3 a {{
        color: var(--accent);
        text-decoration: none;
      }}
      .repo-summary h3 a:hover {{
        text-decoration: underline;
      }}
      .repo-right, .repo-right * {{
        color: var(--muted) !important;
      }}
      .repo-meta {{
        font-size: 0.95rem;
        color: var(--muted) !important;
        white-space: nowrap;
      }}
      .repo-stars {{
        font-size: 1.05rem;
        font-weight: 600;
        color: var(--fg);
        white-space: nowrap;
      }}
      .repo-body {{
        padding: 0 20px 20px 20px;
      }}
      .repo-card {{
        scroll-margin-top: 96px; /* account for sticky toolbar */
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
        .pagination-bar {{
          flex-direction: column;
          align-items: stretch;
        }}
        .pagination-left,
        .pagination-right,
        .pagination-center {{
          width: 100%;
          justify-content: space-between;
        }}
        .content li {{
          padding: 10px 12px;
        }}
      }}

      /* Copy link button */
      .copy-link {{
        border: 1px solid var(--border);
        background: var(--card);
        color: var(--muted);
        border-radius: 8px;
        padding: 4px 8px;
        font-size: 0.85rem;
        cursor: pointer;
      }}
      .copy-link:hover {{
        color: var(--accent);
        border-color: var(--accent);
      }}

      /* Back to top */
      .back-to-top {{
        position: fixed;
        right: 20px;
        bottom: 24px;
        display: none;
        border: 1px solid var(--border);
        background: var(--card);
        color: var(--fg);
        border-radius: 999px;
        padding: 10px 14px;
        box-shadow: var(--shadow);
        cursor: pointer;
      }}
      .back-to-top:focus {{ outline: 2px solid var(--accent); outline-offset: 2px; }}

      /* Inline copied state for copy-link */
      .copy-link.copied {{
        color: var(--accent);
        border-color: var(--accent);
      }}
    </style>
  </head>
  <body>
    <div class="wrap">
      <header class="page-header" aria-label="Project overview">
        <div class="hero">
          <h1 id="hero-title">{title}</h1>
          <div class="meta" id="hero-meta"></div>
        </div>
      <section class="toolbar" aria-label="Issue controls">
          <div class="toolbar-grid">
            <div class="toolbar-field">
              <label for="repo-search-input">Repositories</label>
              <input id="repo-search-input" type="search" placeholder="Search repositories">
            </div>
            <div class="toolbar-field">
              <label for="issue-search-input">Issues</label>
              <input id="issue-search-input" type="search" placeholder="Search issues">
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
          <div class="pagination-bar" data-pagination="controls" data-location="top" aria-label="Pagination controls">
            <div class="pagination-left">
              <button type="button" class="pagination-button" data-action="prev" aria-label="Previous page">← Prev</button>
              <button type="button" class="pagination-button" data-action="next" aria-label="Next page">Next →</button>
            </div>
            <div class="pagination-center">
              <div class="pagination-input">
                <label class="sr-only" for="page-input-top">Go to page</label>
                <input id="page-input-top" class="pagination-page-input" type="number" min="1" value="1" aria-label="Current page">
                <span class="pagination-display">/ 1</span>
              </div>
            </div>
            <div class="pagination-right pagination-size">
              <label class="pagination-size-label" for="page-size-top">Per page</label>
              <select id="page-size-top" class="pagination-size-select" aria-label="Repositories per page">
                <option value="50" selected>50</option>
                <option value="80">80</option>
                <option value="100">100</option>
                <option value="150">150</option>
                <option value="200">200</option>
              </select>
            </div>
          </div>
          <div class="page-counts" data-pagination="counts"></div>
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
        <div class="pagination-bar" data-pagination="controls" data-location="bottom" aria-label="Pagination controls">
          <div class="pagination-left">
            <button type="button" class="pagination-button" data-action="prev" aria-label="Previous page">← Prev</button>
            <button type="button" class="pagination-button" data-action="next" aria-label="Next page">Next →</button>
          </div>
          <div class="pagination-center">
            <div class="pagination-input">
              <label class="sr-only" for="page-input-bottom">Go to page</label>
              <input id="page-input-bottom" class="pagination-page-input" type="number" min="1" value="1" aria-label="Current page">
              <span class="pagination-display">/ 1</span>
            </div>
          </div>
          <div class="pagination-right pagination-size">
            <label class="pagination-size-label" for="page-size-bottom">Per page</label>
            <select id="page-size-bottom" class="pagination-size-select" aria-label="Repositories per page">
              <option value="50" selected>50</option>
              <option value="80">80</option>
              <option value="100">100</option>
              <option value="150">150</option>
              <option value="200">200</option>
            </select>
          </div>
        </div>
        <div class="page-counts" data-pagination="counts"></div>
      </main>

      <button id="back-to-top" class="back-to-top" type="button" aria-label="Back to top">↑ Top</button>

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

      function formatTimestampDisplay(raw) {{
        if (!raw) return '';
        var cleaned = raw.trim();
        var match = cleaned.match(/^(\d{{4}}-\d{{2}}-\d{{2}})[T ](\d{{2}}:\d{{2}})(?::\d{{2}})?Z$/i);
        if (match) {{
          return match[1] + ' ' + match[2] + ' UTC';
        }}
        return cleaned.replace('T', ' ');
      }}

      var paginationState = {{
        cards: [],
        filteredCards: [],
        currentPage: 1,
        pageSize: 50,
        totalPages: 1,
        totalIssuesVisible: 0,
        totalIssuesAll: 0,
        currentPageRepoCount: 0,
        currentPageIssueCount: 0,
        currentPageCards: []
      }};

      var paginationControls = {{
        prevButtons: [],
        nextButtons: [],
        pageInputs: [],
        pageDisplays: [],
        pageSizeSelects: [],
        countLabels: []
      }};

      function cachePaginationControls() {{
        paginationControls.prevButtons = Array.prototype.slice.call(document.querySelectorAll('.pagination-button[data-action="prev"]'));
        paginationControls.nextButtons = Array.prototype.slice.call(document.querySelectorAll('.pagination-button[data-action="next"]'));
        paginationControls.pageInputs = Array.prototype.slice.call(document.querySelectorAll('.pagination-page-input'));
        paginationControls.pageDisplays = Array.prototype.slice.call(document.querySelectorAll('.pagination-display'));
        paginationControls.pageSizeSelects = Array.prototype.slice.call(document.querySelectorAll('.pagination-size-select'));
        paginationControls.countLabels = Array.prototype.slice.call(document.querySelectorAll('.page-counts[data-pagination="counts"]'));
      }}


      onReady(function initRepoCards() {{
        var content = document.getElementById('issue-content');
        if (!content) return;

        // Move first heading and generated timestamp paragraph into hero
        (function () {{
          var heroTitle = document.getElementById('hero-title');
          var heroMeta = document.getElementById('hero-meta');
          var firstH1 = content.querySelector('h1');
          if (firstH1 && heroTitle) {{
            heroTitle.innerHTML = firstH1.innerHTML;
            firstH1.remove();
          }}
          var firstPara = content.querySelector('p');
          if (firstPara && heroMeta) {{
            var metaText = firstPara.textContent || '';
            metaText = metaText.replace(/^Generated at:\s*/i, '').trim();
            var formatted = formatTimestampDisplay(metaText);
            heroMeta.textContent = formatted ? ('Generated at: ' + formatted) : '';
            firstPara.remove();
          }}
        }})();

        // Find top-level H2s (repositories)
        var h2s = Array.prototype.filter.call(content.children, function (el) {{ return el.tagName === 'H2'; }});
        if (!h2s.length) {{
          var status = document.getElementById('toolbar-status');
          if (status) status.textContent = 'Enhanced features unavailable (Markdown not parsed). Showing plain content.';
          return; // e.g., no markdown conversion or empty dataset
        }}

        var desktop = window.matchMedia('(min-width: 900px)').matches;
        var repoCount = 0;
        var issueTotal = 0;

        h2s.forEach(function (h2) {{
          var raw = (h2.textContent || '').trim();
          var starIdx = raw.indexOf('⭐');
          var repoName = raw;
          var stars = null;
          if (starIdx !== -1) {{
            repoName = raw.slice(0, starIdx).trim();
            var starPart = raw.slice(starIdx + 1).replace(/[^0-9]/g, ' ').trim();
            var parsed = parseInt(starPart.split(/\s+/)[0] || '', 10);
            if (!Number.isNaN(parsed)) stars = parsed;
          }}

          var details = document.createElement('details');
          details.className = 'repo-card';
          if (desktop) details.setAttribute('open', '');

          var summary = document.createElement('summary');
          summary.className = 'repo-summary';

          var titleRow = document.createElement('div');
          titleRow.className = 'repo-title-row';

          var h3 = document.createElement('h3');
          h3.textContent = repoName;

          var meta = document.createElement('div');
          meta.className = 'repo-meta';
          meta.textContent = '';

          var right = document.createElement('div');
          right.className = 'repo-right';

          var anchorBtn = document.createElement('button');
          anchorBtn.type = 'button';
          anchorBtn.className = 'copy-link';
          anchorBtn.title = 'Copy link';
          anchorBtn.setAttribute('aria-label', 'Copy link to ' + repoName);
          anchorBtn.textContent = '🔗';

          right.appendChild(meta);
          right.appendChild(anchorBtn);

          titleRow.appendChild(h3);
          if (stars) {{
            var starSpan = document.createElement('span');
            starSpan.className = 'repo-stars';
            starSpan.textContent = '⭐ ' + stars.toLocaleString();
            titleRow.appendChild(starSpan);
          }}

          summary.appendChild(titleRow);
          summary.appendChild(right);

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

          // Try to locate the repository link paragraph and convert title to a clickable link
          try {{
            var repoLinkEl = body.querySelector('p > a[href^="http"]');
            var repoUrl = repoLinkEl ? String(repoLinkEl.getAttribute('href') || '') : '';
            if (repoUrl) {{
              // Remove the separate repository paragraph to keep the card compact
              var repoP = repoLinkEl.closest('p');
              if (repoP) repoP.remove();
              // Turn the repo name in summary into a link
              h3.textContent = '';
              var h3a = document.createElement('a');
              h3a.href = repoUrl;
              h3a.textContent = repoName;
              h3a.target = '_blank';
              h3a.rel = 'noopener noreferrer';
              // Prevent toggling the <details> when clicking the link
              h3a.addEventListener('click', function (ev) {{ ev.stopPropagation(); }});
              h3.appendChild(h3a);
            }}
          }} catch (e) {{ /* ignore */ }}

          var count = body.querySelectorAll('ul > li').length;
          issueTotal += count;
          repoCount += 1;
          meta.textContent = count + ' ' + (count === 1 ? 'issue' : 'issues');

          details.id = 'repo-' + slugify(repoName);
          if (stars !== null && !Number.isNaN(stars)) {{
            details.dataset.stars = String(stars);
          }}
          details.dataset.filteredOut = '0';
          details.dataset.totalIssues = String(count);
          details.dataset.visibleIssues = String(count);

          // Copy anchor link handler with inline feedback
          var copyTimer = null;
          var originalText = anchorBtn.textContent;
          anchorBtn.addEventListener('click', function (ev) {{
            ev.stopPropagation();
            try {{
              var url = location.origin + location.pathname + '#' + details.id;
              if (navigator.clipboard && navigator.clipboard.writeText) {{
                navigator.clipboard.writeText(url);
              }} else {{
                var ta = document.createElement('textarea');
                ta.value = url;
                document.body.appendChild(ta);
                ta.select();
                document.execCommand('copy');
                document.body.removeChild(ta);
              }}
              anchorBtn.textContent = 'Copied ✓';
              anchorBtn.classList.add('copied');
              anchorBtn.title = 'Copied';
              anchorBtn.setAttribute('aria-label', 'Link copied for ' + repoName);
              clearTimeout(copyTimer);
              copyTimer = setTimeout(function () {{
                anchorBtn.textContent = originalText;
                anchorBtn.classList.remove('copied');
                anchorBtn.title = 'Copy link';
                anchorBtn.setAttribute('aria-label', 'Copy link to ' + repoName);
              }}, 1200);
            }} catch (e) {{ /* ignore */ }}
          }});
        }});

        // After grouping, render label badges inside each issue item
        renderLabelBadges(content);

        paginationState.cards = Array.prototype.slice.call(document.querySelectorAll('.repo-card'));

        // Cache totals on each repo card for faster updates
        document.querySelectorAll('.repo-card').forEach(function (card) {{
          var total = card.querySelectorAll('.repo-body li').length;
          card.dataset.total = String(total);
          if (!card.dataset.stars) {{
            card.dataset.stars = '';
          }}
        }});

        // Wire toolbar controls and perform initial filter (no-op but updates counters)
        wireControls();
        filterAndUpdate({{ resetPage: true, scroll: false }});
      }});
      
      function renderLabelBadges(root) {{
        var dark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        function colorForLabel(name) {{
          var h = 0;
          for (var i = 0; i < name.length; i++) {{
            h = (h * 31 + name.charCodeAt(i)) | 0;
          }}
          h = Math.abs(h) % 360;
          var bgL = dark ? 22 : 94;
          var borderL = dark ? 32 : 80;
          var bg = 'hsl(' + h + ', 70%,' + bgL + '%)';
          var bd = 'hsl(' + h + ', 55%,' + borderL + '%)';
          return {{ bg: bg, bd: bd }};
        }}

        var items = root.querySelectorAll('ul > li');
        items.forEach(function (li) {{
          var html = li.innerHTML;
          var m = html.match(/labels:\s*([^<\n\r]+)/i);
          if (!m) return;
          var labelsStr = m[1].trim();
          // Remove the original labels text (optionally preceded by a <br>)
          li.innerHTML = html.replace(/(?:<br\s*\/?>)?\s*labels:\s*([^<\n\r]+)/i, '').trim();

          var labels = labelsStr.split(',').map(function (s) {{ return s.trim(); }}).filter(Boolean);
          if (!labels.length) return;

          // data attribute for future filtering
          li.setAttribute('data-labels', labels.map(function (s) {{ return s.toLowerCase(); }}).join('|'));

          var row = document.createElement('div');
          row.className = 'label-badges';
          labels.forEach(function (name) {{
            var span = document.createElement('span');
            span.className = 'label-badge';
            span.setAttribute('data-label', name.toLowerCase());
            var col = colorForLabel(name.toLowerCase());
            span.style.backgroundColor = col.bg;
            span.style.borderColor = col.bd;
            span.textContent = name;
            row.appendChild(span);
          }});
          li.appendChild(row);
        }});
      }}

      function debounce(fn, delay) {{
        var t = null;
        return function () {{
          var ctx = this, args = arguments;
          clearTimeout(t);
          t = setTimeout(function () {{ fn.apply(ctx, args); }}, delay);
        }};
      }}

      function parseLabelFilters(raw) {{
        return (raw || '')
          .toLowerCase()
          .split(/[\s,]+/)
          .map(function (s) {{ return s.trim(); }})
          .filter(Boolean);
      }}

      function updateStatus() {{
        var status = document.getElementById('toolbar-status');
        if (!status) return;
        if (!paginationState.filteredCards.length) {{
          status.textContent = 'No repositories match the current filters.';
          return;
        }}
        var totalRepos = paginationState.filteredCards.length;
        var totalIssues = paginationState.totalIssuesVisible;
        status.textContent = 'Total: ' + totalRepos + ' repos · ' + totalIssues + ' issues (page ' + paginationState.currentPage + '/' + paginationState.totalPages + ')';
      }}

      function filterAndUpdate(opts) {{
        opts = opts || {{}};
        var repoTerm = (document.getElementById('repo-search-input') || {{ value: '' }}).value.toLowerCase().trim();
        var issueTerm = (document.getElementById('issue-search-input') || {{ value: '' }}).value.toLowerCase().trim();
        var labelRaw = (document.getElementById('label-input') || {{ value: '' }}).value;
        var labelFilters = parseLabelFilters(labelRaw);
        var hasFilter = !!repoTerm || !!issueTerm || labelFilters.length > 0;

        var matchedCards = [];
        var totalVisibleIssues = 0;
        var totalIssuesAll = 0;

        paginationState.cards.forEach(function (card) {{
          var issues = card.querySelectorAll('.repo-body li');
          var total = issues.length;
          var visible = 0;
          var nameEl = card.querySelector('.repo-summary h3');
          var repoText = (nameEl ? nameEl.textContent : '').toLowerCase();
          var repoMatches = !repoTerm || repoText.indexOf(repoTerm) !== -1;

          issues.forEach(function (li) {{
            var text = (li.textContent || '').toLowerCase();
            var issueMatches = !issueTerm || text.indexOf(issueTerm) !== -1;
            var labelsStr = li.getAttribute('data-labels') || '';
            var labels = labelsStr ? labelsStr.split('|') : [];
            var matchesLabels = labelFilters.length === 0 || labelFilters.some(function (f) {{ return labels.indexOf(f) !== -1; }});
            var show = repoMatches && issueMatches && matchesLabels;
            li.style.display = show ? '' : 'none';
            li.setAttribute('data-hidden', show ? '0' : '1');
            if (show) visible += 1;
          }});

          card.dataset.totalIssues = String(total);
          card.dataset.visibleIssues = String(visible);

          var meta = card.querySelector('.repo-meta');
          if (meta) {{
            var text = visible + (hasFilter ? (' of ' + total) : '') + ' ' + (visible === 1 ? 'issue' : 'issues');
            meta.textContent = text;
          }}

          if (repoMatches && visible > 0) {{
            card.dataset.filteredOut = '0';
            matchedCards.push(card);
            totalVisibleIssues += visible;
            totalIssuesAll += total;
            if (hasFilter) {{
              card.open = true;
            }}
          }} else {{
            card.dataset.filteredOut = '1';
            card.style.display = 'none';
          }}
        }});

        paginationState.filteredCards = matchedCards;
        paginationState.totalIssuesVisible = totalVisibleIssues;
        paginationState.totalIssuesAll = totalIssuesAll;

        if (opts.resetPage !== false) {{
          paginationState.currentPage = 1;
        }}

        paginationState.totalPages = Math.max(1, Math.ceil((paginationState.filteredCards.length || 1) / paginationState.pageSize));
        paginationState.currentPage = Math.min(Math.max(paginationState.currentPage, 1), paginationState.totalPages);

        gotoPage(paginationState.currentPage, {{ scroll: opts.scroll !== false }});
      }}

      function gotoPage(page, opts) {{
        opts = opts || {{}};
        var filtered = paginationState.filteredCards;
        if (!filtered.length) {{
          paginationState.totalPages = 1;
          paginationState.currentPage = 1;
          paginationState.currentPageCards = [];
          paginationState.currentPageRepoCount = 0;
          paginationState.currentPageIssueCount = 0;
          paginationState.cards.forEach(function (card) {{ card.style.display = 'none'; }});
          updatePaginator();
          updateStatus();
          return;
        }}

        paginationState.totalPages = Math.max(1, Math.ceil(filtered.length / paginationState.pageSize));
        var target = Math.min(Math.max(page, 1), paginationState.totalPages);
        paginationState.currentPage = target;

        renderPage();
        updatePaginator();
        updateStatus();

        if (opts.scroll !== false) {{
          window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}
      }}

      function renderPage() {{
        var filtered = paginationState.filteredCards;
        var start = (paginationState.currentPage - 1) * paginationState.pageSize;
        var end = Math.min(filtered.length, start + paginationState.pageSize);
        var pageCards = [];
        var filteredSet = new Set(filtered);

        for (var i = 0; i < filtered.length; i++) {{
          var card = filtered[i];
          if (i >= start && i < end) {{
            card.style.display = '';
            pageCards.push(card);
          }} else {{
            card.style.display = 'none';
          }}
        }}

        paginationState.cards.forEach(function (card) {{
          if (!filteredSet.has(card)) {{
            card.style.display = 'none';
          }}
        }});

        var pageIssues = 0;
        pageCards.forEach(function (card) {{
          pageIssues += parseInt(card.dataset.visibleIssues || '0', 10);
          if (card.dataset.filteredOut === '0') {{
            card.open = true;
          }}
        }});

        paginationState.currentPageCards = pageCards;
        paginationState.currentPageRepoCount = pageCards.length;
        paginationState.currentPageIssueCount = pageIssues;
      }}

      function updatePaginator() {{
        var hasResults = paginationState.filteredCards.length > 0;
        paginationControls.pageDisplays.forEach(function (span) {{
          span.textContent = '/ ' + paginationState.totalPages;
        }});
        paginationControls.pageInputs.forEach(function (input) {{
          input.max = paginationState.totalPages;
          input.min = paginationState.totalPages ? 1 : 0;
          input.disabled = paginationState.totalPages <= 1 || !hasResults;
          input.value = hasResults ? paginationState.currentPage : '';
        }});
        paginationControls.prevButtons.forEach(function (btn) {{
          btn.disabled = paginationState.currentPage <= 1 || !hasResults;
        }});
        paginationControls.nextButtons.forEach(function (btn) {{
          btn.disabled = paginationState.currentPage >= paginationState.totalPages || !hasResults;
        }});
        paginationControls.countLabels.forEach(function (label) {{
          if (!hasResults) {{
            label.textContent = 'No repositories matched your filters.';
          }} else {{
            label.textContent = paginationState.currentPageRepoCount + ' repos · ' + paginationState.currentPageIssueCount + ' issues this page · total ' + paginationState.filteredCards.length + ' repos / ' + paginationState.totalIssuesVisible + ' issues';
          }}
        }});
        paginationControls.pageSizeSelects.forEach(function (select) {{
          var desired = String(paginationState.pageSize);
          var hasOption = Array.prototype.some.call(select.options, function (opt) {{ return opt.value === desired; }});
          if (hasOption) {{
            select.value = desired;
          }}
        }});
      }}

      function wireControls() {{
        cachePaginationControls();
        var repoSearch = document.getElementById('repo-search-input');
        var issueSearch = document.getElementById('issue-search-input');
        var labels = document.getElementById('label-input');
        var onChange = debounce(function () {{ filterAndUpdate({{ resetPage: true }}); }}, 180);
        if (repoSearch) repoSearch.addEventListener('input', onChange);
        if (issueSearch) issueSearch.addEventListener('input', onChange);
        if (labels) labels.addEventListener('input', onChange);

        // Enter on repo search: jump to first visible repo
        if (repoSearch) repoSearch.addEventListener('keydown', function (ev) {{
          if (ev.key === 'Enter') {{ ev.preventDefault(); jumpToFirstVisible(); }}
        }});

        var expandAll = document.getElementById('expand-all');
        var collapseAll = document.getElementById('collapse-all');
        if (expandAll) expandAll.addEventListener('click', function () {{
          visibleCards().forEach(function (card) {{ card.open = true; }});
        }});
        if (collapseAll) collapseAll.addEventListener('click', function () {{
          visibleCards().forEach(function (card) {{ card.open = false; }});
        }});

        // n / Shift+n navigation between visible repos
        window.addEventListener('keydown', function (ev) {{
          var tag = (ev.target && ev.target.tagName || '').toLowerCase();
          if (tag === 'input' || tag === 'textarea' || tag === 'select' || (ev.target && ev.target.isContentEditable)) return;
          if (ev.key === 'n' && !ev.shiftKey) {{ ev.preventDefault(); jumpToNextVisible(); }}
          if ((ev.key === 'N' && !ev.shiftKey) || (ev.key.toLowerCase() === 'n' && ev.shiftKey)) {{ ev.preventDefault(); jumpToPrevVisible(); }}
          if (ev.key === ']') {{ ev.preventDefault(); gotoPage(paginationState.currentPage + 1); }}
          if (ev.key === '[') {{ ev.preventDefault(); gotoPage(paginationState.currentPage - 1); }}
        }});

        // Back-to-top button show/hide
        var topBtn = document.getElementById('back-to-top');
        if (topBtn) {{
          topBtn.addEventListener('click', function () {{ window.scrollTo({{ top: 0, behavior: 'smooth' }}); }});
          var onScroll = debounce(function () {{
            if (window.scrollY > 200) topBtn.style.display = 'inline-flex'; else topBtn.style.display = 'none';
          }}, 50);
          window.addEventListener('scroll', onScroll);
          onScroll();
        }}

        paginationControls.prevButtons.forEach(function (btn) {{
          btn.addEventListener('click', function () {{ gotoPage(paginationState.currentPage - 1); }});
        }});
        paginationControls.nextButtons.forEach(function (btn) {{
          btn.addEventListener('click', function () {{ gotoPage(paginationState.currentPage + 1); }});
        }});
        paginationControls.pageInputs.forEach(function (input) {{
          input.addEventListener('change', function () {{
            var val = parseInt(input.value, 10);
            if (Number.isNaN(val)) {{
              input.value = paginationState.filteredCards.length ? paginationState.currentPage : '';
              return;
            }}
            gotoPage(val);
          }});
          input.addEventListener('keydown', function (ev) {{
            if (ev.key === 'Enter') {{
              ev.preventDefault();
              var val = parseInt(input.value, 10);
              if (!Number.isNaN(val)) {{
                gotoPage(val);
              }}
            }}
          }});
        }});
        if (paginationControls.pageSizeSelects.length) {{
          var initial = parseInt(paginationControls.pageSizeSelects[0].value, 10);
          if (!Number.isNaN(initial) && initial > 0) {{
            paginationState.pageSize = initial;
          }}
          paginationControls.pageSizeSelects.forEach(function (select) {{
            select.addEventListener('change', function (ev) {{
              var val = parseInt(ev.target.value, 10);
              if (Number.isNaN(val) || val <= 0) {{
                val = paginationState.filteredCards.length || paginationState.pageSize || 50;
              }}
              paginationState.pageSize = val;
              paginationControls.pageSizeSelects.forEach(function (other) {{
                if (other !== ev.target) other.value = String(val);
              }});
              paginationState.currentPage = 1;
              gotoPage(paginationState.currentPage);
            }});
          }});
        }}
      }}

      function visibleCards() {{
        return paginationState.currentPageCards.slice();
      }}
      function jumpToCard(card) {{
        if (!card) return;
        card.open = true;
        card.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        card.focus && card.focus();
      }}
      function jumpToFirstVisible() {{
        var cards = visibleCards();
        if (!cards.length) return;
        jumpToCard(cards[0]);
      }}
      function jumpToNextVisible() {{
        var cards = visibleCards();
        if (!cards.length) return;
        for (var i = 0; i < cards.length; i++) {{
          if (cards[i].getBoundingClientRect().top > 5) {{
            jumpToCard(cards[i]);
            return;
          }}
        }}
        if (paginationState.currentPage < paginationState.totalPages) {{
          gotoPage(paginationState.currentPage + 1);
          setTimeout(function () {{
            var nextCards = visibleCards();
            if (nextCards.length) jumpToCard(nextCards[0]);
          }}, 160);
        }}
      }}
      function jumpToPrevVisible() {{
        var cards = visibleCards();
        if (!cards.length) return;
        for (var i = cards.length - 1; i >= 0; i--) {{
          if (cards[i].getBoundingClientRect().top < -5) {{
            jumpToCard(cards[i]);
            return;
          }}
        }}
        if (paginationState.currentPage > 1) {{
          gotoPage(paginationState.currentPage - 1);
          setTimeout(function () {{
            var prevCards = visibleCards();
            if (prevCards.length) jumpToCard(prevCards[prevCards.length - 1]);
          }}, 160);
        }} else {{
          jumpToCard(cards[0]);
        }}
      }}

      
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
