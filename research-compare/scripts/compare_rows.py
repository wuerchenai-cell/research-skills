"""Validate a condition-aware comparison table from CSV or JSON.

Usage:
  python compare_rows.py --input rows.csv
  python compare_rows.py --input rows.json

Required fields per row:
  source, question, method, conditions, cost, conclusion
The script checks required fields and whether numeric claims carry
conditions (SNR, N, K, L, dB, GHz, etc.).
"""
from __future__ import annotations

import argparse
import json
import csv
import re
import sys

REQUIRED = ["source", "question", "method", "conditions", "cost", "conclusion"]
CONDITION_PATTERN = re.compile(
    r"(N\s*=|K\s*=|L\s*=|SNR|dB|GHz|MHz|KHz|Hz|W\s*=|M\s*=|RF\s*chain|array|SNR\s*=)",
    re.IGNORECASE,
)


def load_rows(path: str) -> list[dict]:
    if path.endswith(".json"):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def validate(rows: list[dict]) -> list[str]:
    issues: list[str] = []
    for idx, row in enumerate(rows, 1):
        for field in REQUIRED:
            if field not in row or not str(row[field]).strip():
                issues.append(f"row {idx}: missing or empty '{field}'")
        conclusion = str(row.get("conclusion", ""))
        numeric_claim = bool(re.search(r"\d", conclusion))
        conditions = str(row.get("conditions", ""))
        if numeric_claim and not CONDITION_PATTERN.search(conditions):
            issues.append(
                f"row {idx}: numeric conclusion but no conditions recorded"
            )
    return issues


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    rows = load_rows(args.input)
    issues = validate(rows)
    if issues:
        for issue in issues:
            print(f"[WARN] {issue}")
        sys.exit(1)
    print(f"[OK] {len(rows)} rows validated; required fields present")


if __name__ == "__main__":
    main()
