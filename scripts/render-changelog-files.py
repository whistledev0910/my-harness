#!/usr/bin/env python3
"""Render a bounded Markdown summary from GitHub pull-request file JSON."""

from __future__ import annotations

import argparse
import json
import sys


def safe_markdown_path(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("\r", "\\r")
        .replace("\n", "\\n")
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be positive")

    document = json.load(sys.stdin)
    pages = document if document and isinstance(document[0], list) else [document]
    files = [item["filename"] for page in pages for item in page]
    total = len(files)
    shown = min(total, args.limit)
    if total > shown:
        print(f"- Changed files: {total} total (first {shown} shown)")
    else:
        print(f"- Changed files: {total} total")
    for path in files[:shown]:
        print(f"  - `{safe_markdown_path(path)}`")
    omitted = total - shown
    if omitted:
        print(f"  - _… {omitted} additional file(s) omitted from this entry._")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
