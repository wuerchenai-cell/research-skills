#!/usr/bin/env python3
"""Maintain a reviewer-comment response matrix and support-only draft."""
from __future__ import annotations

import sys
from pathlib import Path

# Bootstrap: some Python distributions (e.g. isolated/embedded builds) do not
# add the script's own directory to sys.path, which would break the sibling
# import below. Adding it explicitly keeps the script runnable everywhere.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _career_common import SUPPORT_DIR_NAME, utc_now

import argparse
import csv
import json
from datetime import date
from typing import Sequence, TextIO

MATRIX_REL = Path(SUPPORT_DIR_NAME) / "rebuttal"
DRAFT_REL = Path(SUPPORT_DIR_NAME) / "drafts"
CSV_NAME = "response-matrix.csv"
JSON_NAME = "response-matrix.json"
DRAFT_NAME = "response-letter-draft.md"

MATRIX_COLUMNS = (
    "comment_id",
    "reviewer",
    "comment",
    "requested_change",
    "response_summary",
    "evidence_source",
    "manuscript_location",
    "status",
    "owner",
    "due",
    "created_at",
)

VALID_STATUSES = {"open", "addressed", "needs_evidence", "declined_with_reason", "needs_human_review"}


class ResponseLetterError(ValueError):
    """Raised when response-letter matrix input is invalid."""


def _root(project: Path) -> Path:
    return Path(project).resolve(strict=True)


def matrix_dir(project: Path) -> Path:
    return _root(project) / MATRIX_REL


def matrix_path(project: Path) -> Path:
    return matrix_dir(project) / CSV_NAME


def draft_path(project: Path) -> Path:
    return _root(project) / DRAFT_REL / DRAFT_NAME


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(MATRIX_COLUMNS), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in MATRIX_COLUMNS})


def init_matrix(project: Path) -> dict[str, str]:
    path = matrix_path(project)
    if not path.exists():
        _write_csv(path, [])
    readme = matrix_dir(project) / "README-response-letter.md"
    if not readme.exists():
        readme.write_text(
            "# Response Letter Matrix\n\n"
            "Support-only reviewer-comment matrix. A polished DOCX may later be "
            "exported from a validated draft, but this matrix itself must stay in "
            "the support area.\n",
            encoding="utf-8",
        )
    return {"csv_path": path.as_posix(), "readme_path": readme.as_posix()}


def read_matrix(project: Path) -> list[dict[str, str]]:
    path = matrix_path(project)
    if not path.is_file():
        raise ResponseLetterError(f"response matrix not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return [{column: row.get(column, "") for column in MATRIX_COLUMNS} for row in reader]


def add_comment(
    project: Path,
    *,
    comment_id: str,
    reviewer: str,
    comment: str,
    requested_change: str = "",
    response_summary: str = "",
    evidence_source: str = "",
    manuscript_location: str = "",
    status: str = "open",
    owner: str = "",
    due: str = "",
) -> dict[str, str]:
    if not comment_id.strip():
        raise ResponseLetterError("comment_id is required")
    if status not in VALID_STATUSES:
        raise ResponseLetterError(f"invalid status: {status}")
    init_matrix(project)
    rows = read_matrix(project)
    row = {
        "comment_id": comment_id.strip(),
        "reviewer": reviewer.strip(),
        "comment": comment.strip(),
        "requested_change": requested_change.strip(),
        "response_summary": response_summary.strip(),
        "evidence_source": evidence_source.strip(),
        "manuscript_location": manuscript_location.strip(),
        "status": status,
        "owner": owner.strip(),
        "due": due.strip(),
        "created_at": utc_now(),
    }
    rows.append(row)
    _write_csv(matrix_path(project), rows)
    return row


def _date_ok(value: str) -> bool:
    if not value.strip():
        return True
    try:
        date.fromisoformat(value.strip())
    except ValueError:
        return False
    return True


def _problem(kind: str, row: int, detail: str) -> dict[str, str]:
    return {"kind": kind, "row": str(row), "detail": detail}


def lint_matrix(project: Path, *, strict: bool = False) -> dict[str, object]:
    rows = read_matrix(project)
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    seen: dict[str, int] = {}
    for index, row in enumerate(rows, start=2):
        comment_id = row.get("comment_id", "").strip()
        status = row.get("status", "").strip()
        if not comment_id:
            errors.append(_problem("missing_comment_id", index, "comment_id is empty"))
        elif comment_id in seen:
            errors.append(_problem("duplicate_comment_id", index, comment_id))
        else:
            seen[comment_id] = index
        if not row.get("reviewer", "").strip():
            errors.append(_problem("missing_reviewer", index, comment_id or "row"))
        if not row.get("comment", "").strip():
            errors.append(_problem("missing_comment", index, comment_id or "row"))
        if status not in VALID_STATUSES:
            errors.append(_problem("invalid_status", index, status))
        if not row.get("response_summary", "").strip():
            warnings.append(_problem("missing_response_summary", index, comment_id or "row"))
        if status == "addressed" and not row.get("evidence_source", "").strip():
            warnings.append(_problem("addressed_missing_evidence_source", index, comment_id or "row"))
        if not _date_ok(row.get("due", "")):
            errors.append(_problem("invalid_due", index, row.get("due", "")))
    if strict:
        errors.extend(warnings)
        warnings = []
    return {
        "ok": not errors,
        "row_count": len(rows),
        "errors": errors,
        "warnings": warnings,
        "strict": strict,
        "checked_at": utc_now(),
    }


def export_json(project: Path) -> dict[str, object]:
    rows = read_matrix(project)
    payload = {
        "schema_version": "1.0",
        "exported_at": utc_now(),
        "comments": rows,
    }
    out = matrix_dir(project) / JSON_NAME
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"json_path": out.as_posix(), "comment_count": len(rows), "comments": rows}


