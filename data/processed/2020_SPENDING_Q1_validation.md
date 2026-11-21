# Validation Report: 2020_SPENDING_Q1.csv

**Source Type:** SPENDING_Q1
**File:** 2020_SPENDING_Q1.csv
**Generated:** 2026-11-22 01:42:42

## Summary

### Check Status

- **Total Rules:** 53
- **Passed:** 50 ✅
- **With Warnings:** 3 ⚠️
- **With Errors:** 0 ❌

### Issues Found

- **Errors:** 0
- **Warnings:** 12 ⚠️

## ✅ Passed Checks

- **duplicate_records** (state_body blocks)
- **duplicate_records** (program blocks)
- **duplicate_records** (subprogram rows)
- **duplicate_records** (program totals)
- **duplicate_records** (state_body whitespace variants)
- **duplicate_records** (state_body totals)
- **empty_identifiers** (state_body)
- **empty_identifiers** (program)
- **empty_identifiers** (subprogram)
- **execution_exceeds_100** (overall)
- **execution_exceeds_100** (state_body)
- **execution_exceeds_100** (program)
- **hierarchical_totals** (overall_actual vs state_body_actual)
- **hierarchical_totals** (state_body_actual vs program_actual)
- **hierarchical_totals** (program_actual vs subprogram_actual)
- **hierarchical_totals** (overall_annual_plan vs state_body_annual_plan)
- **hierarchical_totals** (state_body_annual_plan vs program_annual_plan)
- **hierarchical_totals** (program_annual_plan vs subprogram_annual_plan)
- **hierarchical_totals** (overall_period_plan vs state_body_period_plan)
- **hierarchical_totals** (state_body_period_plan vs program_period_plan)
- **hierarchical_totals** (program_period_plan vs subprogram_period_plan)
- **hierarchical_totals** (overall_rev_annual_plan vs state_body_rev_annual_plan)
- **hierarchical_totals** (state_body_rev_annual_plan vs program_rev_annual_plan)
- **hierarchical_totals** (program_rev_annual_plan vs subprogram_rev_annual_plan)
- **hierarchical_totals** (overall_rev_period_plan vs state_body_rev_period_plan)
- **hierarchical_totals** (state_body_rev_period_plan vs program_rev_period_plan)
- **hierarchical_totals** (program_rev_period_plan vs subprogram_rev_period_plan)
- **missing_financial_data** (overall)
- **missing_financial_data** (state_body)
- **missing_financial_data** (program)
- **missing_financial_data** (subprogram)
- **negative_percentages** (overall)
- **negative_percentages** (state_body)
- **negative_percentages** (program)
- **negative_percentages** (subprogram)
- **negative_totals** (overall)
- **negative_totals** (state_body)
- **negative_totals** (program)
- **percentage_calculation** (overall_actual_vs_rev_annual_plan)
- **percentage_calculation** (state_body_actual_vs_rev_annual_plan)
- **percentage_calculation** (program_actual_vs_rev_annual_plan)
- **percentage_calculation** (subprogram_actual_vs_rev_annual_plan)
- **percentage_calculation** (overall_actual_vs_rev_period_plan)
- **percentage_calculation** (state_body_actual_vs_rev_period_plan)
- **percentage_calculation** (program_actual_vs_rev_period_plan)
- **percentage_calculation** (subprogram_actual_vs_rev_period_plan)
- **period_vs_annual** (overall)
- **period_vs_annual** (state_body)
- **period_vs_annual** (program)
- **required_fields**

## ⚠️ Warnings

### ⚠️ execution_exceeds_100: subprogram (1 failures)

- Row 178: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (916.10%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002

### ⚠️ negative_totals: subprogram (3 failures)

- Subprogram field 'subprogram_annual_plan' has negative value: -20066.40 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_rev_annual_plan' has negative value: -20066.40 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_actual' has negative value: -183833.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002

### ⚠️ period_vs_annual: subprogram (8 failures)

- Subprogram violation: 'subprogram_period_plan' (1393274.90) exceeds limit 'subprogram_annual_plan' (0.00) by 1393274.90 for ՀՀ վարչապետի  աշխատակազմ | 1136 | 11011
- Subprogram violation: 'subprogram_period_plan' (113280.00) exceeds limit 'subprogram_annual_plan' (0.00) by 113280.00 for ՀՀ վարչապետի  աշխատակազմ | 1136 | 31004
- Subprogram violation: 'subprogram_period_plan' (100000.00) exceeds limit 'subprogram_annual_plan' (0.00) by 100000.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1049 | 11015
- Subprogram violation: 'subprogram_period_plan' (158350.10) exceeds limit 'subprogram_annual_plan' (0.00) by 158350.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1167 | 11006
- Subprogram violation: 'subprogram_period_plan' (2250.00) exceeds limit 'subprogram_annual_plan' (0.00) by 2250.00 for ՀՀ աշխատանքի և սոցիալական հարցերի նախարարություն | 1088 | 11007
- Subprogram violation: 'subprogram_period_plan' (110000.00) exceeds limit 'subprogram_annual_plan' (70000.00) by 40000.00 for ՀՀ աշխատանքի և սոցիալական հարցերի նախարարություն | 1088 | 12013
- Subprogram violation: 'subprogram_period_plan' (602.00) exceeds limit 'subprogram_annual_plan' (0.00) by 602.00 for ՀՀ աշխատանքի և սոցիալական հարցերի նախարարություն | 1098 | 12003
- Subprogram violation: 'subprogram_rev_period_plan' (25005.00) exceeds limit 'subprogram_rev_annual_plan' (0.00) by 25005.00 for ՀՀ առողջապահության նախարարություն | 1099 | 11002

---

For detailed information about validation checks and how to interpret results,
see [docs/validation.md](../../docs/validation.md).
