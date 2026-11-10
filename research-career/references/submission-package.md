# Submission Package

## Boundary

This is a venue checklist adapter. It helps ensure core files and required statements are not forgotten, but it does not replace the target journal or conference instructions. Different venues may require different cover letter, highlights, graphical abstract, conflict-of-interest, author contribution, data/code availability, ethics, and supplement formats.

Use it when the user asks for a "投稿材料包", "cover letter", "highlights", "graphical abstract", "补充材料", or "data availability".

## Closed Loop

Run:

```bash
python scripts/submission_package.py --project <项目根> --venue "Target Journal" --manuscript <docx或pdf> --cover-letter <docx或pdf> --data-availability-statement "..."
```

Outputs stay under:

- `skill辅助（用户无需打开，辅助skill使用）/logs/submission-package/submission-package-audit.json`
- `skill辅助（用户无需打开，辅助skill使用）/logs/submission-package/submission-package-audit.csv`

User-openable deliverables may still live in `成果/`, but QA ledgers never do.

## Gate Rules

- Missing manuscript is an error.
- Referenced package files that do not exist are errors.
- Missing cover letter, data availability, COI, or author contribution statements are warnings by default; strict mode may escalate core omissions.
- DOCX final manuscripts should also run `validate_deliverable.py`, `final_docx_citation_audit.py`, and `final_manuscript_qa.py`.
- DOI is not mandatory for every source; references need DOI or a no-DOI reason.

## Human Review

Before submission, the user must still check venue limits, author order, affiliations, ethics/consent wording, figure permissions, and any journal-specific portal fields.
