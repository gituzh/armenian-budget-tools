# Validation Report: 2020_SPENDING_Q1234.csv

**Source Type:** SPENDING_Q1234
**File:** 2020_SPENDING_Q1234.csv
**Generated:** 2026-11-22 01:42:42

## Summary

### Check Status

- **Total Rules:** 39
- **Passed:** 35 ✅
- **With Warnings:** 4 ⚠️
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
- **hierarchical_totals** (overall_rev_annual_plan vs state_body_rev_annual_plan)
- **hierarchical_totals** (state_body_rev_annual_plan vs program_rev_annual_plan)
- **hierarchical_totals** (program_rev_annual_plan vs subprogram_rev_annual_plan)
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
- **required_fields**

## ⚠️ Warnings

### ⚠️ execution_exceeds_100: subprogram (1 failures)

- Row 213: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (171.70%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002

### ⚠️ negative_percentages: program (11 failures)

- Row 204: Negative percentage for 'program_actual_vs_rev_annual_plan' (-2.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Row 205: Negative percentage for 'program_actual_vs_rev_annual_plan' (-2.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Row 206: Negative percentage for 'program_actual_vs_rev_annual_plan' (-2.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Row 207: Negative percentage for 'program_actual_vs_rev_annual_plan' (-2.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11012
- Row 208: Negative percentage for 'program_actual_vs_rev_annual_plan' (-2.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Row 209: Negative percentage for 'program_actual_vs_rev_annual_plan' (-2.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12001
- Row 210: Negative percentage for 'program_actual_vs_rev_annual_plan' (-2.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12002
- Row 211: Negative percentage for 'program_actual_vs_rev_annual_plan' (-2.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12003
- Row 212: Negative percentage for 'program_actual_vs_rev_annual_plan' (-2.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Row 213: Negative percentage for 'program_actual_vs_rev_annual_plan' (-2.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Row 214: Negative percentage for 'program_actual_vs_rev_annual_plan' (-2.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31004

### ⚠️ negative_totals: program (11 failures)

- Program field 'program_actual' has negative value: -13377.70 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Program field 'program_actual' has negative value: -13377.70 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Program field 'program_actual' has negative value: -13377.70 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Program field 'program_actual' has negative value: -13377.70 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11012
- Program field 'program_actual' has negative value: -13377.70 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Program field 'program_actual' has negative value: -13377.70 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12001
- Program field 'program_actual' has negative value: -13377.70 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12002
- Program field 'program_actual' has negative value: -13377.70 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12003
- Program field 'program_actual' has negative value: -13377.70 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Program field 'program_actual' has negative value: -13377.70 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Program field 'program_actual' has negative value: -13377.70 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31004

### ⚠️ negative_totals: subprogram (3 failures)

- Subprogram field 'subprogram_annual_plan' has negative value: -20066.40 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_rev_annual_plan' has negative value: -879164.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_actual' has negative value: -1509593.50 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002

---

For detailed information about validation checks and how to interpret results,
see [docs/validation.md](../../docs/validation.md).
