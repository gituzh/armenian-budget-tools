# Validation Report: 2022_SPENDING_Q1234.csv

**Source Type:** SPENDING_Q1234
**File:** 2022_SPENDING_Q1234.csv
**Generated:** 2026-11-22 01:42:44

## Summary

### Check Status

- **Total Rules:** 39
- **Passed:** 36 ✅
- **With Warnings:** 3 ⚠️
- **With Errors:** 0 ❌

### Issues Found

- **Errors:** 0
- **Warnings:** 35 ⚠️

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
- **negative_percentages** (program)
- **negative_percentages** (subprogram)
- **negative_totals** (overall)
- **negative_totals** (state_body)
- **percentage_calculation** (overall_actual_vs_rev_annual_plan)
- **percentage_calculation** (state_body_actual_vs_rev_annual_plan)
- **percentage_calculation** (program_actual_vs_rev_annual_plan)
- **percentage_calculation** (subprogram_actual_vs_rev_annual_plan)
- **required_fields**

## ⚠️ Warnings

### ⚠️ execution_exceeds_100: subprogram (5 failures)

- Row 134: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (100.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1019 | 11001
- Row 174: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (103.70%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1049 | 21014
- Row 276: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (100.60%) in ՀՀ առողջապահության նախարարություն | 1053 | 11009
- Row 279: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (100.10%) in ՀՀ առողջապահության նախարարություն | 1053 | 11015
- Row 281: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (102.60%) in ՀՀ առողջապահության նախարարություն | 1053 | 32001

### ⚠️ negative_totals: program (27 failures)

- Program field 'program_annual_plan' has negative value: -8917337.50 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Program field 'program_annual_plan' has negative value: -8917337.50 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Program field 'program_annual_plan' has negative value: -8917337.50 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Program field 'program_annual_plan' has negative value: -8917337.50 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11012
- Program field 'program_annual_plan' has negative value: -8917337.50 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Program field 'program_annual_plan' has negative value: -8917337.50 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12003
- Program field 'program_annual_plan' has negative value: -8917337.50 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Program field 'program_annual_plan' has negative value: -8917337.50 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31004
- Program field 'program_annual_plan' has negative value: -8917337.50 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 32001
- Program field 'program_rev_annual_plan' has negative value: -8683403.50 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Program field 'program_rev_annual_plan' has negative value: -8683403.50 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Program field 'program_rev_annual_plan' has negative value: -8683403.50 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Program field 'program_rev_annual_plan' has negative value: -8683403.50 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11012
- Program field 'program_rev_annual_plan' has negative value: -8683403.50 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Program field 'program_rev_annual_plan' has negative value: -8683403.50 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12003
- Program field 'program_rev_annual_plan' has negative value: -8683403.50 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Program field 'program_rev_annual_plan' has negative value: -8683403.50 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31004
- Program field 'program_rev_annual_plan' has negative value: -8683403.50 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 32001
- Program field 'program_actual' has negative value: -7356722.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Program field 'program_actual' has negative value: -7356722.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Program field 'program_actual' has negative value: -7356722.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Program field 'program_actual' has negative value: -7356722.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11012
- Program field 'program_actual' has negative value: -7356722.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Program field 'program_actual' has negative value: -7356722.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12003
- Program field 'program_actual' has negative value: -7356722.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Program field 'program_actual' has negative value: -7356722.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31004
- Program field 'program_actual' has negative value: -7356722.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 32001

### ⚠️ negative_totals: subprogram (3 failures)

- Subprogram field 'subprogram_annual_plan' has negative value: -10059266.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_rev_annual_plan' has negative value: -10059266.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_actual' has negative value: -8725601.50 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002

---

For detailed information about validation checks and how to interpret results,
see [docs/validation.md](../../docs/validation.md).
