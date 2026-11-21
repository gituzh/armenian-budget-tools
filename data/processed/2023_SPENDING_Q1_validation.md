# Validation Report: 2023_SPENDING_Q1.csv

**Source Type:** SPENDING_Q1
**File:** 2023_SPENDING_Q1.csv
**Generated:** 2026-11-22 01:42:44

## Summary

### Check Status

- **Total Rules:** 53
- **Passed:** 48 ✅
- **With Warnings:** 5 ⚠️
- **With Errors:** 0 ❌

### Issues Found

- **Errors:** 0
- **Warnings:** 52 ⚠️

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
- **negative_percentages** (program)
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

### ⚠️ execution_exceeds_100: program (10 failures)

- Row 138: Execution > 100% for 'program_actual_vs_rev_period_plan' (164.50%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1040 | 12002
- Row 139: Execution > 100% for 'program_actual_vs_rev_period_plan' (164.50%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1040 | 12003
- Row 140: Execution > 100% for 'program_actual_vs_rev_period_plan' (164.50%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1040 | 32004
- Row 141: Execution > 100% for 'program_actual_vs_rev_period_plan' (164.50%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1040 | 32009
- Row 194: Execution > 100% for 'program_actual_vs_rev_period_plan' (230.10%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Row 195: Execution > 100% for 'program_actual_vs_rev_period_plan' (230.10%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Row 196: Execution > 100% for 'program_actual_vs_rev_period_plan' (230.10%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Row 197: Execution > 100% for 'program_actual_vs_rev_period_plan' (230.10%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Row 198: Execution > 100% for 'program_actual_vs_rev_period_plan' (230.10%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Row 199: Execution > 100% for 'program_actual_vs_rev_period_plan' (230.10%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002

### ⚠️ execution_exceeds_100: subprogram (3 failures)

- Row 140: Execution > 100% for 'subprogram_actual_vs_rev_period_plan' (212.20%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1040 | 32004
- Row 161: Execution > 100% for 'subprogram_actual_vs_rev_period_plan' (103.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1049 | 21009
- Row 199: Execution > 100% for 'subprogram_actual_vs_rev_period_plan' (181.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002

### ⚠️ negative_totals: program (30 failures)

- Program field 'program_annual_plan' has negative value: -8683502.80 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Program field 'program_annual_plan' has negative value: -8683502.80 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Program field 'program_annual_plan' has negative value: -8683502.80 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Program field 'program_annual_plan' has negative value: -8683502.80 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Program field 'program_annual_plan' has negative value: -8683502.80 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Program field 'program_annual_plan' has negative value: -8683502.80 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Program field 'program_rev_annual_plan' has negative value: -8674410.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Program field 'program_rev_annual_plan' has negative value: -8674410.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Program field 'program_rev_annual_plan' has negative value: -8674410.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Program field 'program_rev_annual_plan' has negative value: -8674410.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Program field 'program_rev_annual_plan' has negative value: -8674410.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Program field 'program_rev_annual_plan' has negative value: -8674410.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Program field 'program_period_plan' has negative value: -691703.30 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Program field 'program_period_plan' has negative value: -691703.30 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Program field 'program_period_plan' has negative value: -691703.30 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Program field 'program_period_plan' has negative value: -691703.30 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Program field 'program_period_plan' has negative value: -691703.30 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Program field 'program_period_plan' has negative value: -691703.30 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Program field 'program_rev_period_plan' has negative value: -682610.70 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Program field 'program_rev_period_plan' has negative value: -682610.70 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Program field 'program_rev_period_plan' has negative value: -682610.70 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Program field 'program_rev_period_plan' has negative value: -682610.70 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Program field 'program_rev_period_plan' has negative value: -682610.70 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Program field 'program_rev_period_plan' has negative value: -682610.70 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Program field 'program_actual' has negative value: -1570913.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Program field 'program_actual' has negative value: -1570913.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Program field 'program_actual' has negative value: -1570913.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Program field 'program_actual' has negative value: -1570913.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Program field 'program_actual' has negative value: -1570913.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Program field 'program_actual' has negative value: -1570913.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002

### ⚠️ negative_totals: subprogram (5 failures)

- Subprogram field 'subprogram_annual_plan' has negative value: -10000000.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_rev_annual_plan' has negative value: -10000000.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_period_plan' has negative value: -1025726.50 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_rev_period_plan' has negative value: -1025726.50 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_actual' has negative value: -1856517.80 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002

### ⚠️ period_vs_annual: subprogram (4 failures)

- Subprogram violation: 'subprogram_period_plan' (8250.00) exceeds limit 'subprogram_annual_plan' (0.00) by 8250.00 for ՀՀ վարչապետի  աշխատակազմ | 1136 | 31005
- Subprogram violation: 'subprogram_period_plan' (164988.10) exceeds limit 'subprogram_annual_plan' (0.00) by 164988.10 for ՀՀ էկոնոմիկայի նախարարություն | 1190 | 11007
- Subprogram violation: 'subprogram_period_plan' (1396.80) exceeds limit 'subprogram_annual_plan' (0.00) by 1396.80 for ՀՀ աշխատանքի և սոցիալական հարցերի նախարարություն | 1160 | 12006
- Subprogram violation: 'subprogram_period_plan' (84741.80) exceeds limit 'subprogram_annual_plan' (0.00) by 84741.80 for ՀՀ ֆինանսների նախարարություն | 1108 | 31002

---

For detailed information about validation checks and how to interpret results,
see [docs/validation.md](../../docs/validation.md).
