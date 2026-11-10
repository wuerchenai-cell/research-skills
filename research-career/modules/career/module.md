# Module: 求职与博后追踪 (Career & Postdoc Tracker)

Status: stable. Provides `skill辅助（用户无需打开，辅助skill使用）/成果跟踪/career.csv` for the active unit.

## When to use

找教职/工业岗/博后，需要追踪 CV、多个申请、面试与 offer 时间线时。

## Artifact

`skill辅助（用户无需打开，辅助skill使用）/成果跟踪/career.csv` columns:

- `app_id`: 编号 ca-001
- `target`: 学校/公司/组
- `type`: faculty/industry/postdoc
- `status`: draft/submitted/interview/offer/rejected
- `deadline`: 申请截止
- `submitted_date`: 提交日
- `interview_date`: 面试日
- `outcome`: 结果
- `contact`: HR/PI
- `notes`: 面试准备要点

## Rules

- CV 统一在 成果/ 维护一版（docx/pdf 等可交付格式；Markdown 草稿在 skill辅助（用户无需打开，辅助skill使用）/），这里只追踪申请状态。
- interview 前在 notes 记该岗位的研究匹配点。

## Do not

- 不要把推荐信/敏感材料散落；统一收 成果/ 并控制可见性。
- 不要漏记 interview_date——面试差旅要提前排。

