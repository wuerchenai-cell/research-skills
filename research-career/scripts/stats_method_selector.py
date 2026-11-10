#!/usr/bin/env python3
"""Offline statistical method triage for project support reports.

This script selects a conservative candidate method from a small checklist. It
does not run statistics, optimize p values, or replace a statistician. All
reports stay under skill辅助（用户无需打开，辅助skill使用）/.
"""
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

REPORT_REL = Path(SUPPORT_DIR_NAME) / "analysis"
JSON_NAME = "statistics-method-selection.json"
CSV_NAME = "statistics-method-selection.csv"


def _clean(value: object) -> str:
    return str(value or "").strip()


def _normality_note(normality: str) -> str:
    value = _clean(normality).lower()
    if value in {"normal", "approximately_normal", "approx_normal"}:
        return "normality recorded as acceptable; still report diagnostics"
    if value in {"non_normal", "skewed"}:
        return "normality concern recorded; prefer robust/non-parametric sensitivity analysis"
    return "normality unknown; inspect distribution and report the diagnostic result"


def recommend_method(
    *,
    outcome_type: str,
    group_count: int,
    paired: bool = False,
    repeated: bool = False,
    normality: str = "unknown",
    sample_size_per_group: int | None = None,
    predictor_type: str = "",
    task: str = "compare",
) -> dict[str, object]:
    """Return a conservative method recommendation without using dependencies."""
    outcome = _clean(outcome_type).lower()
    predictor = _clean(predictor_type).lower()
    warnings: list[str] = []
    assumptions = [
        "confirm independent sampling unless paired/repeated design is explicit",
        _normality_note(normality),
        "predefine exclusions and covariates before looking at significance",
    ]
    effect_size = "report an effect size with confidence interval"
    reporting = [
        "state sample size per group and missing-data handling",
        "report exact p values where appropriate",
        "separate exploratory analysis from confirmatory analysis",
    ]
    rationale = "selected by outcome type, group count, pairing, and small-sample caution"

    if not outcome:
        return {
            "primary_method": "needs-human-review",
            "rationale": "outcome_type is missing",
            "assumption_checks": assumptions,
            "effect_size": effect_size,
            "reporting": reporting,
            "warnings": ["outcome_type missing"],
        }

    if group_count <= 0:
        warnings.append("group_count must be positive; human review required")
        group_count = 0

    if repeated:
        primary = "linear mixed model" if outcome == "continuous" else "generalized mixed model"
        effect_size = "report model coefficient/effect estimate with confidence interval"
    elif outcome in {"continuous", "numeric", "scale"}:
        if group_count == 1:
            primary = "one-sample t-test or Wilcoxon signed-rank test"
            effect_size = "mean difference or median shift with confidence interval"
        elif group_count == 2:
            if paired:
                primary = "paired t-test"
                effect_size = "paired mean difference with confidence interval"
                if _clean(normality).lower() in {"non_normal", "skewed"}:
                    primary = "Wilcoxon signed-rank test"
                    warnings.append("paired continuous outcome is non-normal; consider Wilcoxon signed-rank")
            else:
                primary = "Welch t-test"
                effect_size = "mean difference and standardized mean difference with confidence interval"
                if _clean(normality).lower() in {"non_normal", "skewed"}:
                    warnings.append("non-normal continuous outcome; add Mann-Whitney U sensitivity analysis")
        elif group_count > 2:
            primary = "Welch ANOVA"
            effect_size = "omega-squared or eta-squared with confidence interval"
            if paired:
                primary = "repeated-measures ANOVA or linear mixed model"
            if _clean(normality).lower() in {"non_normal", "skewed"}:
                warnings.append("non-normal multi-group outcome; consider Kruskal-Wallis sensitivity analysis")
        else:
            primary = "needs-human-review"
    elif outcome in {"binary", "categorical", "proportion"}:
        if group_count == 2:
            small = sample_size_per_group is not None and sample_size_per_group <= 20
            if small:
                primary = "Fisher exact test"
                warnings.append("small cell/sample size; Fisher exact test is safer than chi-square")
            else:
                primary = "chi-square test"
            effect_size = "risk ratio, odds ratio, or risk difference with confidence interval"
        elif group_count > 2:
            primary = "chi-square test"
            effect_size = "Cramer's V or model-based contrast with confidence interval"
            if sample_size_per_group is not None and sample_size_per_group <= 20:
                warnings.append("small groups; check expected cell counts and consider exact/Monte Carlo methods")
        else:
            primary = "binomial test"
            effect_size = "proportion with confidence interval"
    elif outcome in {"time_to_event", "survival"}:
        primary = "Kaplan-Meier plus log-rank test"
        effect_size = "hazard ratio with confidence interval"
        if predictor in {"continuous", "multi_covariate"} or task in {"adjust", "model"}:
            primary = "Cox proportional hazards model"
        assumptions.append("check proportional hazards assumption")
    elif outcome in {"count", "rate"}:
        primary = "Poisson or negative binomial regression"
        effect_size = "rate ratio with confidence interval"
        assumptions.append("check overdispersion; use negative binomial when overdispersed")
    else:
        primary = "needs-human-review"
        warnings.append(f"unrecognized outcome_type: {outcome_type}")

    if sample_size_per_group is not None and sample_size_per_group < 5:
        warnings.append("very small sample size; treat inference as exploratory and seek methods review")

    return {
        "primary_method": primary,
        "rationale": rationale,
        "assumption_checks": assumptions,
        "effect_size": effect_size,
        "reporting": reporting,
        "warnings": warnings,
    }


