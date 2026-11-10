#!/usr/bin/env python3
"""Consulting deck blueprint（显式选择的咨询式演示模式）。

Boundary:
- blueprint / briefs / lint 结果只写辅助区 presentation/consulting-deck/。
- 默认 output_mode=native_academic；consulting_image_only 仅在用户显式传入时启用。
- 批量 export 前 sample_gate 必须 approved。
- 实际 PPTX 生成仍走 Output Layer（deliverable_factory / render chain），
  本脚本不创建平行交付链，也不写 成果/。

CLI:
    init --project P --deck-id ID --audience A --use-case U [--mode M]
    add-page --project P --deck-id ID --page-id S01 --title T --message M \
        [--proof-object chart] [--evidence E-001]... [--label illustrative|forward]
    approve-sample --project P --deck-id ID
    lint --project P --deck-id ID [--strict]
    export --project P --deck-id ID

Exit codes: 0 ok, 1 validation/blocked, 2 file error.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

try:
    from _career_common import SUPPORT_DIR_NAME
except ImportError:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _career_common import SUPPORT_DIR_NAME

DECK_DIR_REL = "presentation/consulting-deck"
BLUEPRINTS_REL = f"{DECK_DIR_REL}/blueprints"
BRIEFS_REL = f"{DECK_DIR_REL}/slide-briefs"
QA_REL = f"{DECK_DIR_REL}/qa"

ALLOWED_MODES = ("native_academic", "consulting_image_only", "hybrid_selective_editable")
ALLOWED_PROOF_OBJECTS = ("chart", "table", "diagram", "quote", "image", "equation", "none")
ALLOWED_LABELS = ("illustrative", "forward")
ALLOWED_DETAIL = ("executive", "technical", "mixed")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def blueprint_path(project: Path, deck_id: str) -> Path:
    return Path(project) / SUPPORT_DIR_NAME / BLUEPRINTS_REL / f"{deck_id}.json"


def _load(project: Path, deck_id: str) -> dict | None:
    path = blueprint_path(project, deck_id)
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _save(project: Path, deck_id: str, deck: dict) -> Path:
    path = blueprint_path(project, deck_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(deck, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def init_deck(project: Path, deck_id: str, audience: str, use_case: str,
              mode: str | None = None, detail_level: str = "executive",
              visual_style: str = "", language: str = "zh",
              evidence_boundary: str = "verified-only") -> dict:
    if not deck_id or not audience.strip() or not use_case.strip():
        return {"exit_code": 1, "status": "error", "reason": "audience 与 use case 必填"}
    if mode is None:
        mode = "native_academic"  # 用户未显式要求图片型咨询 deck 时，默认 native_academic
    if mode not in ALLOWED_MODES:
        return {"exit_code": 1, "status": "error", "reason": f"mode 非法: {mode}"}
    if detail_level not in ALLOWED_DETAIL:
        return {"exit_code": 1, "status": "error", "reason": f"detail_level 非法: {detail_level}"}
    if evidence_boundary not in ("verified-only", "allow-labelled-forward"):
        return {"exit_code": 1, "status": "error", "reason": f"evidence_boundary 非法: {evidence_boundary}"}
    deck = {
        "schema_version": "1.0",
        "deck_id": deck_id,
        "audience": audience,
        "decision_or_use_case": use_case,
        "detail_level": detail_level,
        "visual_style": visual_style,
        "language": language or "zh",
        "output_mode": mode,
        "evidence_boundary": evidence_boundary,
        "sample_gate": "pending",
        "pages": [],
        "created_at": utc_now(),
        "note": (
            "image-only 模式的 deck 可搜索性/可访问性/可编辑性弱于原生 PPT，"
            "最终 QA 状态最多 needs-human-review。"
            if mode == "consulting_image_only" else
            "实际 PPTX 生成走 Output Layer 既有渲染链。"
        ),
    }
    path = _save(project, deck_id, deck)
    return {"exit_code": 0, "status": "created", "blueprint": str(path), "output_mode": mode}


def add_page(project: Path, deck_id: str, page_id: str, title: str, message: str,
             proof_object: str = "none", evidence: Sequence[str] | None = None,
             label: str | None = None, visual_brief: str = "",
             open_questions: Sequence[str] | None = None) -> dict:
    deck = _load(project, deck_id)
    if deck is None:
        return {"exit_code": 2, "error": f"blueprint not found: {deck_id}"}
    if not page_id.strip() or not title.strip():
        return {"exit_code": 1, "status": "error", "reason": "page_id 与 title 必填"}
    if not message.strip():
        return {"exit_code": 1, "status": "error",
                "reason": "每页必须有一个 governing message（proof object 驱动的核心论点）"}
    if proof_object not in ALLOWED_PROOF_OBJECTS:
        return {"exit_code": 1, "status": "error", "reason": f"proof_object 非法: {proof_object}"}
    if any(p["page_id"] == page_id for p in deck["pages"]):
        return {"exit_code": 1, "status": "error", "reason": f"page_id 重复: {page_id}"}
    if proof_object != "none" and not (evidence or label):
        return {"exit_code": 1, "status": "error",
                "reason": "proof object 非 none 时必须提供 evidence_refs 或 forward/illustrative 标签"}
    if label is not None and label not in ALLOWED_LABELS:
        return {"exit_code": 1, "status": "error", "reason": f"label 非法: {label}"}
    page = {
        "page_id": page_id,
        "title": title,
        "governing_message": message,
        "proof_object": proof_object,
        "evidence_refs": list(evidence or []),
        "evidence_label": label,
        "visual_brief": visual_brief,
        "open_questions": list(open_questions or []),
    }
    deck["pages"].append(page)
    _save(project, deck_id, deck)
    return {"exit_code": 0, "status": "added", "page_id": page_id}


def approve_sample(project: Path, deck_id: str) -> dict:
    deck = _load(project, deck_id)
    if deck is None:
        return {"exit_code": 2, "error": f"blueprint not found: {deck_id}"}
    if not deck["pages"]:
        return {"exit_code": 1, "status": "error", "reason": "至少需要一页才能批准样页 gate"}
    deck["sample_gate"] = "approved"
    deck["sample_gate_approved_at"] = utc_now()
    _save(project, deck_id, deck)
    return {"exit_code": 0, "status": "approved"}


def lint_deck(project: Path, deck_id: str, strict: bool = False) -> dict:
    deck = _load(project, deck_id)
    if deck is None:
        return {"exit_code": 2, "error": f"blueprint not found: {deck_id}"}
    errors: list[str] = []
    warnings: list[str] = []
    if not str(deck.get("audience", "")).strip():
        errors.append("audience 为空")
    if not str(deck.get("decision_or_use_case", "")).strip():
        errors.append("use case 为空")
    if deck.get("output_mode") not in ALLOWED_MODES:
        errors.append(f"mode 非法: {deck.get('output_mode')}")
    if not str(deck.get("language", "")).strip():
        errors.append("language 为空")
    page_ids = [p.get("page_id") for p in deck.get("pages", [])]
    if len(page_ids) != len(set(page_ids)):
        errors.append("page_id 存在重复")
    for page in deck.get("pages", []):
        pid = page.get("page_id", "?")
        if not str(page.get("title", "")).strip():
            errors.append(f"{pid}: title 缺失")
        if not str(page.get("governing_message", "")).strip():
            errors.append(f"{pid}: governing message 缺失")
        if page.get("proof_object", "none") != "none":
            if not page.get("evidence_refs") and not page.get("evidence_label"):
                errors.append(f"{pid}: proof object 无 evidence_refs 也无 forward/illustrative 标签")
        if strict and not str(page.get("visual_brief", "")).strip():
            warnings.append(f"{pid}: visual_brief 缺失（strict 提示）")
    if deck.get("output_mode") == "consulting_image_only":
        warnings.append("image-only deck：最终交付物必须通过 final_presentation_qa 并标记 image_only")
    return {
        "exit_code": 1 if errors else 0,
        "errors": errors,
        "warnings": warnings,
        "sample_gate": deck.get("sample_gate"),
        "output_mode": deck.get("output_mode"),
    }


def export_deck(project: Path, deck_id: str) -> dict:
    deck = _load(project, deck_id)
    if deck is None:
        return {"exit_code": 2, "error": f"blueprint not found: {deck_id}"}
    if deck.get("sample_gate") != "approved":
        return {
            "exit_code": 1, "status": "blocked",
            "reason": "sample gate 未 approved：批量 export 前必须先通过样页确认（approve-sample）。",
        }
    lint = lint_deck(project, deck_id)
    if lint["exit_code"] != 0:
        return {"exit_code": 1, "status": "blocked",
                "reason": "lint 未通过，先修复 blueprint", "errors": lint["errors"]}
    briefs_dir = Path(project) / SUPPORT_DIR_NAME / BRIEFS_REL
    briefs_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for page in deck["pages"]:
        brief = {
            "deck_id": deck_id,
            "output_mode": deck["output_mode"],
            "page_id": page["page_id"],
            "title": page["title"],
            "governing_message": page["governing_message"],
            "proof_object": page["proof_object"],
            "evidence_refs": page.get("evidence_refs", []),
            "evidence_label": page.get("evidence_label"),
            "visual_brief": page.get("visual_brief", ""),
            "open_questions": page.get("open_questions", []),
        }
        path = briefs_dir / f"{deck_id}-{page['page_id']}.json"
        path.write_text(json.dumps(brief, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written.append(str(path))
    summary_path = briefs_dir / f"{deck_id}-build-summary.json"
    summary = {
        "deck_id": deck_id,
        "output_mode": deck["output_mode"],
        "page_count": len(deck["pages"]),
        "image_only": deck["output_mode"] == "consulting_image_only",
        "editability_claim": (
            "image-only pages are NOT natively editable"
            if deck["output_mode"] == "consulting_image_only"
            else "native objects preferred; per-slide editability matrix required for hybrid mode"
        ),
        "next_step": "render via Output Layer chain, then run final_presentation_qa.py",
        "exported_at": utc_now(),
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    written.append(str(summary_path))
    return {"exit_code": 0, "status": "exported", "files": written,
            "output_mode": deck["output_mode"]}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="consulting_deck_blueprint.py",
        description="Consulting deck blueprint: init / add-page / approve-sample / lint / export.",
    )
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("init")
    p.add_argument("--project", required=True, type=Path)
    p.add_argument("--deck-id", required=True)
    p.add_argument("--audience", required=True)
    p.add_argument("--use-case", required=True)
    p.add_argument("--mode", default=None, choices=ALLOWED_MODES)
    p.add_argument("--detail-level", default="executive", choices=ALLOWED_DETAIL)
    p.add_argument("--visual-style", default="")
    p.add_argument("--language", default="zh")
    p.add_argument("--evidence-boundary", default="verified-only",
                   choices=("verified-only", "allow-labelled-forward"))
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("add-page")
    p.add_argument("--project", required=True, type=Path)
    p.add_argument("--deck-id", required=True)
    p.add_argument("--page-id", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--message", required=True)
    p.add_argument("--proof-object", default="none", choices=ALLOWED_PROOF_OBJECTS)
    p.add_argument("--evidence", action="append", default=[])
    p.add_argument("--label", default=None, choices=ALLOWED_LABELS)
    p.add_argument("--visual-brief", default="")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("approve-sample")
    p.add_argument("--project", required=True, type=Path)
    p.add_argument("--deck-id", required=True)
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("lint")
    p.add_argument("--project", required=True, type=Path)
    p.add_argument("--deck-id", required=True)
    p.add_argument("--strict", action="store_true")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("export")
    p.add_argument("--project", required=True, type=Path)
    p.add_argument("--deck-id", required=True)
    p.add_argument("--json", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_usage(sys.stderr)
        return 2
    if args.command == "init":
        result = init_deck(args.project, args.deck_id, args.audience, args.use_case,
                           mode=args.mode, detail_level=args.detail_level,
                           visual_style=args.visual_style, language=args.language,
                           evidence_boundary=args.evidence_boundary)
    elif args.command == "add-page":
        result = add_page(args.project, args.deck_id, args.page_id, args.title, args.message,
                          proof_object=args.proof_object, evidence=args.evidence,
                          label=args.label, visual_brief=args.visual_brief)
    elif args.command == "approve-sample":
        result = approve_sample(args.project, args.deck_id)
    elif args.command == "lint":
        result = lint_deck(args.project, args.deck_id, strict=args.strict)
    else:
        result = export_deck(args.project, args.deck_id)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for key in ("status", "blueprint", "output_mode", "page_id", "sample_gate",
                    "exit_code", "reason", "error"):
            if key in result:
                print(f"{key}: {result[key]}")
        for err in result.get("errors", []):
            print(f"  error: {err}")
        for warn in result.get("warnings", []):
            print(f"  warning: {warn}")
    return int(result.get("exit_code", 0))


if __name__ == "__main__":
    raise SystemExit(main())
