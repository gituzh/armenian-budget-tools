# Datasets

## File naming and root

- Primary parsed budget datasets live in a single active parsed-data root and use `{year}_{SOURCE_TYPE}.csv`.
- GDP snapshots from `gdp-extract` use `{year}_{BUDGET_LAW|SPENDING_Q1234}_GDP.json`.
- A name with a label after the source type, `{year}_BUDGET_LAW_{LABEL}.csv`, is another published version of that year's budget law, not the adopted one. `{year}_BUDGET_LAW.csv` without a label is the adopted law; use it unless the question is about a draft.
  - `EDRAFT`: public-consultation copy from e-draft.am (2020-2026).
  - `PARLIAMENT`: draft as submitted to parliament (2021-2026).
  - `PARLIAMENT2`: revised draft published by parliament.am for the second reading (2020-2026). Its data is identical to the adopted law in each of these years.
  - `DRAFT`, `DRAFT2`: draft and revised draft from a government session agenda on e-gov.am (2026 `DRAFT2`, 2027 `DRAFT`). 2027 has only a draft so far.
  - Drafts with a budget message in DOCX also have `{year}_BUDGET_LAW_{LABEL}_GDP.json` (`EDRAFT` 2021-2026; 2020 `EDRAFT` has none: the extractor finds no GDP table); `PARLIAMENT` and `PARLIAMENT2` have none.
  - A draft's `_validation.md` has an `Identical data` line when its CSV is byte-identical to other versions of that year (2026 `DRAFT2` and `PARLIAMENT2` of 2020-2026 equal the adopted law; `EDRAFT` of 2021-2024 equals `PARLIAMENT`; 2020 `EDRAFT` equals no other version).
  - Missing versions (not an error in the data). Every year 2019-2027 and label not covered by a year range above is one of these (searches: 22 Nov 2026; "not found" means a bounded search missed it, not that it was never published):
    - Not published as a spreadsheet: every 2019 draft (programme tables are PDF only; 2019 `DRAFT2` is one sheet of changes with no annexes archive); 2020 `PARLIAMENT`, `DRAFT` and `DRAFT2` (programme tables are PDF only); 2027 `EDRAFT` (the e-draft.am project has only the law text).
    - File lost (the e-gov.am session agenda lists the file, the link no longer downloads): `DRAFT` 2022-2026, `DRAFT2` 2023-2025.
    - Not found: 2021 `DRAFT` and `DRAFT2`, 2022 `DRAFT2` (e-gov.am session archive searched on 22 Nov 2026); 2027 `PARLIAMENT` and `PARLIAMENT2` (parliament.am draft lists searched on 22 Nov 2026; they hold no draft later than 3 Jul 2026).
    - Not yet published: 2027 `DRAFT2` (session agendas read up to 19 Nov 2026).
    - Table with reasons, sessions and file ids: `docs/data_schemas.md` 3.4.
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