def _report_dir(project: Path) -> Path:
    return Path(project).resolve(strict=True) / REPORT_REL


def select_and_write(
    project: Path,
    *,
    question: str,
    outcome_type: str,
    group_count: int,
    paired: bool = False,
    repeated: bool = False,
    normality: str = "unknown",
    sample_size_per_group: int | None = None,
    predictor_type: str = "",
    strict: bool = False,
) -> dict[str, object]:
    recommendation = recommend_method(
        outcome_type=outcome_type,
        group_count=group_count,
        paired=paired,
        repeated=repeated,
        normality=normality,
        sample_size_per_group=sample_size_per_group,
        predictor_type=predictor_type,
    )
    errors: list[dict[str, str]] = []
    warnings = [{"kind": "method_warning", "detail": text} for text in recommendation.get("warnings", [])]
    if recommendation["primary_method"] == "needs-human-review":
        errors.append({"kind": "needs_human_review", "detail": "method selection could not be automated"})
    if strict and warnings:
        errors.extend({"kind": item["kind"], "detail": item["detail"]} for item in warnings)
        warnings = []

    payload = {
        "schema_version": "1.0",
        "generated_at": utc_now(),
        "question": _clean(question),
        "inputs": {
            "outcome_type": _clean(outcome_type),
            "group_count": group_count,
            "paired": paired,
            "repeated": repeated,
            "normality": _clean(normality),
            "sample_size_per_group": sample_size_per_group if sample_size_per_group is not None else "",
            "predictor_type": _clean(predictor_type),
        },
        "recommendation": recommendation,
        "warnings": warnings,
        "errors": errors,
        "ok": not errors,
        "boundary": "triage only; confirm with study design, assumptions, and domain/statistics review",
    }

    out_dir = _report_dir(project)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / JSON_NAME
    csv_path = out_dir / CSV_NAME
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    row = {
        "generated_at": payload["generated_at"],
        "question": payload["question"],
        "outcome_type": payload["inputs"]["outcome_type"],
        "group_count": str(group_count),
        "paired": str(paired),
        "repeated": str(repeated),
        "primary_method": recommendation["primary_method"],
        "warnings": "; ".join(item["detail"] for item in warnings),
        "errors": "; ".join(item["detail"] for item in errors),
    }
    csv_path.write_text(csv_text([row], row.keys()), encoding="utf-8-sig")
    return {
        "ok": payload["ok"],
        "json_path": json_path.as_posix(),
        "csv_path": csv_path.as_posix(),
        "recommendation": recommendation,
        "warnings": warnings,
        "errors": errors,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--question", required=True)
    parser.add_argument("--outcome", "--outcome-type", dest="outcome_type", required=True)
    parser.add_argument("--groups", "--group-count", dest="group_count", required=True, type=int)
    parser.add_argument("--paired", action="store_true")
    parser.add_argument("--repeated", action="store_true")
    parser.add_argument("--normality", default="unknown")
    parser.add_argument("--sample-size-per-group", type=int, default=None)
    parser.add_argument("--predictor-type", default="")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def _print_human(result: dict[str, object], output: TextIO) -> None:
    status = "PASS" if result["ok"] else "NEEDS REVIEW"
    recommendation = result["recommendation"]
    print(f"Statistical method triage: {status}", file=output)
    print(f"Primary method: {recommendation['primary_method']}", file=output)
    print(f"Report: {result['json_path']}", file=output)
    for item in result.get("warnings", []):
        print(f"WARN: {item['detail']}", file=output)
    for item in result.get("errors", []):
        print(f"ERROR: {item['detail']}", file=output)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None, stderr: TextIO | None = None) -> int:
    output = stdout if stdout is not None else sys.stdout
    error_output = stderr if stderr is not None else sys.stderr
    args = build_parser().parse_args(argv)
    try:
        result = select_and_write(
            args.project,
            question=args.question,
            outcome_type=args.outcome_type,
            group_count=args.group_count,
            paired=args.paired,
            repeated=args.repeated,
            normality=args.normality,
            sample_size_per_group=args.sample_size_per_group,
            predictor_type=args.predictor_type,
            strict=args.strict,
        )
    except (OSError, ValueError, UnicodeError) as exc:
        print(f"stats_method_selector failed: {exc}", file=error_output)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2), file=output)
    else:
        _print_human(result, output)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