def _group_rows(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        reviewer = row.get("reviewer", "").strip() or "Reviewer"
        grouped.setdefault(reviewer, []).append(row)
    return grouped


def export_draft(project: Path) -> dict[str, object]:
    rows = read_matrix(project)
    path = draft_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Response Letter Draft",
        "",
        f"Generated: {utc_now()}",
        "",
        "This is a support-only draft. Verify every response against the manuscript and evidence before promotion.",
        "",
    ]
    for reviewer, reviewer_rows in _group_rows(rows).items():
        lines.append(f"## {reviewer}")
        lines.append("")
        for row in reviewer_rows:
            lines.append(f"### {row.get('comment_id', '').strip() or 'comment'}")
            lines.append("")
            lines.append(f"**Comment:** {row.get('comment', '').strip()}")
            if row.get("requested_change", "").strip():
                lines.append(f"**Requested change:** {row['requested_change'].strip()}")
            lines.append(f"**Response:** {row.get('response_summary', '').strip() or '[response needed]'}")
            if row.get("manuscript_location", "").strip():
                lines.append(f"**Manuscript location:** {row['manuscript_location'].strip()}")
            if row.get("evidence_source", "").strip():
                lines.append(f"**Evidence source:** {row['evidence_source'].strip()}")
            lines.append(f"**Status:** {row.get('status', '').strip() or 'open'}")
            lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return {"draft_path": path.as_posix(), "comment_count": len(rows)}


def _print_lint(result: dict[str, object], output: TextIO) -> None:
    print(f"Response letter matrix lint: {'PASS' if result['ok'] else 'FAIL'}", file=output)
    print(f"Rows: {result['row_count']}", file=output)
    for item in result.get("errors", []):
        print(f"ERROR row {item['row']}: {item['kind']} - {item['detail']}", file=output)
    for item in result.get("warnings", []):
        print(f"WARN row {item['row']}: {item['kind']} - {item['detail']}", file=output)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p_init = sub.add_parser("init")
    p_init.add_argument("--project", required=True, type=Path)

    p_add = sub.add_parser("add-comment")
    p_add.add_argument("--project", required=True, type=Path)
    p_add.add_argument("--comment-id", required=True)
    p_add.add_argument("--reviewer", required=True)
    p_add.add_argument("--comment", required=True)
    p_add.add_argument("--requested-change", default="")
    p_add.add_argument("--response-summary", default="")
    p_add.add_argument("--evidence-source", default="")
    p_add.add_argument("--manuscript-location", default="")
    p_add.add_argument("--status", default="open", choices=sorted(VALID_STATUSES))
    p_add.add_argument("--owner", default="")
    p_add.add_argument("--due", default="")

    p_lint = sub.add_parser("lint")
    p_lint.add_argument("--project", required=True, type=Path)
    p_lint.add_argument("--strict", action="store_true")
    p_lint.add_argument("--json", action="store_true")

    p_draft = sub.add_parser("export-draft")
    p_draft.add_argument("--project", required=True, type=Path)

    p_json = sub.add_parser("export-json")
    p_json.add_argument("--project", required=True, type=Path)
    return parser


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None, stderr: TextIO | None = None) -> int:
    output = stdout if stdout is not None else sys.stdout
    error_output = stderr if stderr is not None else sys.stderr
    args = build_parser().parse_args(argv)
    try:
        if args.command == "init":
            print(json.dumps(init_matrix(args.project), ensure_ascii=False, indent=2), file=output)
            return 0
        if args.command == "add-comment":
            row = add_comment(
                args.project,
                comment_id=args.comment_id,
                reviewer=args.reviewer,
                comment=args.comment,
                requested_change=args.requested_change,
                response_summary=args.response_summary,
                evidence_source=args.evidence_source,
                manuscript_location=args.manuscript_location,
                status=args.status,
                owner=args.owner,
                due=args.due,
            )
            print(json.dumps(row, ensure_ascii=False, indent=2), file=output)
            return 0
        if args.command == "lint":
            result = lint_matrix(args.project, strict=args.strict)
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2), file=output)
            else:
                _print_lint(result, output)
            return 0 if result["ok"] else 1
        if args.command == "export-draft":
            print(json.dumps(export_draft(args.project), ensure_ascii=False, indent=2), file=output)
            return 0
        if args.command == "export-json":
            print(json.dumps(export_json(args.project), ensure_ascii=False, indent=2), file=output)
            return 0
    except (ResponseLetterError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"response_letter failed: {exc}", file=error_output)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
