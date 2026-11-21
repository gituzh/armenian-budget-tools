# Validation Report: 2020_SPENDING_Q12.csv

**Source Type:** SPENDING_Q12
**File:** 2020_SPENDING_Q12.csv
**Generated:** 2026-11-22 01:42:42

## Summary

### Check Status

- **Total Rules:** 53
- **Passed:** 48 ✅
- **With Warnings:** 5 ⚠️
- **With Errors:** 0 ❌

### Issues Found

- **Errors:** 0
- **Warnings:** 47 ⚠️

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

### ⚠️ execution_exceeds_100: subprogram (2 failures)

- Row 198: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (2671.50%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Row 198: Execution > 100% for 'subprogram_actual_vs_rev_period_plan' (4147.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002

### ⚠️ negative_percentages: program (20 failures)

- Row 190: Negative percentage for 'program_actual_vs_rev_annual_plan' (-0.20%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Row 191: Negative percentage for 'program_actual_vs_rev_annual_plan' (-0.20%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Row 192: Negative percentage for 'program_actual_vs_rev_annual_plan' (-0.20%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Row 193: Negative percentage for 'program_actual_vs_rev_annual_plan' (-0.20%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11012
- Row 194: Negative percentage for 'program_actual_vs_rev_annual_plan' (-0.20%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Row 195: Negative percentage for 'program_actual_vs_rev_annual_plan' (-0.20%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12001
- Row 196: Negative percentage for 'program_actual_vs_rev_annual_plan' (-0.20%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12002
- Row 197: Negative percentage for 'program_actual_vs_rev_annual_plan' (-0.20%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Row 198: Negative percentage for 'program_actual_vs_rev_annual_plan' (-0.20%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Row 199: Negative percentage for 'program_actual_vs_rev_annual_plan' (-0.20%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31004
- Row 190: Negative percentage for 'program_actual_vs_rev_period_plan' (-0.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Row 191: Negative percentage for 'program_actual_vs_rev_period_plan' (-0.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Row 192: Negative percentage for 'program_actual_vs_rev_period_plan' (-0.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Row 193: Negative percentage for 'program_actual_vs_rev_period_plan' (-0.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11012
- Row 194: Negative percentage for 'program_actual_vs_rev_period_plan' (-0.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Row 195: Negative percentage for 'program_actual_vs_rev_period_plan' (-0.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12001
- Row 196: Negative percentage for 'program_actual_vs_rev_period_plan' (-0.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12002
- Row 197: Negative percentage for 'program_actual_vs_rev_period_plan' (-0.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Row 198: Negative percentage for 'program_actual_vs_rev_period_plan' (-0.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Row 199: Negative percentage for 'program_actual_vs_rev_period_plan' (-0.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31004

### ⚠️ negative_totals: program (11 failures)

- Program field 'program_actual' has negative value: -3734.80 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Program field 'program_actual' has negative value: -3734.80 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Program field 'program_actual' has negative value: -3734.80 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Program field 'program_actual' has negative value: -3734.80 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11012
- Program field 'program_actual' has negative value: -3734.80 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Program field 'program_actual' has negative value: -3734.80 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12001
- Program field 'program_actual' has negative value: -3734.80 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12002
- Program field 'program_actual' has negative value: -3734.80 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Program field 'program_actual' has negative value: -3734.80 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Program field 'program_actual' has negative value: -3734.80 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31004
- Program field 'program_actual' has negative value: -1909.30 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 9017 | 31002

### ⚠️ negative_totals: subprogram (6 failures)

- Subprogram field 'subprogram_annual_plan' has negative value: -20066.40 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_rev_annual_plan' has negative value: -31152.30 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_period_plan' has negative value: -20066.40 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_rev_period_plan' has negative value: -20066.40 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_actual' has negative value: -832233.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_actual' has negative value: -1909.30 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 9017 | 31002

### ⚠️ period_vs_annual: subprogram (8 failures)

- Subprogram violation: 'subprogram_period_plan' (1585380.00) exceeds limit 'subprogram_annual_plan' (0.00) by 1585380.00 for ՀՀ վարչապետի  աշխատակազմ | 1136 | 11011
- Subprogram violation: 'subprogram_period_plan' (545280.00) exceeds limit 'subprogram_annual_plan' (0.00) by 545280.00 for ՀՀ վարչապետի  աշխատակազմ | 1136 | 31004
- Subprogram violation: 'subprogram_period_plan' (180000.00) exceeds limit 'subprogram_annual_plan' (0.00) by 180000.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1049 | 11015
- Subprogram violation: 'subprogram_period_plan' (158350.10) exceeds limit 'subprogram_annual_plan' (0.00) by 158350.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1167 | 11006
- Subprogram violation: 'subprogram_period_plan' (2250.00) exceeds limit 'subprogram_annual_plan' (0.00) by 2250.00 for ՀՀ աշխատանքի և սոցիալական հարցերի նախարարություն | 1088 | 11007
- Subprogram violation: 'subprogram_period_plan' (300000.00) exceeds limit 'subprogram_annual_plan' (70000.00) by 230000.00 for ՀՀ աշխատանքի և սոցիալական հարցերի նախարարություն | 1088 | 12013
- Subprogram violation: 'subprogram_period_plan' (602.00) exceeds limit 'subprogram_annual_plan' (0.00) by 602.00 for ՀՀ աշխատանքի և սոցիալական հարցերի նախարարություն | 1098 | 12003
- Subprogram violation: 'subprogram_rev_period_plan' (23996.60) exceeds limit 'subprogram_rev_annual_plan' (18720.30) by 5276.30 for ՀՀ շրջակա միջավայրի նախարարություն | 1173 | 11005

---

For detailed information about validation checks and how to interpret results,
see [docs/validation.md](../../docs/validation.md).
