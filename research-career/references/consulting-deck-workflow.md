# Consulting Deck Workflow(咨询式演示:显式选择的三种模式)

方法论来源:https://github.com/Pikapika260214/rw-consulting-ppt(MIT,已登记;
仅借鉴方法论,不 vendor 代码)。**默认模式仍是 `native_academic`**——
只有用户明确要求"咨询式/图片型 PPT"时才启用其他模式。

## 三种输出模式

| 模式 | 适用 | 关键约束 |
|---|---|---|
| `native_academic`(默认) | 学术汇报、组会、答辩 | 图表/表格/公式必须是原生对象;`--strict` 下关键对象只有截图即 error |
| `consulting_image_only` | 给领导/评审的决策汇报(显式选择) | 整页图片可接受,但必须标记 `image_only`;可搜索性/可访问性/可编辑性弱;QA 最终状态最多 `needs-human-review` |
| `hybrid_selective_editable` | 混合需求 | 必须输出每页 editability matrix,绝不笼统声称完全可编辑 |

图片中的表格、图表、公式**不能算** Word/PowerPoint 原生对象;
可编辑化路径依赖 OCR 与额外包,不自动安装、不承诺完美恢复。

## 工作流

### 1. Alignment contract(init)

```powershell
python -B scripts/consulting_deck_blueprint.py init --project <project> \
  --deck-id deck-01 --audience "课题组例会" \
  --use-case "汇报进展并决策下一步实验" [--mode consulting_image_only]
```

先对齐 audience / use case / detail level / style / output mode / language,
再讲故事线。缺任一项 lint 直接 error。

### 2. Blueprint + 每页 governing message(add-page)

```powershell
python -B scripts/consulting_deck_blueprint.py add-page --project <project> \
  --deck-id deck-01 --page-id S01 --title "研究背景" \
  --message "弱光检测是本课题的核心瓶颈" --proof-object chart --evidence E-001
```

- 每页**只有一个** governing message。
- proof object 非 `none` 时必须有 evidence_refs,或显式 `--label illustrative|forward`。
- claim–evidence–visual 三者映射进 blueprint,全 deck 保持一致性。

### 3. 样页 gate(approve-sample)

批量生成前必须先做样页并经用户确认:`approve-sample` 置 `sample_gate=approved`;
未批准时 `export` 直接 blocked(exit 1)。

### 4. 导出 briefs(export)

```powershell
python -B scripts/consulting_deck_blueprint.py export --project <project> --deck-id deck-01
```

briefs 只写辅助区 `presentation/consulting-deck/slide-briefs/`;
实际渲染仍走 Output Layer 既有链(deliverable_factory 等),不建平行交付链。

### 5. 最终 QA(final_presentation_qa)

```powershell
python -B scripts/final_presentation_qa.py --pptx <file.pptx> --project <project> \
  --mode <mode> [--strict] [--json]
```

检查:zip/核心 XML、slide 尺寸与数量、图片 alt text、媒体 relationship、
图片 DPI、image-only 比例、原生 chart/table/equation 计数、残留草稿标记、
每页 editability(hybrid)。QA JSON/CSV 只进辅助区;
无渲染视觉复核时状态一律 `needs-human-review`,不得声称 final-ready。
