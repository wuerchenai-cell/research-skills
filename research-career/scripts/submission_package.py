#!/usr/bin/env python3
"""Audit a manuscript submission package without external dependencies."""
from __future__ import annotations

import sys
from pathlib import Path

# Bootstrap: some Python distributions (e.g. isolated/embedded builds) do not
# add the script's own directory to sys.path, which would break the sibling
# import below. Adding it explicitly keeps the script runnable everywhere.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _career_common import SUPPORT_DIR_NAME, csv_text, utc_now

import argparse
import json
from typing import Sequence, TextIO

REPORT_REL = Path(SUPPORT_DIR_NAME) / "logs" / "submission-package"
JSON_NAME = "submission-package-audit.json"
CSV_NAME = "submission-package-audit.csv"


def _root(project: Path) -> Path:
    return Path(project).resolve(strict=True)


def report_dir(project: Path) -> Path:
    return _root(project) / REPORT_REL


def _problem(kind: str, field: str, detail: str) -> dict[str, str]:
    return {"kind": kind, "field": field, "detail": detail}


def _check_file(
    *,
    label: str,
    path_value: str | Path | None,
    required: bool,
    allowed_suffixes: set[str],
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
) -> dict[str, str]:
    if path_value is None or not str(path_value).strip():
        item = {"label": label, "path": "", "status": "missing"}
        if required:
            errors.append(_problem(f"missing_{label}", label, f"{label} is required"))
        else:
            warnings.append(_problem(f"missing_{label}", label, f"{label} not provided"))
        return item
    path = Path(path_value)
    item = {"label": label, "path": path.as_posix(), "status": "present"}
    if not path.is_file():
        item["status"] = "not_found"
        errors.append(_problem("file_not_found", label, path.as_posix()))
        return item
    suffix = path.suffix.lower()
    if allowed_suffixes and suffix not in allowed_suffixes:
        warnings.append(_problem("unexpected_suffix", label, f"{path.name} should be one of {sorted(allowed_suffixes)}"))
        item["status"] = "present_unexpected_suffix"
    return item


def audit_package(
    project: Path,
    *,
    venue: str = "",
    manuscript: str | Path | None = None,
    cover_letter: str | Path | None = None,
    highlights: str | Path | None = None,
    graphical_abstract: str | Path | None = None,
    supplement: str | Path | None = None,
    data_availability_statement: str = "",
    coi_statement: str = "",
    author_contribution_statement: str = "",
    strict: bool = False,
) -> dict[str, object]:
    _root(project)
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    items = [
        _check_file(
            label="manuscript",
            path_value=manuscript,
            required=True,
            allowed_suffixes={".docx", ".pdf"},
            errors=errors,
            warnings=warnings,
        ),
        _check_file(
            label="cover_letter",
            path_value=cover_letter,
            required=False,
            allowed_suffixes={".docx", ".pdf", ".txt"},
            errors=errors,
            warnings=warnings,
        ),
        _check_file(
            label="highlights",
            path_value=highlights,
            required=False,
            allowed_suffixes={".docx", ".pdf", ".txt"},
            errors=errors,
            warnings=warnings,
        ),
        _check_file(
            label="graphical_abstract",
            path_value=graphical_abstract,
            required=False,
            allowed_suffixes={".png", ".jpg", ".jpeg", ".svg", ".pdf"},
            errors=errors,
            warnings=warnings,
        ),
        _check_file(
            label="supplement",
            path_value=supplement,
            required=False,
            allowed_suffixes={".docx", ".pdf", ".xlsx", ".zip"},
            errors=errors,
            warnings=warnings,
        ),
    ]
    if not data_availability_statement.strip():
        warnings.append(_problem("missing_data_availability_statement", "data_availability_statement", "data/code availability should be stated or marked not applicable"))
    if not coi_statement.strip():
        warnings.append(_problem("missing_coi_statement", "coi_statement", "conflict-of-interest statement not recorded"))
    if not author_contribution_statement.strip():
        warnings.append(_problem("missing_author_contribution_statement", "author_contribution_statement", "author contribution statement not recorded"))

    if strict:
        escalated = [
            item
            for item in warnings
            if item["kind"]
            in {
                "missing_cover_letter",
                "missing_data_availability_statement",
                "missing_coi_statement",
                "missing_author_contribution_statement",
            }
        ]
        errors.extend(escalated)
        warnings = [item for item in warnings if item not in escalated]

    payload = {
        "schema_version": "1.0",
        "generated_at": utc_now(),
        "venue": venue.strip(),
        "items": items,
        "statements": {
            "data_availability_statement": data_availability_statement.strip(),
            "coi_statement": coi_statement.strip(),
            "author_contribution_statement": author_contribution_statement.strip(),
        },
        "warnings": warnings,
        "errors": errors,
        "ok": not errors,
        "boundary": "checklist adapter only; venue instructions and human review remain required",
    }
    out_dir = report_dir(project)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / JSON_NAME
    csv_path = out_dir / CSV_NAME
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = [
        {
            "label": item["label"],
            "path": item["path"],
            "status": item["status"],
            "generated_at": payload["generated_at"],
        }
        for item in items
    ]
    csv_path.write_text(csv_text(rows, ("generated_at", "label", "path", "status")), encoding="utf-8-sig")
    return {
        "ok": payload["ok"],
        "json_path": json_path.as_posix(),
        "csv_path": csv_path.as_posix(),
        "items": items,
        "warnings": warnings,
        "errors": errors,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--venue", default="")
    parser.add_argument("--manuscript", type=Path, default=None)
    parser.add_argument("--cover-letter", type=Path, default=None)
    parser.add_argument("--highlights", type=Path, default=None)
    parser.add_argument("--graphical-abstract", type=Path, default=None)
    parser.add_argument("--supplement", type=Path, default=None)
    parser.add_argument("--data-availability-statement", default="")
    parser.add_argument("--coi-statement", default="")
    parser.add_argument("--author-contribution-statement", default="")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def _print_human(result: dict[str, object], output: TextIO) -> None:
    print(f"Submission package audit: {'PASS' if result['ok'] else 'FAIL'}", file=output)
    print(f"Report: {result['json_path']}", file=output)
    for item in result.get("errors", []):
        print(f"ERROR {item['field']}: {item['kind']} - {item['detail']}", file=output)
    for item in result.get("warnings", []):
        print(f"WARN {item['field']}: {item['kind']} - {item['detail']}", file=output)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None, stderr: TextIO | None = None) -> int:
    output = stdout if stdout is not None else sys.stdout
    error_output = stderr if stderr is not None else sys.stderr
    args = build_parser().parse_args(argv)
    try:
        result = audit_package(
            args.project,
            venue=args.venue,
            manuscript=args.manuscript,
            cover_letter=args.cover_letter,
            highlights=args.highlights,
            graphical_abstract=args.graphical_abstract,
            supplement=args.supplement,
            data_availability_statement=args.data_availability_statement,
            coi_statement=args.coi_statement,
            author_contribution_statement=args.author_contribution_statement,
            strict=args.strict,
        )
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"submission_package failed: {exc}", file=error_output)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2), file=output)
    else:
        _print_human(result, output)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
