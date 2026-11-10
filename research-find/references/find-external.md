# Find — External Search Protocol

This reference governs how `research-find` reaches beyond local files. It exists to
keep discovery cheap and honest: an external hit is a pointer, not a summary.

## Default order

1. **MCP path** — delegate to the installed `nature-academic-search` skill. It is the
   primary external channel and exposes coordinated workflows (multi-source search,
   citation verification, reference management).
2. **No-MCP path** — if the MCP server is unavailable, run
   `nature-academic-search/scripts/academic_search.py` directly. It queries OpenAlex
   (free, no API key, indexes CrossRef/PubMed/arXiv) and emits JSON records.
3. **Local path** — if external tools are unavailable or the user restricts the search
   to their own materials, run `research-find/scripts/find_local.py`.

## Query construction

- Start from the user's topic, research question, or named paper.
- Extract 2–4 topical keywords; expand with synonyms when results are thin.
- Add constraints only when stated: year range, language, venue type, open access, quantity.
- Record the query string so the search is reproducible.

## What to do with each external result

- Treat the record as a candidate pointer, not a claim about its content.
- Verify identity before recommending (see the two levels below).
- State access level honestly: full text, abstract only, metadata only, or unknown.
- Attach a recommendation reason tied to the user's goal (introduction, key paper, survey, method, benchmark).
- Propose a reading order: foundational → key method → recent advances → survey.

## Identity verification (two distinct levels)

`identity_check.py` distinguishes two levels; never collapse them:

- **Syntax check** (default): field format only — title non-empty, DOI
  format, year format. A syntax pass says nothing about whether the
  literature actually exists or whether the metadata matches it.
- **Authoritative check** (`--authoritative`, requires network): the DOI
  is looked up in Crossref and the title/year are compared with the
  authoritative record. Outcomes: match, partial, mismatch, or unverified,
  with a per-field result (matched / mismatched / unavailable).

A field the record does not carry — for example the user supplies a year
but the record has no issued date — is reported as **unavailable**, never
as consistent. In that case the overall outcome is *partial* (exit code 4):
nothing mismatched, but not everything could be verified. Do not present a
partial result as a full identity match.

If the authoritative lookup cannot be performed (no network, rate-limited,
record missing), report **unverified** (exit code 3) and do not present the
candidate as identity-verified. The syntax check alone must never be used
as evidence that a work exists or that its metadata is correct.

## Failure handling

- If the MCP path fails, report the specific tool failure and continue with the no-MCP path.
- If OpenAlex is rate-limited or unreachable, report it and fall back to local search; mark external search as pending rather than inventing candidates.
- Never fabricate DOIs, authors, titles, venues, years, or access levels.

## Access-level honesty

- Full text: available locally or reachable through the user's subscription.
- Abstract only: only metadata/abstract is retrievable.
- Metadata only: identity known, content not retrieved.
- Unknown: do not guess; mark it and let the user decide.

## Completion criteria

A find task with external search is complete only when:

- external candidates are identity-checked and access levels are stated;
- each recommendation has a reason tied to the user's goal;
- a reading order is proposed;
- no candidate is claimed to have been read in depth;
- failed external sources are reported, not silently dropped.
