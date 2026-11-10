---
name: research-verify
description: Use when the user wants to verify a technical judgment, datasheet parameter, derivation, or experimental claim. Focuses on parameter checks, technical derivation, and a minimal validation plan. Does not replace implementation, EDA, statistics, or experiment logging tools.
---

# Research Verify

Verify a technical judgment, datasheet parameter, derivation, or experimental claim. Check parameters, reconstruct derivations, and propose a minimal validation plan.

## Non-negotiable rules

1. Separate source-stated parameters, calculations, inferences, and unresolved guesses.
2. Never invent datasheet values, device parameters, tolerances, or numerical results.
3. Verify parameters against the original datasheet or official document.
4. Check units, dimensions, and boundary conditions for every equation.
5. Mark what is proven, what is derived, and what still needs testing.
6. Keep the user responsible for final engineering and safety decisions.

## Task router

| User goal | Primary mode | Load |
|---|---|---|
| Check a datasheet parameter or tolerance | parameter-check | references/verify-params.md |
| Reconstruct a technical derivation | derivation-check | references/verify-derivation.md |
| Plan a minimal test to confirm a claim | minimal-validation | references/verify-minimal.md |

## Universal workflow

1. Identify the technical claim and its original evidence.
2. Extract and check parameters, units, and constraints.
3. Reconstruct the derivation step by step.
4. Propose a minimal validation plan with measurable outcomes.
5. Mark what remains unverified.

## Material intake

- A datasheet, official document, experimental log, code result, or derivation.
- The specific technical claim to verify.

Do not require project initialization or library scan. Use existing experiment-log, spreadsheet, or statistics skills for implementation and analysis.

## Scripts

- scripts/verify_params.py: check parameter values, units, and constraints.
- scripts/unit_check.py: basic unit and dimension consistency check.

## References

- references/verify-params.md
- references/verify-derivation.md
- references/verify-minimal.md

## Completion criteria

Consider a verify task complete only when:
- parameters are checked against the original source;
- derivations are reconstructed with assumptions stated;
- a minimal validation plan is proposed;
- unverified items are clearly marked.
