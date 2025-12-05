# Validation Report: 2019_SPENDING_Q12.csv

**Source Type:** SPENDING_Q12
**File:** 2019_SPENDING_Q12.csv
**Generated:** 2025-11-24 18:40:31

## Summary

### Check Status

- **Total Rules:** 47
- **Passed:** 32 ✅
- **With Warnings:** 4 ⚠️
- **With Errors:** 11 ❌

### Issues Found

- **Errors:** 12 ❌
- **Warnings:** 11 ⚠️

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
- **required_fields**

## ⚠️ Warnings

### ⚠️ execution_exceeds_100 (3 failures)

- Row 17: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (355.20%) in ՀՀ վարչապետի  աշխատակազմ | 1019 | 12002
- Row 295: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (17969.00%) in ՀՀ էկոնոմիկայի նախարարություն | 1079 | 31002
- Row 17: Execution > 100% for 'subprogram_actual_vs_rev_period_plan' (355.20%) in ՀՀ վարչապետի  աշխատակազմ | 1019 | 12002

### ⚠️ negative_totals (1 failures)

- State_body field 'state_body_actual' has negative value: -14769.39 for ՀՀ տնտեսական զարգացման և ներդրումների նախարարության պետական գույքի կառավարման կոմիտե | 9975 | 99100

### ⚠️ negative_totals (2 failures)

- Program field 'program_actual' has negative value: -94.85 for ՀՀ արտակարգ իրավիճակների նախարարություն | 9995 | 99100
- Program field 'program_actual' has negative value: -14769.39 for ՀՀ տնտեսական զարգացման և ներդրումների նախարարության պետական գույքի կառավարման կոմիտե | 9975 | 99100

### ⚠️ negative_totals (5 failures)

- Subprogram field 'subprogram_annual_plan' has negative value: -1276.00 for ՀՀ էկոնոմիկայի նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_rev_annual_plan' has negative value: -1276.00 for ՀՀ էկոնոմիկայի նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_actual' has negative value: -229284.34 for ՀՀ էկոնոմիկայի նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_actual' has negative value: -94.85 for ՀՀ արտակարգ իրավիճակների նախարարություն | 9995 | 99100
- Subprogram field 'subprogram_actual' has negative value: -14769.39 for ՀՀ տնտեսական զարգացման և ներդրումների նախարարության պետական գույքի կառավարման կոմիտե | 9975 | 99100

## ❌ Errors

### ❌ hierarchical_totals (1 failures)

- Overall overall_actual: expected 633462930.31, got 636637196.46, diff 3174266.1500000954 (tolerance 5.0)

### ❌ hierarchical_totals (1 failures)

- ՀՀ էկոնոմիկայի նախարարություն: expected 5216845.62, got 2042579.47, diff 3174266.1500000004

### ❌ hierarchical_totals (1 failures)

- Overall overall_annual_plan: expected 1631977785.02, got 1648063122.32, diff 16085337.299999952 (tolerance 5.0)

### ❌ hierarchical_totals (1 failures)

- ՀՀ էկոնոմիկայի նախարարություն: expected 26488847.499999996, got 10403510.2, diff 16085337.299999997

### ❌ hierarchical_totals (1 failures)

- Overall overall_period_plan: expected 761847057.78, got 769496066.28, diff 7649008.5 (tolerance 5.0)

### ❌ hierarchical_totals (1 failures)

- ՀՀ էկոնոմիկայի նախարարություն: expected 13094322.800000004, got 5445314.3, diff 7649008.500000005

### ❌ hierarchical_totals (1 failures)

- Overall overall_rev_annual_plan: expected 1672550903.58, got 1688725904.14, diff 16175000.560000181 (tolerance 5.0)

### ❌ hierarchical_totals (1 failures)

- ՀՀ էկոնոմիկայի նախարարություն: expected 26814859.929999996, got 10639859.37, diff 16175000.559999997

### ❌ hierarchical_totals (1 failures)

- Overall overall_rev_period_plan: expected 790210142.3399999, got 797972330.1, diff 7762187.76000011 (tolerance 5.0)

### ❌ hierarchical_totals (1 failures)

- ՀՀ էկոնոմիկայի նախարարություն: expected 13443851.230000002, got 5681663.47, diff 7762187.760000003

### ❌ period_vs_annual (2 failures)

- Subprogram violation: 'subprogram_period_plan' (0.00) > 'subprogram_annual_plan' (-1276.00) by 1276.00 for ՀՀ էկոնոմիկայի նախարարություն | 1079 | 31002
- Subprogram violation: 'subprogram_rev_period_plan' (0.00) > 'subprogram_rev_annual_plan' (-1276.00) by 1276.00 for ՀՀ էկոնոմիկայի նախարարություն | 1079 | 31002

---

For detailed information about validation checks and how to interpret results,
see [docs/validation.md](https://github.com/gituzh/armenian-budget-tools/blob/main/docs/validation.md).
