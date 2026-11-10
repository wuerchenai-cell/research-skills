# Library: Incremental Index

## Purpose

Build or update an incremental index of a folder without moving originals.

## Workflow

1. Scan the folder for files (PDF, DOCX, MD, TXT).
2. Record filename, size, mtime, and a first-line title.
3. Skip already-indexed files by hash or mtime.
4. Report newly added, changed, and unidentified files.

## Quality gates

- Originals are untouched.
- The index records source path and identity hints.
- Skipped files are justified.

## Common pitfalls

- Moving or renaming user files.
- Indexing without recording the source path.
