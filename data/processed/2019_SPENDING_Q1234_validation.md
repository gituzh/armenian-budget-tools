# Validation Report: 2019_SPENDING_Q1234.csv

**Source Type:** SPENDING_Q1234
**File:** 2019_SPENDING_Q1234.csv
**Generated:** 2026-11-22 01:42:42

## Summary

### Check Status

- **Total Rules:** 39
- **Passed:** 21 ✅
- **With Warnings:** 3 ⚠️
- **With Errors:** 15 ❌

### Issues Found

- **Errors:** 42 ❌
- **Warnings:** 9 ⚠️

## ✅ Passed Checks

- **duplicate_records** (subprogram rows)
- **empty_identifiers** (state_body)
- **empty_identifiers** (program)
- **empty_identifiers** (subprogram)
- **execution_exceeds_100** (overall)
- **execution_exceeds_100** (state_body)
- **execution_exceeds_100** (program)
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
- **required_fields**

## ⚠️ Warnings

### ⚠️ execution_exceeds_100: subprogram (2 failures)

- Row 111: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (355.20%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1019 | 12002
- Row 172: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (54852.50%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002

### ⚠️ negative_totals: program (1 failures)

- Program field 'program_actual' has negative value: -1198.40 for ՀՀ արտակարգ իրավիճակների նախարարություն | 9995 | 99100

### ⚠️ negative_totals: subprogram (6 failures)

- Subprogram field 'subprogram_annual_plan' has negative value: -1276.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_rev_annual_plan' has negative value: -1276.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_rev_annual_plan' has negative value: -21946.50 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 9017 | 31002
- Subprogram field 'subprogram_actual' has negative value: -699917.70 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_actual' has negative value: -21946.50 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 9017 | 31002
- Subprogram field 'subprogram_actual' has negative value: -1198.40 for ՀՀ արտակարգ իրավիճակների նախարարություն | 9995 | 99100

## ❌ Errors

### ❌ duplicate_records: state_body blocks (4 failures)

- State body 'ՀՀ վարչապետի աշխատակազմ' appears in 2 separate blocks (CSV lines 14-70, 975-981)
- State body 'ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն' appears in 2 separate blocks (CSV lines 104-219, 475-526)
- State body 'ՀՀ էկոնոմիկայի նախարարություն' appears in 2 separate blocks (CSV lines 345-365, 422-474)
- State body 'ՀՀ կրթության, գիտության, մշակույթի և սպորտի նախարարություն' appears in 2 separate blocks (CSV lines 527-719, 901-950)

### ❌ duplicate_records: program blocks (4 failures)

- State body 'ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն' program 1004 appears in 2 separate blocks (CSV lines 109, 475-491)
- State body 'ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն' program 1027 appears in 2 separate blocks (CSV lines 115, 494)
- State body 'ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն' program 1072 appears in 2 separate blocks (CSV lines 157-158, 497-510)
- State body 'ՀՀ կրթության, գիտության, մշակույթի և սպորտի նախարարություն' program 1115 appears in 2 separate blocks (CSV lines 555, 930-932)

### ❌ duplicate_records: program totals (4 failures)

- State body 'ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն' program 1004 totals differ across its rows: program_annual_plan values [0.0, 16901296.9]; program_rev_annual_plan values [85680.0, 26020510.6]; program_actual values [0.0, 21884551.0]; program_actual_vs_rev_annual_plan values [0.0, 0.841] (distinct total sets start at CSV lines 109, 475)
- State body 'ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն' program 1027 totals differ across its rows: program_annual_plan values [0.0, 336497.3]; program_rev_annual_plan values [65607.7, 336497.3]; program_actual values [26100.9, 323725.4]; program_actual_vs_rev_annual_plan values [0.398, 0.962] (distinct total sets start at CSV lines 115, 494)
- State body 'ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն' program 1072 totals differ across its rows: program_annual_plan values [0.0, 12610054.8]; program_rev_annual_plan values [3591908.0, 8316967.1]; program_actual values [3591908.0, 1989069.0]; program_actual_vs_rev_annual_plan values [1.0, 0.239] (distinct total sets start at CSV lines 157, 497)
- State body 'ՀՀ կրթության, գիտության, մշակույթի և սպորտի նախարարություն' program 1115 totals differ across its rows: program_annual_plan values [0.0, 978187.4]; program_rev_annual_plan values [54509.4, 1243374.7]; program_actual values [54509.4, 1084496.7]; program_actual_vs_rev_annual_plan values [1.0, 0.872] (distinct total sets start at CSV lines 555, 930)

### ❌ duplicate_records: state_body whitespace variants (1 failures)

- State body 'ՀՀ վարչապետի աշխատակազմ' has 2 whitespace variants: 'ՀՀ վարչապետի  աշխատակազմ' (first CSV line 14), 'ՀՀ վարչապետի աշխատակազմ' (first CSV line 975)

### ❌ duplicate_records: state_body totals (4 failures)

- State body 'ՀՀ վարչապետի աշխատակազմ' totals differ across its rows: state_body_annual_plan values [16668356.9, 639558.5]; state_body_rev_annual_plan values [18372581.3, 564758.2]; state_body_actual values [14120700.9, 386398.0]; state_body_actual_vs_rev_annual_plan values [0.769, 0.684] (distinct total sets start at CSV lines 14, 975)
- State body 'ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն' totals differ across its rows: state_body_annual_plan values [147577637.6, 47947633.2]; state_body_rev_annual_plan values [175528847.3, 51344887.1]; state_body_actual values [139336023.3, 32308095.0]; state_body_actual_vs_rev_annual_plan values [0.794, 0.629] (distinct total sets start at CSV lines 104, 475)
- State body 'ՀՀ էկոնոմիկայի նախարարություն' totals differ across its rows: state_body_annual_plan values [9322213.5, 16085337.3]; state_body_rev_annual_plan values [8969716.5, 12777853.9]; state_body_actual values [4356519.0, 8133979.5]; state_body_actual_vs_rev_annual_plan values [0.486, 0.637] (distinct total sets start at CSV lines 345, 422)
- State body 'ՀՀ կրթության, գիտության, մշակույթի և սպորտի նախարարություն' totals differ across its rows: state_body_annual_plan values [141696953.9, 15933738.6, 4361319.5]; state_body_rev_annual_plan values [144261843.8, 18884769.8, 5448873.3]; state_body_actual values [134875641.9, 17563849.3, 4868153.7]; state_body_actual_vs_rev_annual_plan values [0.935, 0.93, 0.893] (distinct total sets start at CSV lines 527, 654, 901)

### ❌ hierarchical_totals: overall_actual vs state_body_actual (1 failures)

- Overall overall_actual: expected 1566562784.7000003, got 1629436862.4, diff 62874077.69999981 (tolerance 2000.0)

### ❌ hierarchical_totals: state_body_actual vs program_actual (3 failures)

- ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն: expected 147446773.0, got 139336023.3, diff 8110749.699999988
- ՀՀ էկոնոմիկայի նախարարություն: expected 12490498.500000002, got 4356519.0, diff 8133979.500000002
- ՀՀ կրթության, գիտության, մշակույթի և սպորտի նախարարություն: expected 156223148.0, got 134875641.9, diff 21347506.099999994

### ❌ hierarchical_totals: program_actual vs subprogram_actual (4 failures)

- ՀՀ կրթության, գիտության, մշակույթի և սպորտի նախարարություն/Երիտասարդության ծրագիր: expected 1139006.1, got 54509.4, diff 1084496.7000000002
- ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն/Կոլեկտորադրենաժային ծառայություններ: expected 349826.30000000005, got 26100.9, diff 323725.4
- ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն/Ոռոգման համակարգի առողջացում: expected 21884551.1, got 0.0, diff 21884551.1
- ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն/Ջրամատակարարաման և ջրահեռացման բարելավում: expected 5580977.100000001, got 3591908.0, diff 1989069.1000000006

### ❌ hierarchical_totals: overall_annual_plan vs state_body_annual_plan (1 failures)

- Overall overall_annual_plan: expected 1563735093.6999998, got 1648063122.3, diff 84328028.60000014 (tolerance 2000.0)

### ❌ hierarchical_totals: state_body_annual_plan vs program_annual_plan (3 failures)

- ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն: expected 165677421.79999995, got 147577637.6, diff 18099784.19999996
- ՀՀ էկոնոմիկայի նախարարություն: expected 25407550.799999997, got 9322213.5, diff 16085337.299999997
- ՀՀ կրթության, գիտության, մշակույթի և սպորտի նախարարություն: expected 161013824.60000002, got 141696953.9, diff 19316870.700000018

### ❌ hierarchical_totals: program_annual_plan vs subprogram_annual_plan (4 failures)

- ՀՀ կրթության, գիտության, մշակույթի և սպորտի նախարարություն/Երիտասարդության ծրագիր: expected 978187.4, got 0.0, diff 978187.4
- ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն/Կոլեկտորադրենաժային ծառայություններ: expected 336497.3, got 0.0, diff 336497.3
- ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն/Ոռոգման համակարգի առողջացում: expected 16901296.9, got 0.0, diff 16901296.9
- ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն/Ջրամատակարարաման և ջրահեռացման բարելավում: expected 12610054.8, got 0.0, diff 12610054.8

### ❌ hierarchical_totals: overall_rev_annual_plan vs state_body_rev_annual_plan (1 failures)

- Overall overall_rev_annual_plan: expected 1674463746.6000001, got 1762920130.7, diff 88456384.0999999 (tolerance 2000.0)

### ❌ hierarchical_totals: state_body_rev_annual_plan vs program_rev_annual_plan (3 failures)

- ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն: expected 192199759.4, got 175528847.3, diff 16670912.099999994
- ՀՀ էկոնոմիկայի նախարարություն: expected 21747570.399999995, got 8969716.5, diff 12777853.899999995
- ՀՀ կրթության, գիտության, մշակույթի և սպորտի նախարարություն: expected 167352112.20000002, got 144261843.8, diff 23090268.400000006

### ❌ hierarchical_totals: program_rev_annual_plan vs subprogram_rev_annual_plan (4 failures)

- ՀՀ կրթության, գիտության, մշակույթի և սպորտի նախարարություն/Երիտասարդության ծրագիր: expected 1297884.1, got 54509.4, diff 1243374.7000000002
- ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն/Կոլեկտորադրենաժային ծառայություններ: expected 402105.0, got 65607.7, diff 336497.3
- ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն/Ոռոգման համակարգի առողջացում: expected 26106190.599999998, got 85680.0, diff 26020510.599999998
- ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն/Ջրամատակարարաման և ջրահեռացման բարելավում: expected 11908875.1, got 3591908.0, diff 8316967.1

### ❌ percentage_calculation: subprogram_actual_vs_rev_annual_plan (1 failures)

- Row 871: Mismatch for 'subprogram_actual_vs_rev_annual_plan'. Expected: 1.0000, Reported: 0.9880, Diff: 0.0120 in ՀՀ բարձր տեխնոլոգիական արդյունաբերության նախարարություն | 1100 | 11004

---

For detailed information about validation checks and how to interpret results,
see [docs/validation.md](../../docs/validation.md).
