# Statistical Method Selection

## Boundary

This is a triage checklist, not statistical analysis. It helps choose a defensible starting method from outcome type, group count, pairing, repeated measures, normality notes, and small-sample cautions. It must not be used to optimize p values after looking at results.

Use it when the user asks "该用什么统计方法", "方差分析还是 t 检验", or similar. If the design, outcome, or sampling structure is unclear, return `needs-human-review` and ask for the missing design facts.

## Closed Loop

Run:

```bash
python scripts/stats_method_selector.py --project <项目根> --question "..." --outcome continuous --groups 2
```

Outputs stay under:

- `skill辅助（用户无需打开，辅助skill使用）/analysis/statistics-method-selection.json`
- `skill辅助（用户无需打开，辅助skill使用）/analysis/statistics-method-selection.csv`

The report records:

- primary candidate method;
- rationale;
- assumption checks;
- effect size/reporting requirements;
- warnings or `needs-human-review` errors.

## Gate Rules

- Missing or unknown outcome type cannot be treated as final advice.
- Small binary samples prefer exact methods and warn.
- Continuous two-group unpaired comparisons default to Welch t-test unless the design says otherwise.
- Repeated/paired designs must not be silently collapsed into independent tests.
- The answer must state assumptions and effect-size reporting, not just name a p-value test.

## Evidence Boundary

This route sits in Output Layer + Gate Layer. It may guide analysis planning, but any manuscript claim still needs the Evidence Layer: data source, analysis log, exclusion record, and figure/table provenance.
