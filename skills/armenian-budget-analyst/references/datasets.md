# Datasets

## File naming and root

- Primary parsed datasets live in a single data root and use `{year}_{SOURCE_TYPE}.csv`.
- Prefer `ARMENIAN_BUDGET_DATA_PATH` when set; otherwise use repo `data/processed`.
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

## Measure selection

- Allocation questions: start with `BUDGET_LAW`.
- Full-year execution questions: use `SPENDING_Q1234` when available.
- Partial-year execution questions: use `SPENDING_Q1`, `SPENDING_Q12`, or `SPENDING_Q123`, and label the covered period.
- Projection questions: use `MTEP`, and name the specific plan year `y0`, `y1`, or `y2`.

## Comparability rules

- Keep the aggregation grain consistent. If the budget side uses `program_total`, compare it to `program_actual`, not `subprogram_actual`.
- `BUDGET_LAW` and `SPENDING_*` are comparable only when the metric and grain are aligned.
- `SPENDING_Q1`, `SPENDING_Q12`, and `SPENDING_Q123` are not full-year actuals.
- `MTEP` is a planning dataset. Do not compare it to factual execution as if it were actual spend.
- Some topics require manual continuity mappings across reorganizations or program-code changes. Treat those mappings as explicit assumptions, not implicit facts.

## Common failure modes

- Mixing annual and period measures in one series without saying so
- Mixing original and revised annual plans without naming the metric
- Treating `MTEP` totals as actual spending
- Comparing program totals with subprogram actuals
- Assuming a complete year panel instead of checking availability
- Forgetting that 2025 introduces `program_code_ext`, which can matter for lineages
