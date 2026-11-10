# Library: Retrieve

## Purpose

Find a previously read source or note by keyword, title, or DOI.

## Workflow

1. Search the index and notes by keyword, title, or DOI.
2. Return matching source paths and note locations.
3. Verify the returned source matches the request.
4. Mark missing or unidentified results.

## Quality gates

- Results link to actual sources or notes.
- Missing results are marked, not invented.
- The original source is preferred over a note.

## Common pitfalls

- Returning a note without the original source.
- Inventing file locations.
