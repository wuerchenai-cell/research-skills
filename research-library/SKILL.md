---
name: research-library
description: Use when the user wants to organize a folder of PDFs, recover a previously read source, or manage an existing literature library. Provides incremental indexing, deduplication suggestions, and note-to-source retrieval. Optional: the other five skills work without a library.
---

# Research Library

Organize a folder of PDFs, recover a previously read source, or manage an existing literature library. Provide incremental indexing, deduplication suggestions, and note-to-source retrieval.

## Non-negotiable rules

1. Never move, rename, or delete user originals without explicit user request.
2. Indexes and notes are recall aids; the original source remains the authority.
3. Never invent bibliographic records, DOIs, or file locations.
4. Verify identity (title, authors, year, DOI/version) before claiming two files are duplicates.
5. Preserve the user's existing folder layout and naming habits.
6. Mark indexed, missing, duplicate, and unidentified files honestly.

## Task router

| User goal | Primary mode | Load |
|---|---|---|
| Index a folder of PDFs | incremental-index | references/library-index.md |
| Suggest duplicates | dedup-suggestion | references/library-dedup.md |
| Find a previously read source or note | retrieve | references/library-retrieve.md |

## Universal workflow

1. Identify the target folder or existing library.
2. Build or update an incremental index without moving originals.
3. Suggest duplicates with confidence and verification steps.
4. Retrieve a source or note by keyword, title, or DOI.
5. Keep the index as a working artifact, not a replacement for the source.

## Material intake

- A folder of PDFs/DOCX/MD, an existing catalog, or an existing literature library.
- A recovery keyword, title, DOI, or reading note.

Do not require project initialization for other skills. This skill is optional; study, read, find, compare, and verify do not depend on it.

## Scripts

- scripts/index_folder.py: incremental index of a folder (filename, size, mtime, first-line title).
- scripts/dedup_candidates.py: suggest duplicate candidates by title similarity and hash.
- scripts/find_note.py: search notes by keyword.

## References

- references/library-index.md
- references/library-dedup.md
- references/library-retrieve.md

## Completion criteria

Consider a library task complete only when:
- originals are untouched unless explicitly changed;
- the index is updated and verifiable;
- duplicate suggestions carry verification steps;
- retrieval returns matching sources or notes, not invented records.
