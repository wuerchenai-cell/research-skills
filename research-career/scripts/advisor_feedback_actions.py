#!/usr/bin/env python3
"""Convert advisor or meeting feedback into a support-only action ledger."""
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
import re
from datetime import date
from typing import Sequence, TextIO

ACTION_REL = Path(SUPPORT_DIR_NAME) / "requirements"
CSV_NAME = "advisor-feedback-actions.csv"
JSON_NAME = "advisor-feedback-actions.json"

ACTION_COLUMNS = (
    "action_id",
    "feedback_id",
    "source",
    "raw_feedback",
    "action",
    "owner",
    "due",
    "status",
    "evidence_source",
    "created_at",
)

VALID_STATUSES = {"open", "in_progress", "done", "blocked", "snoozed"}


class AdvisorFeedbackError(ValueError):
    """Raised when advisor feedback input cannot be processed."""


def _root(project: Path) -> Path:
    return Path(project).resolve(strict=True)


def actions_dir(project: Path) -> Path:
    return _root(project) / ACTION_REL


def actions_path(project: Path) -> Path:
    return actions_dir(project) / CSV_NAME


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(ACTION_COLUMNS), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in ACTION_COLUMNS})


def init_actions(project: Path) -> dict[str, str]:
    path = actions_path(project)
    if not path.exists():
        _write_csv(path, [])
    readme = actions_dir(project) / "README-advisor-feedback-actions.md"
    if not readme.exists():
        readme.write_text(
            "# Advisor Feedback Actions\n\n"
            "Support-only action ledger for turning meeting/advisor feedback into "
            "owners, due dates, evidence links, and status. Do not put this ledger "
            "under 资料/ or 成果/.\n",
            encoding="utf-8",
        )
    return {"csv_path": path.as_posix(), "readme_path": readme.as_posix()}


def read_actions(project: Path) -> list[dict[str, str]]:
    path = actions_path(project)
    if not path.is_file():
        raise AdvisorFeedbackError(f"advisor feedback ledger not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return [{column: row.get(column, "") for column in ACTION_COLUMNS} for row in reader]


def _split_actions(text: str) -> list[str]:
    chunks = re.split(r"(?:\r?\n|[；;。]+)", text)
    actions: list[str] = []
    for chunk in chunks:
        cleaned = re.sub(r"^\s*(?:[-*]|\d+[.)、])\s*", "", chunk).strip()
        cleaned = cleaned.strip("，, ")
        if cleaned:
            actions.append(cleaned)
    return actions


def add_feedback(
    project: Path,
    *,
    feedback_id: str,
    text: str,
    owner: str = "",
    due: str = "",
    source: str = "",
    evidence_source: str = "",
    status: str = "open",
) -> list[dict[str, str]]:
    if not feedback_id.strip():
        raise AdvisorFeedbackError("feedback_id is required")
    if status not in VALID_STATUSES:
        raise AdvisorFeedbackError(f"invalid status: {status}")
    init_actions(project)
    rows = read_actions(project)
    created_at = utc_now()
    actions = _split_actions(text)
    if not actions:
        raise AdvisorFeedbackError("feedback text did not contain any action")
    new_rows: list[dict[str, str]] = []
    for index, action in enumerate(actions, start=1):
        row = {
            "action_id": f"{feedback_id.strip()}-a{index:02d}",
            "feedback_id": feedback_id.strip(),
            "source": source.strip(),
            "raw_feedback": text.strip(),
            "action": action,
            "owner": owner.strip(),
            "due": due.strip(),
            "status": status,
            "evidence_source": evidence_source.strip(),
            "created_at": created_at,
        }
        rows.append(row)
        new_rows.append(row)
    _write_csv(actions_path(project), rows)
    return new_rows


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


def lint_actions(project: Path, *, strict: bool = False) -> dict[str, object]:
    rows = read_actions(project)
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    seen: dict[str, int] = {}
    for index, row in enumerate(rows, start=2):
        action_id = row.get("action_id", "").strip()
        if not action_id:
            errors.append(_problem("missing_action_id", index, "action_id is empty"))
        elif action_id in seen:
            errors.append(_problem("duplicate_action_id", index, action_id))
        else:
            seen[action_id] = index
        if not row.get("feedback_id", "").strip():
            errors.append(_problem("missing_feedback_id", index, action_id or "row"))
        if not row.get("action", "").strip():
            errors.append(_problem("missing_action", index, action_id or "row"))
        if row.get("status", "").strip() not in VALID_STATUSES:
            errors.append(_problem("invalid_status", index, row.get("status", "")))
        if not _date_ok(row.get("due", "")):
            errors.append(_problem("invalid_due", index, row.get("due", "")))
        if not row.get("owner", "").strip():
            warnings.append(_problem("missing_owner", index, action_id or "row"))
        if not row.get("due", "").strip():
            warnings.append(_problem("missing_due", index, action_id or "row"))
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
    rows = read_actions(project)
    payload = {
        "schema_version": "1.0",
        "exported_at": utc_now(),
        "actions": rows,
    }
    out = actions_dir(project) / JSON_NAME
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"json_path": out.as_posix(), "action_count": len(rows), "actions": rows}


def _print_lint(result: dict[str, object], output: TextIO) -> None:
    print(f"Advisor feedback actions lint: {'PASS' if result['ok'] else 'FAIL'}", file=output)
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

    p_add = sub.add_parser("add")
    p_add.add_argument("--project", required=True, type=Path)
    p_add.add_argument("--feedback-id", required=True)
    p_add.add_argument("--text", required=True)
    p_add.add_argument("--owner", default="")
    p_add.add_argument("--due", default="")
    p_add.add_argument("--source", default="")
    p_add.add_argument("--evidence-source", default="")
    p_add.add_argument("--status", default="open", choices=sorted(VALID_STATUSES))

    p_lint = sub.add_parser("lint")
    p_lint.add_argument("--project", required=True, type=Path)
    p_lint.add_argument("--strict", action="store_true")
    p_lint.add_argument("--json", action="store_true")

    p_export = sub.add_parser("export-json")
    p_export.add_argument("--project", required=True, type=Path)
    return parser


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None, stderr: TextIO | None = None) -> int:
    output = stdout if stdout is not None else sys.stdout
    error_output = stderr if stderr is not None else sys.stderr
    args = build_parser().parse_args(argv)
    try:
        if args.command == "init":
            print(json.dumps(init_actions(args.project), ensure_ascii=False, indent=2), file=output)
            return 0
        if args.command == "add":
            rows = add_feedback(
                args.project,
                feedback_id=args.feedback_id,
                text=args.text,
                owner=args.owner,
                due=args.due,
                source=args.source,
                evidence_source=args.evidence_source,
                status=args.status,
            )
            print(json.dumps({"added": rows}, ensure_ascii=False, indent=2), file=output)
            return 0
        if args.command == "lint":
            result = lint_actions(args.project, strict=args.strict)
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2), file=output)
            else:
                _print_lint(result, output)
            return 0 if result["ok"] else 1
        if args.command == "export-json":
            print(json.dumps(export_json(args.project), ensure_ascii=False, indent=2), file=output)
            return 0
    except (AdvisorFeedbackError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"advisor_feedback_actions failed: {exc}", file=error_output)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
