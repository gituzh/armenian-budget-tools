# Validation Report: 2025_SPENDING_Q12.csv

**Source Type:** SPENDING_Q12
**File:** 2025_SPENDING_Q12.csv
**Generated:** 2026-11-22 01:42:46

## Summary

### Check Status

- **Total Rules:** 53
- **Passed:** 47 ✅
- **With Warnings:** 6 ⚠️
- **With Errors:** 0 ❌

### Issues Found

- **Errors:** 0
- **Warnings:** 82 ⚠️

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

### ⚠️ execution_exceeds_100: program (2 failures)

- Row 56: Execution > 100% for 'program_actual_vs_rev_annual_plan' (103.60%) in ՀՀ վարչապետի  աշխատակազմ | 1214 | 11003
- Row 56: Execution > 100% for 'program_actual_vs_rev_period_plan' (103.60%) in ՀՀ վարչապետի  աշխատակազմ | 1214 | 11003

### ⚠️ execution_exceeds_100: subprogram (5 failures)

- Row 56: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (103.60%) in ՀՀ վարչապետի  աշխատակազմ | 1214 | 11003
- Row 230: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (100.50%) in ՀՀ առողջապահության նախարարություն | 1053 | 11015
- Row 56: Execution > 100% for 'subprogram_actual_vs_rev_period_plan' (103.60%) in ՀՀ վարչապետի  աշխատակազմ | 1214 | 11003
- Row 226: Execution > 100% for 'subprogram_actual_vs_rev_period_plan' (100.60%) in ՀՀ առողջապահության նախարարություն | 1053 | 11006
- Row 230: Execution > 100% for 'subprogram_actual_vs_rev_period_plan' (100.50%) in ՀՀ առողջապահության նախարարություն | 1053 | 11015

### ⚠️ negative_percentages: program (22 failures)

