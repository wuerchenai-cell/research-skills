#!/usr/bin/env python3
"""Minimal shared helpers for research-career scripts.

This module intentionally carries only what the bundled career scripts
need: the support-directory name, a UTC timestamp helper, and a CSV
serializer. It is self-contained and does not depend on any other
skill or package.
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from io import StringIO
from typing import Mapping, Sequence

SUPPORT_DIR_NAME = "skill辅助（用户无需打开，辅助skill使用）"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def csv_text(rows: Sequence[Mapping[str, object]], columns: Sequence[str]) -> str:
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=list(columns), lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({column: row.get(column, "") for column in columns})
    return output.getvalue()
