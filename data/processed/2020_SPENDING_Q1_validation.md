# Validation Report: 2020_SPENDING_Q1.csv

**Source Type:** SPENDING_Q1
**File:** 2020_SPENDING_Q1.csv
**Generated:** 2025-12-05 15:24:15

## Summary

### Check Status

- **Total Rules:** 47
- **Passed:** 44 ✅
- **With Warnings:** 3 ⚠️
- **With Errors:** 0 ❌

### Issues Found

- **Errors:** 0
- **Warnings:** 12 ⚠️

## ✅ Passed Checks

- **empty_identifiers**
- **empty_identifiers**
- **empty_identifiers**
- **execution_exceeds_100**
- **execution_exceeds_100**
- **execution_exceeds_100**
- **hierarchical_totals**
- **hierarchical_totals**
- **hierarchical_totals**
- **hierarchical_totals**
- **hierarchical_totals**
- **hierarchical_totals**
- **hierarchical_totals**
- **hierarchical_totals**
- **hierarchical_totals**
- **hierarchical_totals**
- **hierarchical_totals**
- **hierarchical_totals**
- **hierarchical_totals**
- **hierarchical_totals**
- **hierarchical_totals**
- **missing_financial_data**
- **missing_financial_data**
- **missing_financial_data**
- **missing_financial_data**
- **negative_percentages**
- **negative_percentages**
- **negative_percentages**
- **negative_percentages**
- **negative_totals**
- **negative_totals**
- **negative_totals**
- **percentage_calculation**
- **percentage_calculation**
- **percentage_calculation**
- **percentage_calculation**
- **percentage_calculation**
- **percentage_calculation**
- **percentage_calculation**
- **percentage_calculation**
- **period_vs_annual**
- **period_vs_annual**
- **period_vs_annual**
- **required_fields**

## ⚠️ Warnings

### ⚠️ execution_exceeds_100 (1 failures)

- Row 178: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (916.10%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002

### ⚠️ negative_totals (3 failures)

- Subprogram field 'subprogram_annual_plan' has negative value: -20066.40 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_rev_annual_plan' has negative value: -20066.40 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_actual' has negative value: -183833.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002

### ⚠️ period_vs_annual (8 failures)

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
see [docs/validation.md](https://github.com/gituzh/armenian-budget-tools/blob/main/docs/validation.md).
