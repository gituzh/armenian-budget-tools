# Validation Report: 2019_SPENDING_Q1.csv

**Source Type:** SPENDING_Q1
**File:** 2019_SPENDING_Q1.csv
**Generated:** 2026-11-22 01:42:41

## Summary

### Check Status

- **Total Rules:** 53
- **Passed:** 49 ✅
- **With Warnings:** 4 ⚠️
- **With Errors:** 0 ❌

### Issues Found

- **Errors:** 0
- **Warnings:** 12 ⚠️

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
- **negative_percentages** (program)
- **negative_percentages** (subprogram)
- **negative_totals** (overall)
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
- **period_vs_annual** (subprogram)
- **required_fields**

## ⚠️ Warnings

### ⚠️ execution_exceeds_100: subprogram (4 failures)

- Row 15: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (145.90%) in ՀՀ վարչապետի  աշխատակազմ | 1019 | 12002
- Row 231: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (9933.20%) in ՀՀ տնտեսական զարգացման և ներդրումների նախարարություն | 1079 | 31002
- Row 15: Execution > 100% for 'subprogram_actual_vs_rev_period_plan' (145.90%) in ՀՀ վարչապետի  աշխատակազմ | 1019 | 12002
- Row 16: Execution > 100% for 'subprogram_actual_vs_rev_period_plan' (446.00%) in ՀՀ վարչապետի  աշխատակազմ | 1019 | 12003

### ⚠️ negative_totals: state_body (1 failures)

- State_body field 'state_body_actual' has negative value: -7565.86 for ՀՀ տնտեսական զարգացման և ներդրումների նախարարության պետական գույքի կառավարման կոմիտե | 9975 | 99100

### ⚠️ negative_totals: program (2 failures)

- Program field 'program_actual' has negative value: -94.85 for ՀՀ արտակարգ իրավիճակների նախարարություն | 9995 | 99100
- Program field 'program_actual' has negative value: -7565.86 for ՀՀ տնտեսական զարգացման և ներդրումների նախարարության պետական գույքի կառավարման կոմիտե | 9975 | 99100

### ⚠️ negative_totals: subprogram (5 failures)

- Subprogram field 'subprogram_annual_plan' has negative value: -1276.00 for ՀՀ տնտեսական զարգացման և ներդրումների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_rev_annual_plan' has negative value: -1276.00 for ՀՀ տնտեսական զարգացման և ներդրումների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_actual' has negative value: -126747.38 for ՀՀ տնտեսական զարգացման և ներդրումների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_actual' has negative value: -94.85 for ՀՀ արտակարգ իրավիճակների նախարարություն | 9995 | 99100
- Subprogram field 'subprogram_actual' has negative value: -7565.86 for ՀՀ տնտեսական զարգացման և ներդրումների նախարարության պետական գույքի կառավարման կոմիտե | 9975 | 99100

---

For detailed information about validation checks and how to interpret results,
see [docs/validation.md](../../docs/validation.md).
