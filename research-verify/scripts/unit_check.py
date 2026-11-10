"""Basic unit and dimension consistency check.

Usage:
  python unit_check.py --freq 24 --freq-unit GHz --wl 12.5 --wl-unit mm

Checks a frequency/wavelength pair using c = f * lambda within tolerance.
Both inputs must be finite positive numbers; zero, negative, NaN, and
Infinity inputs are rejected with a non-zero exit code.

This is a helper, not a full dimension system.
"""
from __future__ import annotations

import argparse
import math
import sys

C_M_PER_S = 299792458.0  # speed of light in m/s
UNIT_SCALE = {
    "GHz": 1e9, "MHz": 1e6, "KHz": 1e3, "Hz": 1.0,
}
WL_SCALE = {
    "mm": 1e-3, "cm": 1e-2, "m": 1.0, "km": 1e3,
}

REL_TOLERANCE = 0.01


def _positive_problem(name: str, value: float) -> str | None:
    if math.isnan(value):
        return f"{name} is NaN"
    if math.isinf(value):
        return f"{name} is Infinity"
    if value <= 0:
        return f"{name} must be a positive number (got {value})"
    return None


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser()
    parser.add_argument("--freq", type=float, required=True)
    parser.add_argument("--freq-unit", required=True)
    parser.add_argument("--wl", type=float, required=True)
    parser.add_argument("--wl-unit", required=True)
    args = parser.parse_args()

    for label, value in (("freq", args.freq), ("wl", args.wl)):
        problem = _positive_problem(label, value)
        if problem:
            print(f"[ERROR] {problem}")
            sys.exit(1)

    if args.freq_unit not in UNIT_SCALE:
        print(f"[ERROR] unknown frequency unit: {args.freq_unit}")
        sys.exit(1)
    if args.wl_unit not in WL_SCALE:
        print(f"[ERROR] unknown wavelength unit: {args.wl_unit}")
        sys.exit(1)

    freq_hz = args.freq * UNIT_SCALE[args.freq_unit]
    wl_m = args.wl * WL_SCALE[args.wl_unit]
    wl_calc_m = C_M_PER_S / freq_hz
    rel = abs(wl_m - wl_calc_m) / wl_calc_m
    if rel < REL_TOLERANCE:
        print(f"[OK] f*lambda consistent: {rel:.4%} relative error")
    else:
        print(f"[WARN] f*lambda inconsistent: {rel:.4%} relative error")
        sys.exit(1)


if __name__ == "__main__":
    main()
