# Validation Report: 2019_SPENDING_Q1.csv

**Source Type:** SPENDING_Q1
**File:** 2019_SPENDING_Q1.csv
**Generated:** 2025-12-05 15:24:15

## Summary

### Check Status

- **Total Rules:** 47
- **Passed:** 43 ✅
- **With Warnings:** 4 ⚠️
- **With Errors:** 0 ❌

### Issues Found

- **Errors:** 0
- **Warnings:** 12 ⚠️

## ✅ Passed Checks

- **empty_identifiers**
- **empty_identifiers**
- **empty_identifiers**
- **execution_exceeds_100**
- **execution_exceeds_100**
- **execution_exceeds_100**
- **hierarchical_totals**
- **hierarchical_totals**
- **hierarchical_totals**
- **hierarchical_totals**
- **hierarchical_totals**
- **hierarchical_totals**
- **hierarchical_totals**
- **hierarchical_totals**
- **hierarchical_totals**
- **hierarchical_totals**
- **hierarchical_totals**
- **hierarchical_totals**
- **hierarchical_totals**
- **hierarchical_totals**
- **hierarchical_totals**
- **missing_financial_data**
- **missing_financial_data**
- **missing_financial_data**
- **missing_financial_data**
- **negative_percentages**
- **negative_percentages**
- **negative_percentages**
- **negative_percentages**
- **negative_totals**
- **percentage_calculation**
- **percentage_calculation**
- **percentage_calculation**
- **percentage_calculation**
- **percentage_calculation**
- **percentage_calculation**
- **percentage_calculation**
- **percentage_calculation**
- **period_vs_annual**
- **period_vs_annual**
- **period_vs_annual**
- **period_vs_annual**
- **required_fields**

## ⚠️ Warnings

### ⚠️ execution_exceeds_100 (4 failures)

- Row 15: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (145.90%) in ՀՀ վարչապետի  աշխատակազմ | 1019 | 12002
- Row 231: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (9933.20%) in ՀՀ տնտեսական զարգացման և ներդրումների նախարարություն | 1079 | 31002
- Row 15: Execution > 100% for 'subprogram_actual_vs_rev_period_plan' (145.90%) in ՀՀ վարչապետի  աշխատակազմ | 1019 | 12002
- Row 16: Execution > 100% for 'subprogram_actual_vs_rev_period_plan' (446.00%) in ՀՀ վարչապետի  աշխատակազմ | 1019 | 12003

### ⚠️ negative_totals (1 failures)

- State_body field 'state_body_actual' has negative value: -7565.86 for ՀՀ տնտեսական զարգացման և ներդրումների նախարարության պետական գույքի կառավարման կոմիտե | 9975 | 99100

### ⚠️ negative_totals (2 failures)

- Program field 'program_actual' has negative value: -94.85 for ՀՀ արտակարգ իրավիճակների նախարարություն | 9995 | 99100
- Program field 'program_actual' has negative value: -7565.86 for ՀՀ տնտեսական զարգացման և ներդրումների նախարարության պետական գույքի կառավարման կոմիտե | 9975 | 99100

### ⚠️ negative_totals (5 failures)

- Subprogram field 'subprogram_annual_plan' has negative value: -1276.00 for ՀՀ տնտեսական զարգացման և ներդրումների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_rev_annual_plan' has negative value: -1276.00 for ՀՀ տնտեսական զարգացման և ներդրումների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_actual' has negative value: -126747.38 for ՀՀ տնտեսական զարգացման և ներդրումների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_actual' has negative value: -94.85 for ՀՀ արտակարգ իրավիճակների նախարարություն | 9995 | 99100
- Subprogram field 'subprogram_actual' has negative value: -7565.86 for ՀՀ տնտեսական զարգացման և ներդրումների նախարարության պետական գույքի կառավարման կոմիտե | 9975 | 99100

---

For detailed information about validation checks and how to interpret results,
see [docs/validation.md](https://github.com/gituzh/armenian-budget-tools/blob/main/docs/validation.md).
