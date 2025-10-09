#!/usr/bin/env python3
import argparse, sys, re, io, pathlib

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--readme", default="README.md")
    ap.add_argument("--input", required=True, help="Markdown file to insert")
    ap.add_argument("--section-start", default="<!--START_GOOD_FIRST_ISSUES-->")
    ap.add_argument("--section-end", default="<!--END_GOOD_FIRST_ISSUES-->")
    args = ap.parse_args()

    readme_p = pathlib.Path(args.readme)
    content = readme_p.read_text(encoding="utf-8") if readme_p.exists() else ""
    block = pathlib.Path(args.input).read_text(encoding="utf-8")

    start_tag, end_tag = args.section_start, args.section_end
    pattern = re.compile(re.escape(start_tag) + r".*?" + re.escape(end_tag), re.DOTALL)
    replacement = start_tag + "\n" + block + "\n" + end_tag

    if pattern.search(content):
        newc = pattern.sub(replacement, content)
    else:
        # append if not found
        if content and not content.endswith("\n"):
            content += "\n"
        newc = content + "\n" + replacement + "\n"
    if newc != content:
        readme_p.write_text(newc, encoding="utf-8")
        print("README updated.")
    else:
        print("No changes.")
if __name__ == "__main__":
    main()
