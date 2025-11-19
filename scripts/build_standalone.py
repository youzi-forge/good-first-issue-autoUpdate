#!/usr/bin/env python3
"""
Generate a standalone single-file HTML from the built React app.
Inlines all CSS and JS, and injects the data.json content.
"""
import argparse
import json
import re
from pathlib import Path


def inline_assets(html_content: str, dist_dir: Path, base_path: str = "/") -> str:
    """
    Replace external CSS and JS references with inline content.
    Also handles the base path for GitHub Pages deployment.
    """
    # Find all CSS links
    css_pattern = r'<link rel="stylesheet"[^>]*href="([^"]+)"[^>]*>'
    css_matches = re.findall(css_pattern, html_content)
    
    for css_href in css_matches:
        # Remove base path if present
        css_file = css_href.replace(base_path, "", 1).lstrip("/")
        css_path = dist_dir / css_file
        
        if css_path.exists():
            css_content = css_path.read_text(encoding="utf-8")
            # Replace the link tag with inline style
            html_content = re.sub(
                r'<link rel="stylesheet"[^>]*href="' + re.escape(css_href) + r'"[^>]*>',
                f'<style>{css_content}</style>',
                html_content
            )
    
    # Find all JS scripts
    js_pattern = r'<script[^>]*src="([^"]+)"[^>]*></script>'
    js_matches = re.findall(js_pattern, html_content)
    
    for js_src in js_matches:
        # Remove base path if present
        js_file = js_src.replace(base_path, "", 1).lstrip("/")
        js_path = dist_dir / js_file
        
        if js_path.exists():
            js_content = js_path.read_text(encoding="utf-8")
            # Replace the script tag with inline script
            # Use a function to avoid regex escape issues
            pattern = r'<script[^>]*src="' + re.escape(js_src) + r'"[^>]*></script>'
            replacement = f'<script>{js_content}</script>'
            html_content = re.sub(pattern, lambda m: replacement, html_content)
    
    return html_content


def inject_data(html_content: str, data_json_path: Path) -> str:
    """
    Inject the data.json content into the HTML as window.__DATA__.
    """
    if not data_json_path.exists():
        print(f"Warning: {data_json_path} not found, using empty data")
        data = {"meta": {}, "issues": []}
    else:
        with open(data_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    
    # Inject data before the main script
    data_script = f'<script>window.__DATA__={json.dumps(data)};</script>'
    
    # Insert before closing </body>
    html_content = html_content.replace('</body>', f'{data_script}\n</body>')
    
    return html_content


def fix_favicon(html_content: str, dist_dir: Path, base_path: str = "/") -> str:
    """
    Inline the favicon as a data URI.
    """
    favicon_pattern = r'<link rel="icon"[^>]*href="([^"]+)"[^>]*>'
    favicon_match = re.search(favicon_pattern, html_content)
    
    if favicon_match:
        favicon_href = favicon_match.group(1)
        favicon_file = favicon_href.replace(base_path, "", 1).lstrip("/")
        favicon_path = dist_dir / favicon_file
        
        if favicon_path.exists():
            favicon_content = favicon_path.read_text(encoding="utf-8")
            # Convert SVG to data URI
            data_uri = f'data:image/svg+xml,{favicon_content.replace("#", "%23")}'
            html_content = re.sub(
                r'<link rel="icon"[^>]*href="' + re.escape(favicon_href) + r'"[^>]*>',
                f'<link rel="icon" type="image/svg+xml" href="{data_uri}">',
                html_content
            )
    
    return html_content


def modify_app_to_use_injected_data(html_content: str) -> str:
    """
    Modify the React app code to fetch data from window.__DATA__ instead of fetch().
    """
    # This is a simple replacement that works with our specific build
    # We replace the fetch("data.json") call with Promise.resolve(window.__DATA__)
    
    # Pattern to match: fetch("data.json") or fetch('data.json')
    html_content = html_content.replace(
        'fetch("data.json")',
        'Promise.resolve({json:()=>Promise.resolve(window.__DATA__)})'
    )
    html_content = html_content.replace(
        "fetch('data.json')",
        'Promise.resolve({json:()=>Promise.resolve(window.__DATA__)})'
    )
    
    return html_content


def main():
    parser = argparse.ArgumentParser(
        description="Generate standalone HTML from React build"
    )
    parser.add_argument(
        "--dist",
        type=Path,
        default=Path(__file__).parent.parent / "frontend" / "dist",
        help="Path to frontend dist directory",
    )
    parser.add_argument(
        "--data",
        type=Path,
        help="Path to data.json file to inject",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent.parent / "_site" / "index.html",
        help="Output HTML file path",
    )
    parser.add_argument(
        "--base-path",
        type=str,
        default="/good-first-issue-autoUpdate/",
        help="Base path used in the build (for removing from asset paths)",
    )
    
    args = parser.parse_args()
    
    # Read the original HTML
    index_html = args.dist / "index.html"
    if not index_html.exists():
        print(f"Error: {index_html} not found. Run 'npm run build' first.")
        return 1
    
    html_content = index_html.read_text(encoding="utf-8")
    
    # Process the HTML
    print("Inlining CSS and JS assets...")
    html_content = inline_assets(html_content, args.dist, args.base_path)
    
    print("Fixing favicon...")
    html_content = fix_favicon(html_content, args.dist, args.base_path)
    
    print("Modifying app to use injected data...")
    html_content = modify_app_to_use_injected_data(html_content)
    
    if args.data:
        print(f"Injecting data from {args.data}...")
        html_content = inject_data(html_content, args.data)
    else:
        print("No data file specified, using empty data")
        html_content = inject_data(html_content, Path("nonexistent.json"))
    
    # Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html_content, encoding="utf-8")
    
    print(f"✓ Standalone HTML generated: {args.output}")
    print(f"  File size: {args.output.stat().st_size / 1024:.1f} KB")
    
    return 0


if __name__ == "__main__":
    exit(main())
