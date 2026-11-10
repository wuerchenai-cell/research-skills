# Module: 基金与奖学金申请 (Grant & Fellowship Tracker)

Status: stable. Provides `skill辅助（用户无需打开，辅助skill使用）/成果跟踪/grant-tracker.csv` for the active unit.

## When to use

申国自然/省基金/校长奖学金/CSC 等，需要追踪 draft→submit→review→resubmit→awarded 与多轮 deadline 时。

## Artifact

`skill辅助（用户无需打开，辅助skill使用）/成果跟踪/grant-tracker.csv` columns:

- `grant_id`: 编号 gt-001
- `name`: 基金/奖学金名
- `type`: 国自然/省基/奖学金/CSC
- `status`: draft/submitted/under_review/resubmit/awarded/rejected
- `deadline`: 申报截止
- `submit_date`: 提交日
- `resubmit_round`: 第几次 resubmit(0=首申)
- `amount`: 金额或空
- `notes`: 评审意见摘要

## Rules

- resubmit 必须记 resubmit_round 与上轮意见，避免重复踩坑。
- deadline 是硬约束，提前 2 周标红自查材料清单。

## Do not

- 不要把申请书正文写进 CSV；正文在 成果/，这里只追踪节点。
- 不要混用不同基金的 deadline——各自成行。

