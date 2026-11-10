# Library: Dedup Suggestion

## Purpose

Suggest duplicate candidates without deleting anything.

## Workflow

1. Compute a content hash and a normalized title for each file.
2. Compare hashes and title similarity.
3. Report candidate duplicates with confidence and verification steps.
4. Do not delete or merge anything automatically.

## Quality gates

- Duplicates are suggestions, not automatic actions.
- Each suggestion includes verification steps.
- Identity is confirmed before claiming duplicates.

## Common pitfalls

- Deleting files automatically.
- Treating different versions as duplicates without checking.