- Row 170: Negative percentage for 'program_actual_vs_rev_annual_plan' (-9.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Row 171: Negative percentage for 'program_actual_vs_rev_annual_plan' (-9.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Row 172: Negative percentage for 'program_actual_vs_rev_annual_plan' (-9.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Row 173: Negative percentage for 'program_actual_vs_rev_annual_plan' (-9.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11012
- Row 174: Negative percentage for 'program_actual_vs_rev_annual_plan' (-9.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Row 175: Negative percentage for 'program_actual_vs_rev_annual_plan' (-9.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11017
- Row 176: Negative percentage for 'program_actual_vs_rev_annual_plan' (-9.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11018
- Row 177: Negative percentage for 'program_actual_vs_rev_annual_plan' (-9.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12002
- Row 178: Negative percentage for 'program_actual_vs_rev_annual_plan' (-9.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Row 179: Negative percentage for 'program_actual_vs_rev_annual_plan' (-9.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Row 180: Negative percentage for 'program_actual_vs_rev_annual_plan' (-9.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31004
- Row 170: Negative percentage for 'program_actual_vs_rev_period_plan' (-23.30%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Row 171: Negative percentage for 'program_actual_vs_rev_period_plan' (-23.30%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Row 172: Negative percentage for 'program_actual_vs_rev_period_plan' (-23.30%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Row 173: Negative percentage for 'program_actual_vs_rev_period_plan' (-23.30%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11012
- Row 174: Negative percentage for 'program_actual_vs_rev_period_plan' (-23.30%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Row 175: Negative percentage for 'program_actual_vs_rev_period_plan' (-23.30%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11017
- Row 176: Negative percentage for 'program_actual_vs_rev_period_plan' (-23.30%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11018
- Row 177: Negative percentage for 'program_actual_vs_rev_period_plan' (-23.30%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12002
- Row 178: Negative percentage for 'program_actual_vs_rev_period_plan' (-23.30%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Row 179: Negative percentage for 'program_actual_vs_rev_period_plan' (-23.30%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Row 180: Negative percentage for 'program_actual_vs_rev_period_plan' (-23.30%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31004

### ⚠️ negative_totals: program (44 failures)

- Program field 'program_annual_plan' has negative value: -12529883.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Program field 'program_annual_plan' has negative value: -12529883.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Program field 'program_annual_plan' has negative value: -12529883.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Program field 'program_annual_plan' has negative value: -12529883.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11012
- Program field 'program_annual_plan' has negative value: -12529883.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Program field 'program_annual_plan' has negative value: -12529883.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11017
- Program field 'program_annual_plan' has negative value: -12529883.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11018
- Program field 'program_annual_plan' has negative value: -12529883.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12002
- Program field 'program_annual_plan' has negative value: -12529883.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Program field 'program_annual_plan' has negative value: -12529883.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Program field 'program_annual_plan' has negative value: -12529883.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31004
- Program field 'program_rev_annual_plan' has negative value: -12051946.30 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Program field 'program_rev_annual_plan' has negative value: -12051946.30 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Program field 'program_rev_annual_plan' has negative value: -12051946.30 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Program field 'program_rev_annual_plan' has negative value: -12051946.30 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11012
- Program field 'program_rev_annual_plan' has negative value: -12051946.30 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Program field 'program_rev_annual_plan' has negative value: -12051946.30 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11017
- Program field 'program_rev_annual_plan' has negative value: -12051946.30 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11018
- Program field 'program_rev_annual_plan' has negative value: -12051946.30 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12002
- Program field 'program_rev_annual_plan' has negative value: -12051946.30 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Program field 'program_rev_annual_plan' has negative value: -12051946.30 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Program field 'program_rev_annual_plan' has negative value: -12051946.30 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31004
- Program field 'program_period_plan' has negative value: -5340136.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Program field 'program_period_plan' has negative value: -5340136.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Program field 'program_period_plan' has negative value: -5340136.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Program field 'program_period_plan' has negative value: -5340136.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11012
- Program field 'program_period_plan' has negative value: -5340136.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Program field 'program_period_plan' has negative value: -5340136.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11017
- Program field 'program_period_plan' has negative value: -5340136.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11018
- Program field 'program_period_plan' has negative value: -5340136.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12002
- Program field 'program_period_plan' has negative value: -5340136.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Program field 'program_period_plan' has negative value: -5340136.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Program field 'program_period_plan' has negative value: -5340136.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31004
- Program field 'program_rev_period_plan' has negative value: -4862198.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Program field 'program_rev_period_plan' has negative value: -4862198.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Program field 'program_rev_period_plan' has negative value: -4862198.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Program field 'program_rev_period_plan' has negative value: -4862198.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11012
- Program field 'program_rev_period_plan' has negative value: -4862198.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Program field 'program_rev_period_plan' has negative value: -4862198.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11017
- Program field 'program_rev_period_plan' has negative value: -4862198.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11018
- Program field 'program_rev_period_plan' has negative value: -4862198.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12002
- Program field 'program_rev_period_plan' has negative value: -4862198.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Program field 'program_rev_period_plan' has negative value: -4862198.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Program field 'program_rev_period_plan' has negative value: -4862198.90 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31004

### ⚠️ negative_totals: subprogram (5 failures)

- Subprogram field 'subprogram_annual_plan' has negative value: -15000000.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_rev_annual_plan' has negative value: -15000000.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_period_plan' has negative value: -6750000.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_rev_period_plan' has negative value: -6750000.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_actual' has negative value: -612073.50 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002

### ⚠️ period_vs_annual: subprogram (4 failures)

- Subprogram violation: 'subprogram_period_plan' (717569.10) exceeds limit 'subprogram_annual_plan' (465000.00) by 252569.10 for ՀՀ էկոնոմիկայի նախարարություն | 1116 | 11005
- Subprogram violation: 'subprogram_period_plan' (5250.00) exceeds limit 'subprogram_annual_plan' (0.00) by 5250.00 for ՀՀ աշխատանքի և սոցիալական հարցերի նախարարություն | 1082 | 11001
- Subprogram violation: 'subprogram_period_plan' (23778.80) exceeds limit 'subprogram_annual_plan' (0.00) by 23778.80 for ՀՀ բարձր տեխնոլոգիական արդյունաբերության նախարարություն | 1235 | 11007
- Subprogram violation: 'subprogram_period_plan' (470.40) exceeds limit 'subprogram_annual_plan' (0.00) by 470.40 for ՀՀ բարձր տեխնոլոգիական արդյունաբերության նախարարություն | 1235 | 31002

---

For detailed information about validation checks and how to interpret results,
see [docs/validation.md](../../docs/validation.md).
