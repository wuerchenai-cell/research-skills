"""Check a parameter spec: value, unit, tolerance, and range.

All numeric inputs (value, min, max) must be finite numbers: NaN and
+/-Infinity are rejected with a non-zero exit code. Negative values are
allowed by default because quantities such as dBm or temperature can be
negative; pass --positive when the quantity must be strictly positive
(e.g. frequency).

Usage:
  python verify_params.py --name "operating frequency" --value 24 --unit GHz --min 0 --max 100 --tol 10%
  python verify_params.py --name frequency --value 24 --unit GHz --positive
"""
from __future__ import annotations

import argparse
import math
import re
import sys

KNOWN_UNITS = {
    "GHz", "MHz", "KHz", "Hz", "mm", "cm", "m", "km",
    "dB", "dBm", "W", "mW", "V", "mV", "A", "mA",
}


def _finite(label: str, raw: str) -> float:
    """Parse a numeric argument, rejecting non-numeric and non-finite input."""
    try:
        number = float(raw)
    except ValueError:
        print(f"[ERROR] {label} is not numeric: {raw}")
        sys.exit(1)
    if not math.isfinite(number):
        print(f"[ERROR] {label} must be a finite number (got {raw})")
        sys.exit(1)
    return number


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--value", required=True)
    parser.add_argument("--unit", required=True)
    parser.add_argument("--min")
    parser.add_argument("--max")
    parser.add_argument("--tol")
    parser.add_argument("--positive", action="store_true",
                        help="require value > 0 (for quantities that cannot be negative)")
    args = parser.parse_args()

    issues: list[str] = []
    value = _finite("value", args.value)
    low = _finite("min", args.min) if args.min is not None else None
    high = _finite("max", args.max) if args.max is not None else None

    if args.unit not in KNOWN_UNITS:
        issues.append(f"unit not in known set: {args.unit}")

    if args.positive and value <= 0:
        issues.append(f"value must be positive (got {value})")

    if low is not None and value < low:
        issues.append(f"value {value} below min {low}")
    if high is not None and value > high:
        issues.append(f"value {value} above max {high}")
    if low is not None and high is not None and low > high:
        issues.append(f"min {low} is greater than max {high}")

    if args.tol:
        if not re.match(r"^\d+(\.\d+)?%?$", args.tol):
            issues.append(f"tolerance format looks invalid: {args.tol}")

    if issues:
        for issue in issues:
            print(f"[WARN] {issue}")
        sys.exit(1)
    print(f"[OK] {args.name} = {args.value} {args.unit} (checks passed)")


if __name__ == "__main__":
    main()
