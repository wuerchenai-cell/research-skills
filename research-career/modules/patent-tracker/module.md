# Module: 专利申报追踪 (Patent Tracker)

Status: stable. Provides `skill辅助（用户无需打开，辅助skill使用）/成果跟踪/patent-tracker.csv` for the active unit.

## When to use

把科研成果转专利，需要追踪 受理→实审→答复→授权/驳回 各阶段、答复期限与权利要求时。

## Artifact

`skill辅助（用户无需打开，辅助skill使用）/成果跟踪/patent-tracker.csv` columns:

- `patent_id`: 编号 pt-001
- `title`: 专利名
- `type`: 发明/实用新型
- `status`: 受理/实审/答复/授权/驳回
- `filing_date`: 申请日
- `office_action_date`: 审查意见日
- `response_due`: 答复期限
- `claims_ref`: 权利要求书路径
- `notes`: 审查要点

## Rules

- office_action 必须填 response_due，超期视为撤回。
- 答复期限常比想象紧，建议提前 1 个月备答复稿。

## Do not

- 不要把权利要求书正文塞进 CSV；正文在 成果/，这里只追踪阶段。
- 不要遗漏 '答复' 状态——很多专利死在没及时答复。

