"""Locate key sections, formulas, and figures in extracted text.

Returns line numbers and surrounding context for matches.
This is a lightweight index, not a semantic analysis.
"""
from __future__ import annotations

import re
import sys


def locate(text: str, patterns: list[str], context_lines: int = 2) -> str:
    lines = text.splitlines()
    results: list[str] = []
    for pat in patterns:
        for i, line in enumerate(lines):
            if re.search(pat, line, re.IGNORECASE):
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                results.append(f"--- Pattern: {pat} (line {i + 1}) ---")
                results.append("\n".join(lines[start:end]))
    return "\n".join(results) if results else "[No matches found]"


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) < 3:
        print("Usage: python read_locate.py <file> <pattern1> [pattern2 ...]", file=sys.stderr)
        sys.exit(1)
    file_path = sys.argv[1]
    patterns = sys.argv[2:]
    try:
        from pathlib import Path
        text = Path(file_path).read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"[ERROR] Could not read file: {e}", file=sys.stderr)
        sys.exit(1)
    print(locate(text, patterns))
