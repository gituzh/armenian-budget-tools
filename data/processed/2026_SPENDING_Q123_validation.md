# Validation Report: 2026_SPENDING_Q123.csv

**Source Type:** SPENDING_Q123
**File:** 2026_SPENDING_Q123.csv
**Generated:** 2026-11-22 01:42:47

## Summary

### Check Status

- **Total Rules:** 53
- **Passed:** 47 ✅
- **With Warnings:** 6 ⚠️
- **With Errors:** 0 ❌

### Issues Found

- **Errors:** 0
- **Warnings:** 81 ⚠️

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
- **required_fields**

## ⚠️ Warnings

### ⚠️ execution_exceeds_100: program (11 failures)

- Row 157: Execution > 100% for 'program_actual_vs_rev_period_plan' (195.20%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Row 158: Execution > 100% for 'program_actual_vs_rev_period_plan' (195.20%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Row 159: Execution > 100% for 'program_actual_vs_rev_period_plan' (195.20%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Row 160: Execution > 100% for 'program_actual_vs_rev_period_plan' (195.20%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11012
- Row 161: Execution > 100% for 'program_actual_vs_rev_period_plan' (195.20%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Row 162: Execution > 100% for 'program_actual_vs_rev_period_plan' (195.20%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11017
- Row 163: Execution > 100% for 'program_actual_vs_rev_period_plan' (195.20%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11018
- Row 164: Execution > 100% for 'program_actual_vs_rev_period_plan' (195.20%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11019
- Row 165: Execution > 100% for 'program_actual_vs_rev_period_plan' (195.20%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Row 166: Execution > 100% for 'program_actual_vs_rev_period_plan' (195.20%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Row 167: Execution > 100% for 'program_actual_vs_rev_period_plan' (195.20%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31004

### ⚠️ execution_exceeds_100: subprogram (2 failures)

- Row 166: Execution > 100% for 'subprogram_actual_vs_rev_period_plan' (110.40%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Row 218: Execution > 100% for 'subprogram_actual_vs_rev_period_plan' (100.30%) in ՀՀ առողջապահության նախարարություն | 1053 | 11008

### ⚠️ negative_totals: program (55 failures)

- Program field 'program_annual_plan' has negative value: -7351877.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Program field 'program_annual_plan' has negative value: -7351877.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Program field 'program_annual_plan' has negative value: -7351877.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Program field 'program_annual_plan' has negative value: -7351877.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11012
- Program field 'program_annual_plan' has negative value: -7351877.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Program field 'program_annual_plan' has negative value: -7351877.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11017
- Program field 'program_annual_plan' has negative value: -7351877.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11018
- Program field 'program_annual_plan' has negative value: -7351877.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11019
- Program field 'program_annual_plan' has negative value: -7351877.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Program field 'program_annual_plan' has negative value: -7351877.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Program field 'program_annual_plan' has negative value: -7351877.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31004
- Program field 'program_rev_annual_plan' has negative value: -3266315.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Program field 'program_rev_annual_plan' has negative value: -3266315.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Program field 'program_rev_annual_plan' has negative value: -3266315.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Program field 'program_rev_annual_plan' has negative value: -3266315.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11012
- Program field 'program_rev_annual_plan' has negative value: -3266315.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Program field 'program_rev_annual_plan' has negative value: -3266315.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11017
- Program field 'program_rev_annual_plan' has negative value: -3266315.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11018
- Program field 'program_rev_annual_plan' has negative value: -3266315.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11019
- Program field 'program_rev_annual_plan' has negative value: -3266315.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Program field 'program_rev_annual_plan' has negative value: -3266315.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Program field 'program_rev_annual_plan' has negative value: -3266315.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31004
- Program field 'program_period_plan' has negative value: -5300756.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Program field 'program_period_plan' has negative value: -5300756.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Program field 'program_period_plan' has negative value: -5300756.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Program field 'program_period_plan' has negative value: -5300756.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11012
- Program field 'program_period_plan' has negative value: -5300756.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Program field 'program_period_plan' has negative value: -5300756.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11017
- Program field 'program_period_plan' has negative value: -5300756.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11018
- Program field 'program_period_plan' has negative value: -5300756.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11019
- Program field 'program_period_plan' has negative value: -5300756.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Program field 'program_period_plan' has negative value: -5300756.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Program field 'program_period_plan' has negative value: -5300756.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31004
- Program field 'program_rev_period_plan' has negative value: -1248462.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Program field 'program_rev_period_plan' has negative value: -1248462.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Program field 'program_rev_period_plan' has negative value: -1248462.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Program field 'program_rev_period_plan' has negative value: -1248462.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11012
- Program field 'program_rev_period_plan' has negative value: -1248462.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Program field 'program_rev_period_plan' has negative value: -1248462.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11017
- Program field 'program_rev_period_plan' has negative value: -1248462.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11018
- Program field 'program_rev_period_plan' has negative value: -1248462.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11019
- Program field 'program_rev_period_plan' has negative value: -1248462.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Program field 'program_rev_period_plan' has negative value: -1248462.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Program field 'program_rev_period_plan' has negative value: -1248462.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31004
- Program field 'program_actual' has negative value: -2436819.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Program field 'program_actual' has negative value: -2436819.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Program field 'program_actual' has negative value: -2436819.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Program field 'program_actual' has negative value: -2436819.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11012
- Program field 'program_actual' has negative value: -2436819.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Program field 'program_actual' has negative value: -2436819.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11017
- Program field 'program_actual' has negative value: -2436819.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11018
- Program field 'program_actual' has negative value: -2436819.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11019
- Program field 'program_actual' has negative value: -2436819.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Program field 'program_actual' has negative value: -2436819.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Program field 'program_actual' has negative value: -2436819.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31004

### ⚠️ negative_totals: subprogram (5 failures)

- Subprogram field 'subprogram_annual_plan' has negative value: -10000000.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_rev_annual_plan' has negative value: -10000000.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_period_plan' has negative value: -7500000.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_rev_period_plan' has negative value: -7500000.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_actual' has negative value: -8283171.70 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002

### ⚠️ period_vs_annual: program (2 failures)

- Program violation: 'program_period_plan' (41571.70) exceeds limit 'program_annual_plan' (36483.70) by 5088.00 for ՀՀ ֆինանսների նախարարություն | 1031 | 11001
- Program violation: 'program_period_plan' (41571.70) exceeds limit 'program_annual_plan' (36483.70) by 5088.00 for ՀՀ ֆինանսների նախարարություն | 1031 | 11002

### ⚠️ period_vs_annual: subprogram (6 failures)

- Subprogram violation: 'subprogram_period_plan' (30000.00) exceeds limit 'subprogram_annual_plan' (0.00) by 30000.00 for ՀՀ էկոնոմիկայի նախարարություն | 1165 | 12011
- Subprogram violation: 'subprogram_period_plan' (1191245.10) exceeds limit 'subprogram_annual_plan' (591245.10) by 600000.00 for ՀՀ կրթության, գիտության, մշակույթի և սպորտի նախարարություն | 1192 | 32006
- Subprogram violation: 'subprogram_period_plan' (37583.50) exceeds limit 'subprogram_annual_plan' (0.00) by 37583.50 for ՀՀ կրթության, գիտության, մշակույթի և սպորտի նախարարություն | 1196 | 12001
- Subprogram violation: 'subprogram_period_plan' (33351.70) exceeds limit 'subprogram_annual_plan' (25523.70) by 7828.00 for ՀՀ ֆինանսների նախարարություն | 1031 | 11002
- Subprogram violation: 'subprogram_period_plan' (22000.00) exceeds limit 'subprogram_annual_plan' (0.00) by 22000.00 for ՀՀ պետական եկամուտների կոմիտե | 1023 | 11015
- Subprogram violation: 'subprogram_period_plan' (525000.00) exceeds limit 'subprogram_annual_plan' (0.00) by 525000.00 for ՀՀ կառավարություն | 1139 | 11004

---

For detailed information about validation checks and how to interpret results,
see [docs/validation.md](../../docs/validation.md).
