# Validation Report: 2024_SPENDING_Q1234.csv

**Source Type:** SPENDING_Q1234
**File:** 2024_SPENDING_Q1234.csv
**Generated:** 2026-11-22 01:42:45

## Summary

### Check Status

- **Total Rules:** 39
- **Passed:** 35 ✅
- **With Warnings:** 4 ⚠️
- **With Errors:** 0 ❌

### Issues Found

- **Errors:** 0
- **Warnings:** 50 ⚠️

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

### ⚠️ execution_exceeds_100: program (11 failures)

- Row 198: Execution > 100% for 'program_actual_vs_rev_annual_plan' (112.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Row 199: Execution > 100% for 'program_actual_vs_rev_annual_plan' (112.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Row 200: Execution > 100% for 'program_actual_vs_rev_annual_plan' (112.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Row 201: Execution > 100% for 'program_actual_vs_rev_annual_plan' (112.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Row 202: Execution > 100% for 'program_actual_vs_rev_annual_plan' (112.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11017
- Row 203: Execution > 100% for 'program_actual_vs_rev_annual_plan' (112.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12002
- Row 204: Execution > 100% for 'program_actual_vs_rev_annual_plan' (112.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12003
- Row 205: Execution > 100% for 'program_actual_vs_rev_annual_plan' (112.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Row 206: Execution > 100% for 'program_actual_vs_rev_annual_plan' (112.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Row 207: Execution > 100% for 'program_actual_vs_rev_annual_plan' (112.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31004
- Row 208: Execution > 100% for 'program_actual_vs_rev_annual_plan' (112.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31005

### ⚠️ execution_exceeds_100: subprogram (3 failures)

- Row 171: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (140.80%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1049 | 21014
- Row 206: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (107.10%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Row 263: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (102.90%) in ՀՀ առողջապահության նախարարություն | 1053 | 11006

### ⚠️ negative_totals: program (33 failures)

- Program field 'program_annual_plan' has negative value: -11559968.40 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Program field 'program_annual_plan' has negative value: -11559968.40 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Program field 'program_annual_plan' has negative value: -11559968.40 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Program field 'program_annual_plan' has negative value: -11559968.40 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Program field 'program_annual_plan' has negative value: -11559968.40 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11017
- Program field 'program_annual_plan' has negative value: -11559968.40 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12002
- Program field 'program_annual_plan' has negative value: -11559968.40 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12003
- Program field 'program_annual_plan' has negative value: -11559968.40 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Program field 'program_annual_plan' has negative value: -11559968.40 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Program field 'program_annual_plan' has negative value: -11559968.40 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31004
- Program field 'program_annual_plan' has negative value: -11559968.40 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31005
- Program field 'program_rev_annual_plan' has negative value: -9422359.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Program field 'program_rev_annual_plan' has negative value: -9422359.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Program field 'program_rev_annual_plan' has negative value: -9422359.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Program field 'program_rev_annual_plan' has negative value: -9422359.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Program field 'program_rev_annual_plan' has negative value: -9422359.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11017
- Program field 'program_rev_annual_plan' has negative value: -9422359.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12002
- Program field 'program_rev_annual_plan' has negative value: -9422359.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12003
- Program field 'program_rev_annual_plan' has negative value: -9422359.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Program field 'program_rev_annual_plan' has negative value: -9422359.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Program field 'program_rev_annual_plan' has negative value: -9422359.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31004
- Program field 'program_rev_annual_plan' has negative value: -9422359.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31005
- Program field 'program_actual' has negative value: -10589231.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Program field 'program_actual' has negative value: -10589231.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Program field 'program_actual' has negative value: -10589231.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Program field 'program_actual' has negative value: -10589231.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Program field 'program_actual' has negative value: -10589231.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11017
- Program field 'program_actual' has negative value: -10589231.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12002
- Program field 'program_actual' has negative value: -10589231.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12003
- Program field 'program_actual' has negative value: -10589231.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Program field 'program_actual' has negative value: -10589231.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Program field 'program_actual' has negative value: -10589231.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31004
- Program field 'program_actual' has negative value: -10589231.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31005

### ⚠️ negative_totals: subprogram (3 failures)

- Subprogram field 'subprogram_annual_plan' has negative value: -15000000.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_rev_annual_plan' has negative value: -15000000.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_actual' has negative value: -16065233.40 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002

---

For detailed information about validation checks and how to interpret results,
see [docs/validation.md](../../docs/validation.md).
