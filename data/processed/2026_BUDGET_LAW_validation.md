# Validation Report: 2026_BUDGET_LAW.csv

**Source Type:** BUDGET_LAW
**File:** 2026_BUDGET_LAW.csv
**Generated:** 2026-11-22 19:07:43
**Identical data:** DRAFT2 (2025-11-27), PARLIAMENT2 (2025-12-01), (unlabelled) (2025-12-03)

## Summary

### Check Status

- **Total Rules:** 22
- **Passed:** 20 ✅
- **With Warnings:** 2 ⚠️
- **With Errors:** 0 ❌

### Issues Found

- **Errors:** 0
- **Warnings:** 7 ⚠️

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
- **required_fields**

## ⚠️ Warnings

### ⚠️ negative_totals: program (6 failures)

- Program field 'program_total' has negative value: -7351877.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11001
- Program field 'program_total' has negative value: -7351877.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11003
- Program field 'program_total' has negative value: -7351877.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11015
- Program field 'program_total' has negative value: -7351877.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11017
- Program field 'program_total' has negative value: -7351877.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 11018
- Program field 'program_total' has negative value: -7351877.10 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002

### ⚠️ negative_totals: subprogram (1 failures)

- Subprogram field 'subprogram_total' has negative value: -10000000.00 for ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 1079 | 31002

---

For detailed information about validation checks and how to interpret results,
see [docs/validation.md](../../docs/validation.md).
