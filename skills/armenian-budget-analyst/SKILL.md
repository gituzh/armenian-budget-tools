---
name: armenian-budget-analyst
description: "Analyze parsed Armenian budget CSVs: inspect year and source availability, compare allocations and spending across ministries, programs, and subprograms, and create source-cited tables, charts, and reports from data/processed."
---

# Armenian Budget Analyst

Use this skill for analysis of parsed Armenian budget data in `data/processed`.

## Start here

1. Resolve the data root:
   - use `ARMENIAN_BUDGET_DATA_PATH` if set
   - otherwise use repo `data/processed`
   - if neither exists, fail clearly
2. Run `scripts/data_availability.py` first to inventory datasets by year and source type.
3. Pick the source type intentionally, then state the aggregation grain and metric before computing anything.

## Choose the right dataset

- `BUDGET_LAW`: allocation data
- `SPENDING_Q1234`: full-year actuals when available
- `SPENDING_Q1`, `SPENDING_Q12`, `SPENDING_Q123`: year-to-date data only; label partial coverage explicitly
- `MTEP`: projection and planning data only, not factual spending

## Required workflow

1. Inventory available files first.
2. Name the exact source files used.
3. State the grain explicitly: `state_body`, `program`, or `subprogram`.
4. State the metric explicitly: `*_total`, `*_annual_plan`, `*_rev_annual_plan`, `*_actual`, or `*_total_y0/y1/y2`.
5. Keep parsed-data facts separate from any external denominator, manual classification, or policy interpretation.
6. Add provenance to every output:
   - inline `Sources & derivation` for text and table answers
   - sidecar JSON `<artifact_filename>.provenance.json` for generated files

## Hard rules

- Do not mix program-level and subprogram-level numbers silently.
- Do not sum repeated `program_*` or `state_body_*` totals across every subprogram row; deduplicate parent totals before aggregating above `subprogram` grain.
- Do not compare partial-year actuals with full-year actuals without labeling the mismatch.
- Do not substitute a missing factual series with an estimate, forecast, expected value, or external hardcoded number unless the user explicitly asks for that.
- Do not treat `MTEP` as executed spending.
- Do not use `assets/` as a live data mirror.
- If a mapping is manual or topic-specific, state it explicitly in `filters_or_mappings`.
- If a topic mapping is reused across years or outputs, keep it as a separate explicit mapping artifact or script rather than implying it as a native dataset fact.

## References

- `references/datasets.md`: dataset semantics and comparability rules
- `references/analysis.md`: repeatable output patterns and provenance contract
- `references/examples.md`: short worked examples, including one R&D example
