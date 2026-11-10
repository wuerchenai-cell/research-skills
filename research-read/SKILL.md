---
name: research-read
description: Use when the user wants to read a specific paper, PDF, or document. Extracts text, locates key sections, explains formulas, tables, and figures, and answers questions about the content. Focuses on the actual document at hand.
---

# Research Read

Read a specific paper, PDF, or document. Extract text, locate key sections, explain formulas, tables, and figures, and answer questions about the content.

## Non-negotiable rules

1. Check the user's premise before building on it.
2. Separate source-stated facts, calculations, inferences, and unresolved guesses.
3. Never invent papers, authors, DOIs, quotations, citations, datasets, numerical results, or device parameters.
4. Never claim to have read a full paper or document unless the full relevant content was successfully accessed.
5. Verify critical numbers, equations, tables, figure interpretations, and timing values against the original page.
6. Treat abstracts, search snippets, and secondary summaries as discovery aids rather than final evidence.
7. Attach evidence to claims before drafting polished conclusions.
8. Keep the user responsible for final scientific, engineering, ethical, legal, and submission decisions.

## Task router

| User goal | Primary mode | Load |
|---|---|---|
| Read a paper or PDF | paper-reading | references/read-paper.md |
| Explain a formula | formula-explanation | references/read-formula.md |
| Interpret a figure or table | figure-table | references/read-figure.md |
| Answer questions about a document | qa | references/read-qa.md |

## Universal workflow

1. Identify the document and the user's question.
2. Extract text from the document.
3. Locate the relevant section, page, equation, or figure.
4. Explain the content clearly and grounded in the original.
5. Attach evidence to claims.

## Paper reading

### Identity check

Before reading:
1. Verify title, authors, venue, year, and version.
2. Check for errata, corrections, or retractions.
3. Note the access level: full text, abstract only, or metadata only.

### Deep reading

For each important claim:
1. Locate the exact page, section, table, or figure.
2. Quote the relevant sentence or passage.
3. Explain the claim in plain language.
4. Connect to prerequisites and context.
5. Identify assumptions and limitations.

### Formula explanation

For each formula:
1. State the variables and their definitions.
2. Explain the physical or mathematical meaning.
3. Derive the formula step by step if needed.
4. Discuss assumptions and boundary conditions.
5. Provide a numeric example.

### Figure interpretation

For each figure:
1. Describe what the figure shows.
2. Identify axes, labels, and legends.
3. Explain the trend or pattern.
4. Connect to the text and results.
5. Discuss limitations or alternative interpretations.

## Material intake

- If the user provides a file (PDF, DOCX, TXT, MD), read it directly.
- If the user provides a path, read that file.
- If the user provides nothing, ask for the material or proceed with general knowledge.

Do not require project initialization, library scan, or profile setup. Do not run full workspace validation. Do not create project-local memory unless the user explicitly asks.

## Scripts

- scripts/read_extract.py: extract text from PDF/DOCX/TXT/MD for reading.
- scripts/read_locate.py: locate key sections, formulas, and figures.

## References

- references/read-paper.md
- references/read-formula.md
- references/read-figure.md
- references/read-qa.md

## Completion criteria

Consider a reading task complete only when:
- the relevant content is located and explained;
- the explanation is grounded in the original document;
- assumptions and limitations are stated;
- the user can verify the key claims.
