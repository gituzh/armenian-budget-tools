# Validation Report: 2021_BUDGET_LAW_PARLIAMENT.csv

**Source Type:** BUDGET_LAW
**File:** 2021_BUDGET_LAW_PARLIAMENT.csv
**Generated:** 2026-11-22 20:34:52
**Identical data:** PARLIAMENT (2020-10-01), EDRAFT (2020-10-02)

## Summary

### Check Status

- **Total Rules:** 22
- **Passed:** 21 ✅
- **With Warnings:** 1 ⚠️
- **With Errors:** 0 ❌

### Issues Found

- **Errors:** 0
- **Warnings:** 1 ⚠️

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
- **hierarchical_structure_sanity**
- **hierarchical_totals** (overall_total vs state_body_total)
- **hierarchical_totals** (state_body_total vs program_total)
- **hierarchical_totals** (program_total vs subprogram_total)
- **missing_financial_data** (overall)
- **missing_financial_data** (state_body)
- **missing_financial_data** (program)
- **missing_financial_data** (subprogram)
- **negative_totals** (overall)
- **negative_totals** (state_body)
- **negative_totals** (program)
- **required_fields**

## ⚠️ Warnings

### ⚠️ negative_totals: subprogram (1 failures)

- Subprogram field 'subprogram_total' has negative value: -1276.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002

---

For detailed information about validation checks and how to interpret results,
see [docs/validation.md](../../docs/validation.md).
