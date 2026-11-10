---
name: research-compare
description: Use when the user wants to compare several papers, methods, or sources on the same question. Builds a condition-aware comparison of hypotheses, methods, experiment conditions, costs, and conclusions. Does not automatically turn into a full systematic review.
---

# Research Compare

Compare several papers, methods, or sources on the same question. Build a condition-aware comparison and explain why conclusions differ under different conditions.

## Non-negotiable rules

1. Compare on the user's question, not on paper count or prestige.
2. Separate source-stated facts, calculations, inferences, and unresolved guesses.
3. Never invent papers, DOIs, authors, datasets, numerical results, or device parameters.
4. Record conditions for every numeric or categorical claim (array type, N, K, L, SNR, bandwidth, etc.).
5. Preserve contradictory evidence instead of averaging or voting.
6. Verify critical numbers, equations, and figure interpretations against the original page.
7. Keep the user responsible for final scientific, engineering, ethical, legal, and submission decisions.

## Task router

| User goal | Primary mode | Load |
|---|---|---|
| Compare methods or architectures | method-comparison | references/compare-setup.md |
| Explain why conclusions differ | findings-comparison | references/compare-findings.md |
| Trace each claim to its source | evidence-mapping | references/compare-evidence.md |

## Universal workflow

1. Identify the comparison question and the selected sources.
2. Extract each source's hypothesis, method, conditions, cost, and conclusion.
3. Build a condition-aware comparison table.
4. Explain differences in conclusions by conditions, not by aggregating.
5. Mark unresolved conflicts and missing full-text claims.
6. Do not convert into a systematic review unless explicitly requested.

## Material intake

- User-selected papers, PDFs, notes, or an existing catalog.
- A comparison question and any constraints.
- Existing reading notes or cards as starting points, not substitutes for the original.

Do not require project initialization, library scan, or profile setup. If a source is not available, state it and proceed with what is available.

## Scripts

- scripts/compare_rows.py: build or validate a comparison table from CSV/JSON rows.
- scripts/extract_conditions.py: extract condition keywords from extracted text.

## References

- references/compare-setup.md
- references/compare-evidence.md
- references/compare-findings.md

## Completion criteria

Consider a compare task complete only when:
- a condition-aware comparison is provided;
- each numeric claim carries its conditions;
- differences in conclusions are explained by conditions;
- contradictions and missing sources are marked, not hidden.
