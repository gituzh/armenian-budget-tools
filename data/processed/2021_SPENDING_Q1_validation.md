# Validation Report: 2021_SPENDING_Q1.csv

**Source Type:** SPENDING_Q1
**File:** 2021_SPENDING_Q1.csv
**Generated:** 2025-11-24 18:40:32

## Summary

### Check Status

- **Total Rules:** 47
- **Passed:** 36 ✅
- **With Warnings:** 4 ⚠️
- **With Errors:** 7 ❌

### Issues Found

- **Errors:** 13 ❌
- **Warnings:** 21 ⚠️

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
- **missing_financial_data**
- **missing_financial_data**
- **missing_financial_data**
- **missing_financial_data**
- **negative_percentages**
- **negative_percentages**
- **negative_percentages**
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

### ⚠️ execution_exceeds_100 (3 failures)

- Row 172: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (43710.50%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Row 189: Execution > 100% for 'subprogram_actual_vs_rev_period_plan' (125.50%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1157 | 12017
- Row 224: Execution > 100% for 'subprogram_actual_vs_rev_period_plan' (102.50%) in ՀՀ առողջապահության նախարարություն | 1053 | 11009

### ⚠️ negative_percentages (10 failures)

- Row 168: Negative percentage for 'program_actual_vs_rev_annual_plan' (-22.30%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Row 169: Negative percentage for 'program_actual_vs_rev_annual_plan' (-22.30%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Row 170: Negative percentage for 'program_actual_vs_rev_annual_plan' (-22.30%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Row 171: Negative percentage for 'program_actual_vs_rev_annual_plan' (-22.30%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Row 172: Negative percentage for 'program_actual_vs_rev_annual_plan' (-22.30%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Row 168: Negative percentage for 'program_actual_vs_rev_period_plan' (-80.80%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Row 169: Negative percentage for 'program_actual_vs_rev_period_plan' (-80.80%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Row 170: Negative percentage for 'program_actual_vs_rev_period_plan' (-80.80%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Row 171: Negative percentage for 'program_actual_vs_rev_period_plan' (-80.80%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Row 172: Negative percentage for 'program_actual_vs_rev_period_plan' (-80.80%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002

### ⚠️ negative_totals (5 failures)

- Program field 'program_actual' has negative value: -267695.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Program field 'program_actual' has negative value: -267695.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Program field 'program_actual' has negative value: -267695.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Program field 'program_actual' has negative value: -267695.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Program field 'program_actual' has negative value: -267695.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002

### ⚠️ negative_totals (3 failures)

- Subprogram field 'subprogram_annual_plan' has negative value: -1276.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_rev_annual_plan' has negative value: -1276.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_actual' has negative value: -557746.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002

## ❌ Errors

### ❌ hierarchical_totals (1 failures)

- ՀՀ ոստիկանություն: expected 13179134.299999999, got 13180551.2, diff 1416.9000000003725

### ❌ hierarchical_totals (1 failures)

- ՀՀ ոստիկանություն/Ոստիկանության ոլորտի քաղաքականության մշակում, կառավարում, կենտրոնացված միջոցառումներ, մոնիտորինգ և վերահսկողություն: expected 12919567.6, got 12918150.6, diff 1417.0

### ❌ hierarchical_totals (1 failures)

- ՀՀ ոստիկանություն: expected 65014056.9, got 65015473.8, diff 1416.8999999985099

### ❌ hierarchical_totals (1 failures)

- ՀՀ ոստիկանություն/Ոստիկանության ոլորտի քաղաքականության մշակում, կառավարում, կենտրոնացված միջոցառումներ, մոնիտորինգ և վերահսկողություն: expected 63449572.1, got 63448155.1, diff 1417.0

### ❌ hierarchical_totals (1 failures)

- ՀՀ ոստիկանություն: expected 15024380.7, got 15025797.6, diff 1416.9000000003725

### ❌ hierarchical_totals (1 failures)

- ՀՀ ոստիկանություն/Ոստիկանության ոլորտի քաղաքականության մշակում, կառավարում, կենտրոնացված միջոցառումներ, մոնիտորինգ և վերահսկողություն: expected 14634322.200000001, got 14632905.2, diff 1417.0000000018626

### ❌ period_vs_annual (7 failures)

- Subprogram violation: 'subprogram_period_plan' (272450.40) > 'subprogram_annual_plan' (0.00) by 272450.40 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1004 | 11012
- Subprogram violation: 'subprogram_period_plan' (227272.00) > 'subprogram_annual_plan' (0.00) by 227272.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1072 | 11003
- Subprogram violation: 'subprogram_period_plan' (0.00) > 'subprogram_annual_plan' (-1276.00) by 1276.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram violation: 'subprogram_period_plan' (165000.00) > 'subprogram_annual_plan' (0.00) by 165000.00 for ՀՀ առողջապահության նախարարություն | 1053 | 32004
- Subprogram violation: 'subprogram_period_plan' (500000.00) > 'subprogram_annual_plan' (387693.00) by 112307.00 for ՀՀ ֆինանսների նախարարություն | 1006 | 11002
- Subprogram violation: 'subprogram_period_plan' (25000.00) > 'subprogram_annual_plan' (0.00) by 25000.00 for ՀՀ ֆինանսների նախարարություն | 1108 | 11008
- Subprogram violation: 'subprogram_rev_period_plan' (0.00) > 'subprogram_rev_annual_plan' (-1276.00) by 1276.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002

---

For detailed information about validation checks and how to interpret results,
see [docs/validation.md](https://github.com/gituzh/armenian-budget-tools/blob/main/docs/validation.md).
