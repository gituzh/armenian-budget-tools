# Datasets

## File naming and root

- Primary parsed budget datasets live in a single active parsed-data root and use `{year}_{SOURCE_TYPE}.csv`.
- GDP snapshots from `gdp-extract` use `{year}_{BUDGET_LAW|SPENDING_Q1234}_GDP.json`.
- Prefer `ARMENIAN_BUDGET_DATA_PATH` when set; otherwise use bundled `assets/data` when present; otherwise use repo `data/processed`.
- Availability varies by year. Do not assume every year has every source type. Check with `scripts/data_availability.py` first.

## Source types

| Source type | Meaning | Row grain | Primary measures |
| --- | --- | --- | --- |
| `BUDGET_LAW` | Annual allocations from the state budget law | Subprogram rows with parent totals repeated | `state_body_total`, `program_total`, `subprogram_total` |
| `SPENDING_Q1` | Q1 execution report | Subprogram rows with parent totals repeated | `*_annual_plan`, `*_rev_annual_plan`, `*_period_plan`, `*_rev_period_plan`, `*_actual` |
| `SPENDING_Q12` | Half-year execution report | Subprogram rows with parent totals repeated | `*_annual_plan`, `*_rev_annual_plan`, `*_period_plan`, `*_rev_period_plan`, `*_actual` |
| `SPENDING_Q123` | Nine-month execution report | Subprogram rows with parent totals repeated | `*_annual_plan`, `*_rev_annual_plan`, `*_period_plan`, `*_rev_period_plan`, `*_actual` |
| `SPENDING_Q1234` | Full-year execution report | Subprogram rows with parent totals repeated | `*_annual_plan`, `*_rev_annual_plan`, `*_actual` |
| `MTEP` | Mid-term expenditure program projections | Program rows only; subprogram fields are empty for compatibility | `*_total_y0`, `*_total_y1`, `*_total_y2` |
| `BUDGET_LAW_GDP` | Budget-law macro/GDP assumptions | JSON records nested under extracted tables | `target_year`, `status`, `indicator`, `unit`, `value` |
| `SPENDING_Q1234_GDP` | Spending-report macro/GDP annex values | JSON records nested under extracted tables | `target_year`, `status`, `indicator`, `unit`, `value` |

## Measure selection

- Allocation questions: start with `BUDGET_LAW`.
- Full-year execution questions: use `SPENDING_Q1234` when available.
- Partial-year execution questions: use `SPENDING_Q1`, `SPENDING_Q12`, or `SPENDING_Q123`, and label the covered period.
- Projection questions: use `MTEP`, and name the specific plan year `y0`, `y1`, or `y2`.
- GDP denominator questions: prefer parsed GDP outputs over external values when available. Use `BUDGET_LAW_GDP` for budget-law assumptions and `SPENDING_Q1234_GDP` for spending-report scenarios and actuals. Always filter by `indicator`, `target_year`, and scenario/status.

## Comparability rules

- Keep the aggregation grain consistent. If the budget side uses `program_total`, compare it to `program_actual`, not `subprogram_actual`.
- `program_*` and `state_body_*` totals repeat on every subprogram row in `BUDGET_LAW` and `SPENDING_*`. Deduplicate parent totals before aggregating above `subprogram` grain.
- `BUDGET_LAW` and `SPENDING_*` are comparable only when the metric and grain are aligned.
- `SPENDING_Q1`, `SPENDING_Q12`, and `SPENDING_Q123` are not full-year actuals.
- If `SPENDING_Q1234` is missing, do not silently replace full-year actuals with a forecast or expected value. Use a partial-year source only when that mixed horizon is explicitly labeled.
- `MTEP` is a planning dataset. Do not compare it to factual execution as if it were actual spend.
- GDP records are denominators or macro context, not budget rows. Keep their scenario/status separate from the budget or spending metric being divided.
- GDP values are usually in `մլրդ դրամ`; budget and spending CSV values are usually in `հազ. դրամ`. Convert units explicitly before computing shares.
- The same `target_year` can appear multiple times across report years and scenarios. Do not build a GDP series without an explicit source and scenario rule.
- Some topics require manual continuity mappings across reorganizations or program-code changes. Treat those mappings as explicit assumptions, not implicit facts.

## Common failure modes

- Mixing annual and period measures in one series without saying so
- Mixing original and revised annual plans without naming the metric
- Summing repeated parent totals without deduplicating the parent rows first
- Replacing missing actuals with expected or forecast values without labeling the substitution
- Treating `MTEP` totals as actual spending
- Treating forecast, budget, or historical GDP rows as actual GDP
- Computing GDP shares without converting units
- Comparing program totals with subprogram actuals
- Assuming a complete year panel instead of checking availability
- Forgetting that 2025 introduces `program_code_ext`, which can matter for lineages
