# Validation Report: 2019_SPENDING_Q1234.csv

**Source Type:** SPENDING_Q1234
**File:** 2019_SPENDING_Q1234.csv
**Generated:** 2025-12-10 23:40:10

## Summary

### Check Status

- **Total Rules:** 33
- **Passed:** 20 ✅
- **With Warnings:** 3 ⚠️
- **With Errors:** 10 ❌

### Issues Found

- **Errors:** 25 ❌
- **Warnings:** 9 ⚠️

## ✅ Passed Checks

- **empty_identifiers**
- **empty_identifiers**
- **empty_identifiers**
- **execution_exceeds_100**
- **execution_exceeds_100**
- **execution_exceeds_100**
- **missing_financial_data**
- **missing_financial_data**
- **missing_financial_data**
- **missing_financial_data**
- **negative_percentages**
- **negative_percentages**
- **negative_percentages**
- **negative_percentages**
- **negative_totals**
- **negative_totals**
- **percentage_calculation**
- **percentage_calculation**
- **percentage_calculation**
- **required_fields**

## ⚠️ Warnings

### ⚠️ execution_exceeds_100 (2 failures)

- Row 111: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (355.20%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1019 | 12002
- Row 172: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (54852.50%) in ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002

### ⚠️ negative_totals (1 failures)

- Program field 'program_actual' has negative value: -1198.40 for ՀՀ արտակարգ իրավիճակների նախարարություն | 9995 | 99100

### ⚠️ negative_totals (6 failures)

- Subprogram field 'subprogram_annual_plan' has negative value: -1276.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_rev_annual_plan' has negative value: -1276.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_rev_annual_plan' has negative value: -21946.50 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 9017 | 31002
- Subprogram field 'subprogram_actual' has negative value: -699917.70 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002
- Subprogram field 'subprogram_actual' has negative value: -21946.50 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 9017 | 31002
- Subprogram field 'subprogram_actual' has negative value: -1198.40 for ՀՀ արտակարգ իրավիճակների նախարարություն | 9995 | 99100

## ❌ Errors

### ❌ hierarchical_totals (1 failures)

- Overall overall_actual: expected 1566562784.7000003, got 1629436862.4, diff 62874077.69999981 (tolerance 2000.0)

### ❌ hierarchical_totals (3 failures)

- ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն: expected 147446773.0, got 139336023.3, diff 8110749.699999988
- ՀՀ էկոնոմիկայի նախարարություն: expected 12490498.500000002, got 4356519.0, diff 8133979.500000002
- ՀՀ կրթության, գիտության, մշակույթի և սպորտի նախարարություն: expected 156223148.0, got 134875641.9, diff 21347506.099999994

### ❌ hierarchical_totals (4 failures)

- ՀՀ կրթության, գիտության, մշակույթի և սպորտի նախարարություն/Երիտասարդության ծրագիր: expected 1139006.1, got 54509.4, diff 1084496.7000000002
- ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն/Կոլեկտորադրենաժային ծառայություններ: expected 349826.30000000005, got 26100.9, diff 323725.4
- ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն/Ոռոգման համակարգի առողջացում: expected 21884551.1, got 0.0, diff 21884551.1
- ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն/Ջրամատակարարաման և ջրահեռացման բարելավում: expected 5580977.100000001, got 3591908.0, diff 1989069.1000000006

### ❌ hierarchical_totals (1 failures)

- Overall overall_annual_plan: expected 1563735093.6999998, got 1648063122.3, diff 84328028.60000014 (tolerance 2000.0)

### ❌ hierarchical_totals (3 failures)

- ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն: expected 165677421.79999995, got 147577637.6, diff 18099784.19999996
- ՀՀ էկոնոմիկայի նախարարություն: expected 25407550.799999997, got 9322213.5, diff 16085337.299999997
- ՀՀ կրթության, գիտության, մշակույթի և սպորտի նախարարություն: expected 161013824.60000002, got 141696953.9, diff 19316870.700000018

### ❌ hierarchical_totals (4 failures)

- ՀՀ կրթության, գիտության, մշակույթի և սպորտի նախարարություն/Երիտասարդության ծրագիր: expected 978187.4, got 0.0, diff 978187.4
- ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն/Կոլեկտորադրենաժային ծառայություններ: expected 336497.3, got 0.0, diff 336497.3
- ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն/Ոռոգման համակարգի առողջացում: expected 16901296.9, got 0.0, diff 16901296.9
- ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն/Ջրամատակարարաման և ջրահեռացման բարելավում: expected 12610054.8, got 0.0, diff 12610054.8

### ❌ hierarchical_totals (1 failures)

- Overall overall_rev_annual_plan: expected 1674463746.6000001, got 1762920130.7, diff 88456384.0999999 (tolerance 2000.0)

### ❌ hierarchical_totals (3 failures)

- ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն: expected 192199759.4, got 175528847.3, diff 16670912.099999994
- ՀՀ էկոնոմիկայի նախարարություն: expected 21747570.399999995, got 8969716.5, diff 12777853.899999995
- ՀՀ կրթության, գիտության, մշակույթի և սպորտի նախարարություն: expected 167352112.20000002, got 144261843.8, diff 23090268.400000006

### ❌ hierarchical_totals (4 failures)

- ՀՀ կրթության, գիտության, մշակույթի և սպորտի նախարարություն/Երիտասարդության ծրագիր: expected 1297884.1, got 54509.4, diff 1243374.7000000002
- ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն/Կոլեկտորադրենաժային ծառայություններ: expected 402105.0, got 65607.7, diff 336497.3
- ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն/Ոռոգման համակարգի առողջացում: expected 26106190.599999998, got 85680.0, diff 26020510.599999998
- ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն/Ջրամատակարարաման և ջրահեռացման բարելավում: expected 11908875.1, got 3591908.0, diff 8316967.1

### ❌ percentage_calculation (1 failures)

- Row 871: Mismatch for 'subprogram_actual_vs_rev_annual_plan'. Expected: 1.0000, Reported: 0.9880, Diff: 0.0120 in ՀՀ բարձր տեխնոլոգիական արդյունաբերության նախարարություն | 1100 | 11004

---

For detailed information about validation checks and how to interpret results,
see [docs/validation.md](../../docs/validation.md).
