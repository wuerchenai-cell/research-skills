---
name: research-study
description: Use when the user wants to understand a concept, formula, method, or technical term. Provides concept explanations, prerequisite diagnosis, step-by-step derivations, worked examples, counterexamples, and understanding checks. Focuses on the user's learning goal and the actual material at hand.
---

# Research Study

Help the user understand a concept, formula, method, or technical term. Explain clearly, connect to prerequisites, and verify the user can reproduce the key reasoning.

## Non-negotiable rules

1. Check the user's premise before building on it.
2. Separate facts, calculations, inferences, and unresolved guesses.
3. Never invent papers, DOIs, quotations, citations, datasets, numerical results, or device parameters.
4. Verify critical numbers, equations, tables, and figure interpretations against the original page or official document.
5. Preserve negative results, anomalies, exclusions, failed experiments, and uncertainty.
6. Keep the user responsible for final scientific, engineering, ethical, legal, and submission decisions.

## Task router

| User goal | Primary mode | Load |
|---|---|---|
| Understand a concept or term | concept-explanation | references/study-concept.md |
| Derive a formula or theorem | derivation | references/study-derivation.md |
| Explain a method or algorithm | method-explanation | references/study-method.md |
| Diagnose prerequisite gaps | prerequisite-diagnosis | references/study-prerequisites.md |
| Test understanding with examples | understanding-check | references/study-check.md |

## Universal workflow

1. Identify the user's goal: understand, derive, apply, or diagnose.
2. Check available materials: user-provided file, path, or none.
3. Start with a plain-language explanation, then deepen as needed.
4. Connect to prerequisites and boundary conditions.
5. Provide a worked example or counterexample.
6. Verify the user can reproduce the key reasoning.

## Study modes

### Concept explanation

Build:
1. one-sentence definition;
2. motivating problem;
3. assumptions and boundary conditions;
4. mechanism or derivation;
5. canonical example;
6. counterexample or failure case;
7. connections to neighboring concepts;
8. one retrieval question;
9. one transfer problem.

### Derivation

For each derivation:
1. state the goal and known conditions;
2. list assumptions and constraints;
3. reconstruct the derivation step by step;
4. check units, boundary conditions, and limiting cases;
5. provide a numeric example if useful.

### Method explanation

For each method:
1. state the problem it solves;
2. describe the core idea;
3. explain the key steps;
4. discuss assumptions, failure modes, and alternatives;
5. provide a minimal example.

### Prerequisite diagnosis

1. identify the target capability: explain, derive, calculate, implement, critique, or apply;
2. identify prerequisite concepts;
3. classify each prerequisite as secure, fragile, or missing;
4. start at the first missing dependency.

### Understanding check

1. ask the user to explain the concept in their own words;
2. provide a transfer problem;
3. ask the user to identify assumptions and boundary conditions;
4. provide a counterexample or failure case.

## Material intake

- If the user provides a file (PDF, DOCX, TXT, MD), read it directly.
- If the user provides a path, read that file.
- If the user provides nothing, ask for the material or proceed with general knowledge.

Do not require project initialization, library scan, or profile setup. Do not run full workspace validation. Do not create project-local memory unless the user explicitly asks.

## Scripts

- scripts/study_extract.py: extract text from PDF/DOCX/TXT/MD for study.

## References

- references/study-concept.md
- references/study-derivation.md
- references/study-method.md
- references/study-prerequisites.md
- references/study-check.md

## Completion criteria

Consider a study task complete only when:
- the user understands the concept, formula, or method;
- the explanation is grounded in the available material;
- assumptions and limitations are stated;
- the user can reproduce the key reasoning.
