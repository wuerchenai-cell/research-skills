# Response Letter Workflow

## Boundary

Reviewer response work must stay tied to the actual reviewer comment, manuscript change, and evidence source. This workflow creates a support-only response matrix and draft; it does not invent experiments, promise unsupported changes, or treat an addressed comment as resolved without evidence.

Use it when the user asks "写审稿回复", "response letter 怎么写", or "逐条回复审稿意见".

## Closed Loop

Run:

```bash
python scripts/response_letter.py init --project <项目根>
python scripts/response_letter.py add-comment --project <项目根> --comment-id r1c1 --reviewer "Reviewer 1" --comment "..." --response-summary "..." --evidence-source "manuscript section 3"
python scripts/response_letter.py lint --project <项目根> --strict
python scripts/response_letter.py export-draft --project <项目根>
```

Outputs stay under:

- `skill辅助（用户无需打开，辅助skill使用）/rebuttal/response-matrix.csv`
- `skill辅助（用户无需打开，辅助skill使用）/rebuttal/response-matrix.json`
- `skill辅助（用户无需打开，辅助skill使用）/drafts/response-letter-draft.md`

Promote to DOCX only after lint and evidence checks pass.

## Gate Rules

- `comment_id` must be unique.
- Reviewer and comment text are required.
- Status must be one of `open`, `addressed`, `needs_evidence`, `declined_with_reason`, `needs_human_review`.
- Addressed comments without `evidence_source` are warnings; strict mode makes them errors.
- Missing response summary is a warning; strict mode makes it an error.

## Evidence Boundary

Every response that claims a change, result, or limitation should point to the revised manuscript location or project evidence. Claim verification still belongs to the Evidence Layer.
