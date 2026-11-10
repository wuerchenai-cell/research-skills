---
name: research-find
description: Use when the user wants to find candidate materials for a topic or research question. Returns identity-checked candidates with recommendation reasons, access levels, and a reading order. Prefers existing academic-search tools; does not claim retrieved sources have been deeply read.
---

# Research Find

Find candidate materials for a topic or research question. Verify identity, give recommendation reasons, mark access level, and propose a reading order.

## Non-negotiable rules

1. Check the user's premise and constraints before searching.
2. Separate discovery from reading: a candidate is a pointer, not a summary of its content.
3. Never invent papers, DOIs, authors, venues, versions, or access levels.
4. Verify identity (title, authors, venue, year, DOI/version) before recommending.
5. State access level honestly: full text, abstract only, metadata only, or not accessible.
6. Attach a recommendation reason and a reading order that fits the user's goal.
7. Keep the user responsible for final scientific, engineering, ethical, legal, and submission decisions.

## Task router

| User goal | Primary mode | Load |
|---|---|---|
| Find an introduction or key paper on a topic | candidate-discovery | references/find-identity.md |
| Check what a source actually is | identity-check | references/find-identity.md |
| Rank or justify candidates | recommendation | references/find-recommend.md |
| Plan what to read first | reading-order | references/find-order.md |
| Check whether full text is reachable | access-level | references/find-access.md |
| Find external literature beyond local files | external-search | references/find-external.md |

## Universal workflow

1. Identify the topic, constraints, and target (introduction, key paper, survey, method, etc.).
2. Search local files and available academic tools for candidates.
3. Verify each candidate's identity and access level.
4. Give a recommendation reason per candidate.
5. Propose a reading order based on the user's goal.
6. Do not claim any candidate has been read in depth.

## Material intake

- Local files, folders, existing catalogs, or citation exports.
- Topic, keywords, DOI, title, or research question.
- Constraints: language, venue type, year range, access level, quantity.

Do not require project initialization, library scan, or profile setup. If an academic-search tool is available and authorized, use it; otherwise search local materials and mark external search as pending.

## External search integration

Prefer the installed `nature-academic-search` skill for external literature discovery. It uses MCP tools (PubMed, CrossRef, arXiv, Scopus, ScienceDirect) and falls back to a dependency-free OpenAlex script when MCP is unavailable.

Fallback order for external candidates:

1. **MCP path** — delegate to `nature-academic-search` with the user's topic; use `search_papers`, `get_paper_by_id`, or `get_citation` as appropriate.
2. **No-MCP path** — run `nature-academic-search/scripts/academic_search.py` directly (OpenAlex, no API key) for topic/author/year/sort queries.
3. **Local path** — run `scripts/find_local.py` against the user's folders.

Treat every external result as a candidate pointer: verify identity with `identity_check.py` (syntax by default; `--authoritative` checks the DOI against Crossref when network is available), state access level, and never claim it has been read in depth. Details and query templates: `references/find-external.md`.

## Scripts

- scripts/find_local.py: scan local folders for candidate files matching keywords.
- scripts/identity_check.py: field-format (syntax) check of title/DOI/year/venue; with `--authoritative` it verifies the DOI against Crossref and reports match / partial / mismatch / unverified with per-field outcomes (matched / mismatched / unavailable). Exit codes: 0 pass, 1 mismatch or syntax issue, 3 unverified (lookup unavailable), 4 partial (some supplied fields could not be verified).
- External search (delegate or fallback): see External search integration and references/find-external.md.

## References

- references/find-identity.md
- references/find-recommend.md
- references/find-order.md
- references/find-access.md
- references/find-external.md

## Completion criteria

Consider a find task complete only when:
- candidates are identity-checked and access levels are stated;
- each recommendation has a reason tied to the user's goal;
- a reading order is proposed;
- no candidate is claimed to have been read in depth.
