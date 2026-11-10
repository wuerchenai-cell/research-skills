"""Extract condition keywords from extracted text.

Usage: python extract_conditions.py <file>

Returns lines containing condition-bearing tokens such as N, K, L,
SNR, dB, GHz, RF chain, array type, and bandwidth.
This is an index, not a semantic interpretation.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PATTERNS = [
    r"\bN\s*=", r"\bK\s*=", r"\bL\s*=", r"\bM\s*=",
    r"\bSNR\b", r"\bdB\b", r"\bGHz\b", r"\bMHz\b", r"\bKHz\b", r"\bHz\b",
    r"RF chain", r"analog.digital", r"hybrid", r"sub-connected",
    r"switch", r"fully.digital", r"bandwidth", r"Cram.rao",
]


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) < 2:
        print("Usage: python extract_conditions.py <file>", file=sys.stderr)
        sys.exit(1)
    path = Path(sys.argv[1])
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"[ERROR] Could not read file: {e}", file=sys.stderr)
        sys.exit(1)
    lines = text.splitlines()
    found = 0
    for i, line in enumerate(lines, 1):
        if any(re.search(p, line, re.IGNORECASE) for p in PATTERNS):
            print(f"[line {i}] {line.strip()[:200]}")
            found += 1
    if found == 0:
        print("[No condition keywords found]")


if __name__ == "__main__":
    main()
