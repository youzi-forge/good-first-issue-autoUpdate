#!/usr/bin/env python3
import argparse
import datetime as dt
import pathlib
import re
import sys


def main() -> int:
    ap = argparse.ArgumentParser(description="Update a timestamp placeholder in README.")
    ap.add_argument("--readme", default="README.md")
    ap.add_argument("--start", default="<!--LAST_UPDATED-->")
    ap.add_argument("--end", default="<!--/LAST_UPDATED-->")
    ap.add_argument("--format", default="%Y-%m-%d %H:%M UTC", help="strftime format for UTC time")
    args = ap.parse_args()

    p = pathlib.Path(args.readme)
    if not p.exists():
        print(f"ERROR: README not found: {p}", file=sys.stderr)
        return 2
    text = p.read_text(encoding="utf-8")

    ts = dt.datetime.now(dt.timezone.utc).strftime(args.format)
    pattern = re.compile(re.escape(args.start) + r".*?" + re.escape(args.end), re.DOTALL)
    replacement = args.start + ts + args.end
    if not pattern.search(text):
        print("WARNING: markers not found; no changes made", file=sys.stderr)
        return 0
    new_text = pattern.sub(replacement, text, count=1)
    if new_text != text:
        p.write_text(new_text, encoding="utf-8")
        print(f"Updated timestamp in {p}")
    else:
        print("No changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

