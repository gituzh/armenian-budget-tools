# Validation Report: 2021_SPENDING_Q1.csv

**Source Type:** SPENDING_Q1
**File:** 2021_SPENDING_Q1.csv
**Generated:** 2026-11-22 01:42:42

## Summary

### Check Status

- **Total Rules:** 53
- **Passed:** 48 ✅
- **With Warnings:** 5 ⚠️
- **With Errors:** 0 ❌

### Issues Found

- **Errors:** 0
- **Warnings:** 26 ⚠️

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
- **negative_percentages** (subprogram)
- **negative_totals** (overall)
- **negative_totals** (state_body)
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

### ⚠️ execution_exceeds_100: subprogram (3 failures)

- Row 172: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (43710.50%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Row 189: Execution > 100% for 'subprogram_actual_vs_rev_period_plan' (125.50%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1157 | 12017
- Row 224: Execution > 100% for 'subprogram_actual_vs_rev_period_plan' (102.50%) in ՀՀ առողջապահության նախարարություն | 1053 | 11009

### ⚠️ negative_percentages: program (10 failures)

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

### ⚠️ negative_totals: program (5 failures)

- Program field 'program_actual' has negative value: -267695.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Program field 'program_actual' has negative value: -267695.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Program field 'program_actual' has negative value: -267695.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Program field 'program_actual' has negative value: -267695.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Program field 'program_actual' has negative value: -267695.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002

### ⚠️ negative_totals: subprogram (3 failures)

- Subprogram field 'subprogram_annual_plan' has negative value: -1276.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_rev_annual_plan' has negative value: -1276.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_actual' has negative value: -557746.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002

### ⚠️ period_vs_annual: subprogram (5 failures)

- Subprogram violation: 'subprogram_period_plan' (272450.40) exceeds limit 'subprogram_annual_plan' (0.00) by 272450.40 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1004 | 11012
- Subprogram violation: 'subprogram_period_plan' (227272.00) exceeds limit 'subprogram_annual_plan' (0.00) by 227272.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1072 | 11003
- Subprogram violation: 'subprogram_period_plan' (165000.00) exceeds limit 'subprogram_annual_plan' (0.00) by 165000.00 for ՀՀ առողջապահության նախարարություն | 1053 | 32004
- Subprogram violation: 'subprogram_period_plan' (500000.00) exceeds limit 'subprogram_annual_plan' (387693.00) by 112307.00 for ՀՀ ֆինանսների նախարարություն | 1006 | 11002
- Subprogram violation: 'subprogram_period_plan' (25000.00) exceeds limit 'subprogram_annual_plan' (0.00) by 25000.00 for ՀՀ ֆինանսների նախարարություն | 1108 | 11008

---

For detailed information about validation checks and how to interpret results,
see [docs/validation.md](../../docs/validation.md).
