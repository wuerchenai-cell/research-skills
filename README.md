# research-skills

研究生科研学习 Skill 合集（AI 无关、文件夹式），从旧单体 `reviewing-research-literature` 拆分而来。

## 包含的 Skill（7 个）

| Skill | 用途 |
|---|---|
| `research-study` | 学习辅导：概念、公式、推导、反例、理解检查 |
| `research-read` | 单篇研读：PDF 提取（保留页边界）、条件抽取 |
| `research-find` | 文献检索：本地检索 + 联网检索 + 身份核验（语法/权威两级） |
| `research-compare` | 多篇比较：条件、结论、跨论文对照 |
| `research-verify` | 参数/单位校验：拒绝 NaN/Inf/负频等非法输入 |
| `research-library` | 资料库：增量索引、笔记检索、去重（完整流式哈希） |
| `research-career` | 生涯规划：advisor-feedback、response-letter、submission-package、stats-method、consulting-deck |

## 设计约束

- 不依赖网络时全部走本地实现；联网检索为可选回退（MCP + OpenAlex）。
- 只追加、不覆盖用户资料；`.workbuddy/`、`.codex/` 等 agent 私有目录一律不扫描。
- 提示词注入防御：指令层级 / 不可信内容标记 / 敏感操作确认门。
- 详细约定与验收历史见仓库根目录之外的开发记录（未包含在本上传包内）。

## 安装（Codex 等 agent）

复制 `research-<name>/` 到 agent 的 skills 目录即可；每个 skill 自包含，互相不依赖。

## 上传范围说明（2026-11-10）

- 上传包 `tmp/research-skills-upload/` 仅含上述 7 个 skill，共 76 个文件、约 314 KB。
- 不包含：历史文档、独立审查报告、验收 JSON、备份、临时构建产物、用户论文/笔记资料。
