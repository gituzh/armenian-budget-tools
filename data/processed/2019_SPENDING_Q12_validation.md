# Validation Report: 2019_SPENDING_Q12.csv

**Source Type:** SPENDING_Q12
**File:** 2019_SPENDING_Q12.csv
**Generated:** 2026-11-22 01:42:41

## Summary

### Check Status

- **Total Rules:** 53
- **Passed:** 36 ✅
- **With Warnings:** 4 ⚠️
- **With Errors:** 13 ❌

### Issues Found

- **Errors:** 15 ❌
- **Warnings:** 11 ⚠️

## ✅ Passed Checks

- **duplicate_records** (program blocks)
- **duplicate_records** (subprogram rows)
- **duplicate_records** (program totals)
- **empty_identifiers** (state_body)
- **empty_identifiers** (program)
- **empty_identifiers** (subprogram)
- **execution_exceeds_100** (overall)
- **execution_exceeds_100** (state_body)
- **execution_exceeds_100** (program)
- **hierarchical_totals** (program_actual vs subprogram_actual)
- **hierarchical_totals** (program_annual_plan vs subprogram_annual_plan)
- **hierarchical_totals** (program_period_plan vs subprogram_period_plan)
- **hierarchical_totals** (program_rev_annual_plan vs subprogram_rev_annual_plan)
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

### ⚠️ execution_exceeds_100: subprogram (3 failures)

- Row 17: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (355.20%) in ՀՀ վարչապետի  աշխատակազմ | 1019 | 12002
- Row 295: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (17969.00%) in ՀՀ էկոնոմիկայի նախարարություն | 1079 | 31002
- Row 17: Execution > 100% for 'subprogram_actual_vs_rev_period_plan' (355.20%) in ՀՀ վարչապետի  աշխատակազմ | 1019 | 12002

### ⚠️ negative_totals: state_body (1 failures)

- State_body field 'state_body_actual' has negative value: -14769.39 for ՀՀ տնտեսական զարգացման և ներդրումների նախարարության պետական գույքի կառավարման կոմիտե | 9975 | 99100

### ⚠️ negative_totals: program (2 failures)

- Program field 'program_actual' has negative value: -94.85 for ՀՀ արտակարգ իրավիճակների նախարարություն | 9995 | 99100
- Program field 'program_actual' has negative value: -14769.39 for ՀՀ տնտեսական զարգացման և ներդրումների նախարարության պետական գույքի կառավարման կոմիտե | 9975 | 99100

### ⚠️ negative_totals: subprogram (5 failures)

- Subprogram field 'subprogram_annual_plan' has negative value: -1276.00 for ՀՀ էկոնոմիկայի նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_rev_annual_plan' has negative value: -1276.00 for ՀՀ էկոնոմիկայի նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_actual' has negative value: -229284.34 for ՀՀ էկոնոմիկայի նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_actual' has negative value: -94.85 for ՀՀ արտակարգ իրավիճակների նախարարություն | 9995 | 99100
- Subprogram field 'subprogram_actual' has negative value: -14769.39 for ՀՀ տնտեսական զարգացման և ներդրումների նախարարության պետական գույքի կառավարման կոմիտե | 9975 | 99100

## ❌ Errors

### ❌ duplicate_records: state_body blocks (2 failures)

- State body 'ՀՀ վարչապետի աշխատակազմ' appears in 2 separate blocks (CSV lines 11-62, 816-831)
- State body 'ՀՀ էկոնոմիկայի նախարարություն' appears in 2 separate blocks (CSV lines 279-310, 356-407)

### ❌ duplicate_records: state_body whitespace variants (1 failures)

- State body 'ՀՀ վարչապետի աշխատակազմ' has 2 whitespace variants: 'ՀՀ վարչապետի  աշխատակազմ' (first CSV line 11), 'ՀՀ վարչապետի աշխատակազմ' (first CSV line 816)

### ❌ duplicate_records: state_body totals (2 failures)

- State body 'ՀՀ վարչապետի աշխատակազմ' totals differ across its rows: state_body_annual_plan values [20439178.8, 1153554.8]; state_body_rev_annual_plan values [21463749.92, 1153554.8]; state_body_period_plan values [9046954.3, 447429.2]; state_body_rev_period_plan values [10059490.52, 447429.2]; state_body_actual values [5651189.5, 177601.4]; state_body_actual_vs_rev_annual_plan values [0.263, 0.154]; state_body_actual_vs_rev_period_plan values [0.562, 0.397] (distinct total sets start at CSV lines 11, 816)
- State body 'ՀՀ էկոնոմիկայի նախարարություն' totals differ across its rows: state_body_annual_plan values [10403510.2, 16085337.3]; state_body_rev_annual_plan values [10639859.37, 16175000.56]; state_body_period_plan values [5445314.3, 7649008.5]; state_body_rev_period_plan values [5681663.47, 7762187.76]; state_body_actual values [2042579.47, 3174266.15]; state_body_actual_vs_rev_annual_plan values [0.192, 0.196]; state_body_actual_vs_rev_period_plan values [0.36, 0.409] (distinct total sets start at CSV lines 279, 356)

### ❌ hierarchical_totals: overall_actual vs state_body_actual (1 failures)

- Overall overall_actual: expected 633462930.31, got 636637196.46, diff 3174266.1500000954 (tolerance 2000.0)

### ❌ hierarchical_totals: state_body_actual vs program_actual (1 failures)

- ՀՀ էկոնոմիկայի նախարարություն: expected 5216845.62, got 2042579.47, diff 3174266.1500000004

### ❌ hierarchical_totals: overall_annual_plan vs state_body_annual_plan (1 failures)

- Overall overall_annual_plan: expected 1631977785.02, got 1648063122.32, diff 16085337.299999952 (tolerance 2000.0)

### ❌ hierarchical_totals: state_body_annual_plan vs program_annual_plan (1 failures)

- ՀՀ էկոնոմիկայի նախարարություն: expected 26488847.499999996, got 10403510.2, diff 16085337.299999997

### ❌ hierarchical_totals: overall_period_plan vs state_body_period_plan (1 failures)

- Overall overall_period_plan: expected 761847057.78, got 769496066.28, diff 7649008.5 (tolerance 2000.0)

### ❌ hierarchical_totals: state_body_period_plan vs program_period_plan (1 failures)

- ՀՀ էկոնոմիկայի նախարարություն: expected 13094322.800000004, got 5445314.3, diff 7649008.500000005

### ❌ hierarchical_totals: overall_rev_annual_plan vs state_body_rev_annual_plan (1 failures)

- Overall overall_rev_annual_plan: expected 1672550903.58, got 1688725904.14, diff 16175000.560000181 (tolerance 2000.0)

### ❌ hierarchical_totals: state_body_rev_annual_plan vs program_rev_annual_plan (1 failures)

- ՀՀ էկոնոմիկայի նախարարություն: expected 26814859.929999996, got 10639859.37, diff 16175000.559999997

### ❌ hierarchical_totals: overall_rev_period_plan vs state_body_rev_period_plan (1 failures)

- Overall overall_rev_period_plan: expected 790210142.3399999, got 797972330.1, diff 7762187.76000011 (tolerance 2000.0)

### ❌ hierarchical_totals: state_body_rev_period_plan vs program_rev_period_plan (1 failures)

- ՀՀ էկոնոմիկայի նախարարություն: expected 13443851.230000002, got 5681663.47, diff 7762187.760000003

---

For detailed information about validation checks and how to interpret results,
see [docs/validation.md](../../docs/validation.md).
