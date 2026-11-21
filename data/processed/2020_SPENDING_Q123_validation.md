# Validation Report: 2020_SPENDING_Q123.csv

**Source Type:** SPENDING_Q123
**File:** 2020_SPENDING_Q123.csv
**Generated:** 2026-11-22 01:42:42

## Summary

### Check Status

- **Total Rules:** 53
- **Passed:** 47 ✅
- **With Warnings:** 6 ⚠️
- **With Errors:** 0 ❌

### Issues Found

- **Errors:** 0
- **Warnings:** 79 ⚠️

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
- **required_fields**

## ⚠️ Warnings

### ⚠️ execution_exceeds_100: subprogram (2 failures)

- Row 211: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (4230.20%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Row 211: Execution > 100% for 'subprogram_actual_vs_rev_period_plan' (6327.80%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002

### ⚠️ negative_percentages: program (20 failures)

- Row 203: Negative percentage for 'program_actual_vs_rev_annual_plan' (-11.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Row 204: Negative percentage for 'program_actual_vs_rev_annual_plan' (-11.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Row 205: Negative percentage for 'program_actual_vs_rev_annual_plan' (-11.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Row 206: Negative percentage for 'program_actual_vs_rev_annual_plan' (-11.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11012
- Row 207: Negative percentage for 'program_actual_vs_rev_annual_plan' (-11.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Row 208: Negative percentage for 'program_actual_vs_rev_annual_plan' (-11.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12001
- Row 209: Negative percentage for 'program_actual_vs_rev_annual_plan' (-11.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12002
- Row 210: Negative percentage for 'program_actual_vs_rev_annual_plan' (-11.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Row 211: Negative percentage for 'program_actual_vs_rev_annual_plan' (-11.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Row 212: Negative percentage for 'program_actual_vs_rev_annual_plan' (-11.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31004
- Row 203: Negative percentage for 'program_actual_vs_rev_period_plan' (-14.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Row 204: Negative percentage for 'program_actual_vs_rev_period_plan' (-14.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Row 205: Negative percentage for 'program_actual_vs_rev_period_plan' (-14.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Row 206: Negative percentage for 'program_actual_vs_rev_period_plan' (-14.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11012
- Row 207: Negative percentage for 'program_actual_vs_rev_period_plan' (-14.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Row 208: Negative percentage for 'program_actual_vs_rev_period_plan' (-14.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12001
- Row 209: Negative percentage for 'program_actual_vs_rev_period_plan' (-14.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12002
- Row 210: Negative percentage for 'program_actual_vs_rev_period_plan' (-14.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Row 211: Negative percentage for 'program_actual_vs_rev_period_plan' (-14.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Row 212: Negative percentage for 'program_actual_vs_rev_period_plan' (-14.00%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31004

### ⚠️ negative_totals: program (10 failures)

- Program field 'program_actual' has negative value: -168517.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Program field 'program_actual' has negative value: -168517.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Program field 'program_actual' has negative value: -168517.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11007
- Program field 'program_actual' has negative value: -168517.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11012
- Program field 'program_actual' has negative value: -168517.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Program field 'program_actual' has negative value: -168517.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12001
- Program field 'program_actual' has negative value: -168517.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 12002
- Program field 'program_actual' has negative value: -168517.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31001
- Program field 'program_actual' has negative value: -168517.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Program field 'program_actual' has negative value: -168517.20 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31004

### ⚠️ negative_totals: subprogram (5 failures)

- Subprogram field 'subprogram_annual_plan' has negative value: -20066.40 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_rev_annual_plan' has negative value: -31152.30 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_period_plan' has negative value: -20066.40 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_rev_period_plan' has negative value: -20825.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_actual' has negative value: -1317804.60 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002

### ⚠️ period_vs_annual: program (32 failures)

- Program violation: 'program_period_plan' (9360166.60) exceeds limit 'program_annual_plan' (7187414.20) by 2172752.40 for ՀՀ վարչապետի  աշխատակազմ | 1136 | 11001
- Program violation: 'program_period_plan' (9360166.60) exceeds limit 'program_annual_plan' (7187414.20) by 2172752.40 for ՀՀ վարչապետի  աշխատակազմ | 1136 | 11003
- Program violation: 'program_period_plan' (9360166.60) exceeds limit 'program_annual_plan' (7187414.20) by 2172752.40 for ՀՀ վարչապետի  աշխատակազմ | 1136 | 11004
- Program violation: 'program_period_plan' (9360166.60) exceeds limit 'program_annual_plan' (7187414.20) by 2172752.40 for ՀՀ վարչապետի  աշխատակազմ | 1136 | 11005
- Program violation: 'program_period_plan' (9360166.60) exceeds limit 'program_annual_plan' (7187414.20) by 2172752.40 for ՀՀ վարչապետի  աշխատակազմ | 1136 | 11006
- Program violation: 'program_period_plan' (9360166.60) exceeds limit 'program_annual_plan' (7187414.20) by 2172752.40 for ՀՀ վարչապետի  աշխատակազմ | 1136 | 11007
- Program violation: 'program_period_plan' (9360166.60) exceeds limit 'program_annual_plan' (7187414.20) by 2172752.40 for ՀՀ վարչապետի  աշխատակազմ | 1136 | 11009
- Program violation: 'program_period_plan' (9360166.60) exceeds limit 'program_annual_plan' (7187414.20) by 2172752.40 for ՀՀ վարչապետի  աշխատակազմ | 1136 | 11010
- Program violation: 'program_period_plan' (9360166.60) exceeds limit 'program_annual_plan' (7187414.20) by 2172752.40 for ՀՀ վարչապետի  աշխատակազմ | 1136 | 11011
- Program violation: 'program_period_plan' (9360166.60) exceeds limit 'program_annual_plan' (7187414.20) by 2172752.40 for ՀՀ վարչապետի  աշխատակազմ | 1136 | 12006
- Program violation: 'program_period_plan' (9360166.60) exceeds limit 'program_annual_plan' (7187414.20) by 2172752.40 for ՀՀ վարչապետի  աշխատակազմ | 1136 | 12007
- Program violation: 'program_period_plan' (9360166.60) exceeds limit 'program_annual_plan' (7187414.20) by 2172752.40 for ՀՀ վարչապետի  աշխատակազմ | 1136 | 31001
- Program violation: 'program_period_plan' (9360166.60) exceeds limit 'program_annual_plan' (7187414.20) by 2172752.40 for ՀՀ վարչապետի  աշխատակազմ | 1136 | 31002
- Program violation: 'program_period_plan' (9360166.60) exceeds limit 'program_annual_plan' (7187414.20) by 2172752.40 for ՀՀ վարչապետի  աշխատակազմ | 1136 | 31003
- Program violation: 'program_period_plan' (9360166.60) exceeds limit 'program_annual_plan' (7187414.20) by 2172752.40 for ՀՀ վարչապետի  աշխատակազմ | 1136 | 31004
- Program violation: 'program_period_plan' (2202917.10) exceeds limit 'program_annual_plan' (1984337.90) by 218579.20 for ՀՀ աշխատանքի և սոցիալական հարցերի նախարարություն | 1088 | 11001
- Program violation: 'program_period_plan' (2202917.10) exceeds limit 'program_annual_plan' (1984337.90) by 218579.20 for ՀՀ աշխատանքի և սոցիալական հարցերի նախարարություն | 1088 | 11002
- Program violation: 'program_period_plan' (2202917.10) exceeds limit 'program_annual_plan' (1984337.90) by 218579.20 for ՀՀ աշխատանքի և սոցիալական հարցերի նախարարություն | 1088 | 11004
- Program violation: 'program_period_plan' (2202917.10) exceeds limit 'program_annual_plan' (1984337.90) by 218579.20 for ՀՀ աշխատանքի և սոցիալական հարցերի նախարարություն | 1088 | 11006
- Program violation: 'program_period_plan' (2202917.10) exceeds limit 'program_annual_plan' (1984337.90) by 218579.20 for ՀՀ աշխատանքի և սոցիալական հարցերի նախարարություն | 1088 | 11007
- Program violation: 'program_period_plan' (2202917.10) exceeds limit 'program_annual_plan' (1984337.90) by 218579.20 for ՀՀ աշխատանքի և սոցիալական հարցերի նախարարություն | 1088 | 12001
- Program violation: 'program_period_plan' (2202917.10) exceeds limit 'program_annual_plan' (1984337.90) by 218579.20 for ՀՀ աշխատանքի և սոցիալական հարցերի նախարարություն | 1088 | 12002
- Program violation: 'program_period_plan' (2202917.10) exceeds limit 'program_annual_plan' (1984337.90) by 218579.20 for ՀՀ աշխատանքի և սոցիալական հարցերի նախարարություն | 1088 | 12003
- Program violation: 'program_period_plan' (2202917.10) exceeds limit 'program_annual_plan' (1984337.90) by 218579.20 for ՀՀ աշխատանքի և սոցիալական հարցերի նախարարություն | 1088 | 12004
- Program violation: 'program_period_plan' (2202917.10) exceeds limit 'program_annual_plan' (1984337.90) by 218579.20 for ՀՀ աշխատանքի և սոցիալական հարցերի նախարարություն | 1088 | 12005
- Program violation: 'program_period_plan' (2202917.10) exceeds limit 'program_annual_plan' (1984337.90) by 218579.20 for ՀՀ աշխատանքի և սոցիալական հարցերի նախարարություն | 1088 | 12006
- Program violation: 'program_period_plan' (2202917.10) exceeds limit 'program_annual_plan' (1984337.90) by 218579.20 for ՀՀ աշխատանքի և սոցիալական հարցերի նախարարություն | 1088 | 12008
- Program violation: 'program_period_plan' (2202917.10) exceeds limit 'program_annual_plan' (1984337.90) by 218579.20 for ՀՀ աշխատանքի և սոցիալական հարցերի նախարարություն | 1088 | 12009
- Program violation: 'program_period_plan' (2202917.10) exceeds limit 'program_annual_plan' (1984337.90) by 218579.20 for ՀՀ աշխատանքի և սոցիալական հարցերի նախարարություն | 1088 | 12010
- Program violation: 'program_period_plan' (2202917.10) exceeds limit 'program_annual_plan' (1984337.90) by 218579.20 for ՀՀ աշխատանքի և սոցիալական հարցերի նախարարություն | 1088 | 12011
- Program violation: 'program_period_plan' (2202917.10) exceeds limit 'program_annual_plan' (1984337.90) by 218579.20 for ՀՀ աշխատանքի և սոցիալական հարցերի նախարարություն | 1088 | 12013
- Program violation: 'program_rev_period_plan' (255880.00) exceeds limit 'program_rev_annual_plan' (117330.20) by 138549.80 for ՀՀ կառավարություն | 1139 | 11001

### ⚠️ period_vs_annual: subprogram (10 failures)

- Subprogram violation: 'subprogram_period_plan' (1585956.00) exceeds limit 'subprogram_annual_plan' (0.00) by 1585956.00 for ՀՀ վարչապետի  աշխատակազմ | 1136 | 11011
- Subprogram violation: 'subprogram_period_plan' (1354536.90) exceeds limit 'subprogram_annual_plan' (0.00) by 1354536.90 for ՀՀ վարչապետի  աշխատակազմ | 1136 | 31003
- Subprogram violation: 'subprogram_period_plan' (1355280.00) exceeds limit 'subprogram_annual_plan' (0.00) by 1355280.00 for ՀՀ վարչապետի  աշխատակազմ | 1136 | 31004
- Subprogram violation: 'subprogram_period_plan' (180000.00) exceeds limit 'subprogram_annual_plan' (0.00) by 180000.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1049 | 11015
- Subprogram violation: 'subprogram_period_plan' (158350.10) exceeds limit 'subprogram_annual_plan' (0.00) by 158350.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1167 | 11006
- Subprogram violation: 'subprogram_period_plan' (2250.00) exceeds limit 'subprogram_annual_plan' (0.00) by 2250.00 for ՀՀ աշխատանքի և սոցիալական հարցերի նախարարություն | 1088 | 11007
- Subprogram violation: 'subprogram_period_plan' (470000.00) exceeds limit 'subprogram_annual_plan' (70000.00) by 400000.00 for ՀՀ աշխատանքի և սոցիալական հարցերի նախարարություն | 1088 | 12013
- Subprogram violation: 'subprogram_period_plan' (602.00) exceeds limit 'subprogram_annual_plan' (0.00) by 602.00 for ՀՀ աշխատանքի և սոցիալական հարցերի նախարարություն | 1098 | 12003
- Subprogram violation: 'subprogram_period_plan' (270000.00) exceeds limit 'subprogram_annual_plan' (200000.00) by 70000.00 for ՀՀ բարձր տեխնոլոգիական արդյունաբերության նախարարություն | 1043 | 11004
- Subprogram violation: 'subprogram_rev_period_plan' (255880.00) exceeds limit 'subprogram_rev_annual_plan' (117330.20) by 138549.80 for ՀՀ կառավարություն | 1139 | 11001

---

For detailed information about validation checks and how to interpret results,
see [docs/validation.md](../../docs/validation.md).
