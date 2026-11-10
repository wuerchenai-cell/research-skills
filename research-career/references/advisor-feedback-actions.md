# Advisor Feedback Actions

## Boundary

Advisor or meeting feedback is often ambiguous. This workflow converts feedback into a support-only action ledger, but it does not decide scientific truth or overwrite project priorities. Ambiguous tasks remain `open` until the user confirms owner, due date, and evidence source.

Use it when the user asks to turn "组会反馈", "导师意见", or "反馈" into action items.

## Closed Loop

Run:

```bash
python scripts/advisor_feedback_actions.py init --project <项目根>
python scripts/advisor_feedback_actions.py add --project <项目根> --feedback-id fb001 --text "补一张图；重写方法贡献" --owner me --due 2026-09-10 --source 组会
python scripts/advisor_feedback_actions.py lint --project <项目根>
```

Outputs stay under:

- `skill辅助（用户无需打开，辅助skill使用）/requirements/advisor-feedback-actions.csv`
- `skill辅助（用户无需打开，辅助skill使用）/requirements/advisor-feedback-actions.json`

## Gate Rules

- `action_id` must be unique.
- `feedback_id` and action text must exist.
- Status must be one of `open`, `in_progress`, `done`, `blocked`, `snoozed`.
- Missing owner or due date is a warning; in strict mode it is an error.
- Invalid due date is an error.

## Memory Boundary

After meaningful updates, summarize only the durable next action into project memory or `state/next-actions.md`. Do not copy long meeting transcripts into memory.
