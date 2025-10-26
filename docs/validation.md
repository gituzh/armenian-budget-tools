# Data Validation

## What is Validation?

When we process Armenian budget data from official Excel files, we run comprehensive quality checks to ensure the data is accurate, complete, and trustworthy. Validation helps catch data entry errors, calculation mistakes, missing information, and structural problems that would make analysis unreliable.

Every processed CSV file can be validated to give you confidence that the numbers are correct before you use them for analysis, reporting, or decision-making.

## How to Run Validation

```bash
# Console summary only (shows which checks passed/failed)
armenian-budget validate --csv data/processed/csv/2023_BUDGET_LAW.csv

# Save detailed report to default location (next to the CSV file)
armenian-budget validate --csv data/processed/csv/2023_BUDGET_LAW.csv --report

# This creates: data/processed/csv/2023_BUDGET_LAW_validation.md

# Save report to a custom location
armenian-budget validate --csv data/processed/csv/2023_BUDGET_LAW.csv --report path/to/my_report.md
```

**What happens:**

- Validation always shows a summary in the console
- Use `--report` to also save a detailed Markdown file with complete failure information
- Without `--report`, no file is created (console only)

## Understanding Validation Reports

The validation report lists every check performed and shows:

- ✅ **PASS** - The check succeeded, no issues found
- ❌ **FAIL** - The check found problems (with count and details)
- ⚠️ **WARN** - Issues found but not critical

For each failure, the report shows exactly which state bodies, programs, or subprograms have problems and what the issue is (e.g., "expected 1000, got 950, difference: 50").

## Validation Checks

### Required Fields

All fields described in [data_schemas.md](data_schemas.md#7-complete-column-reference) must be present (both CSV and JSON fields). Missing required fields are critical errors that prevent analysis.

**Severity:** Error

**Note:** Overall metadata is stored in `{year}_{SOURCE_TYPE}_overall.json` alongside the CSV file.

### Empty Identifiers

Budget lines must be identifiable. Empty state body or program names are critical errors; empty subprogram names are warnings.

| Data Type | Empty State Body | Empty Program Name | Empty Subprogram Name |
|-----------|------------------|--------------------|-----------------------|
| **Budget Law** | Error | Error | Warning |
| **Spending Reports** | Error | Error | Warning |
| **MTEP** | Error | Error | - |

### No Missing Financial Data

Critical financial amounts and percentages must not be empty (null/NaN). Missing values prevent analysis and percentage calculations.

| Data Type | Missing Financial Fields | Severity by Level |
|-----------|-------------------------|-------------------|
| **Budget Law** | `*_total` | Error: overall, state_body, program<br>Warning: subprogram |
| **Spending Q1/Q12/Q123** | `*_annual_plan`, `*_rev_annual_plan`, `*_period_plan`, `*_rev_period_plan`, `*_actual`, `*_actual_vs_rev_annual_plan`, `*_actual_vs_rev_period_plan` | Error: overall, state_body, program<br>Warning: subprogram |
| **Spending Q1234** | `*_annual_plan`, `*_rev_annual_plan`, `*_actual`, `*_actual_vs_rev_annual_plan` | Error: overall, state_body, program<br>Warning: subprogram |
| **MTEP** | `*_total_y0`, `*_total_y1`, `*_total_y2`, `plan_years` | Error: overall, state_body, program |

**Wildcard (`*`) represents:** `overall` (JSON), `state_body`, `program`, `subprogram` (CSV). MTEP has no subprogram.

### Hierarchical Totals

Budget hierarchy must sum correctly at each level. Grand total from metadata must equal sum of state bodies; each state body must equal sum of its programs; each program must equal sum of its subprograms. Small differences within tolerance may be rounding; large differences indicate data quality problems.

| Data Type | Grand Total = Σ State Bodies | State Body = Σ Programs | Program = Σ Subprograms | Tolerance (applies to all 3 checks) |
|-----------|------------------------------|-------------------------|-------------------------|-------------------------------------|
| **Budget Law** | Error | Error | Error | 0.0 AMD (strict) |
| **Spending Reports** | Error (all financial fields) | Error (all financial fields) | Error (all financial fields) | 5.0 AMD |
| **MTEP** | Error (Y0, Y1, Y2) | Error (Y0, Y1, Y2) | - | 0.5 AMD per year |

**Note:** For Spending Reports, hierarchical checks apply to amount fields (not percentages): `*_annual_plan`, `*_rev_annual_plan`, `*_actual`, and for Q1/Q12/Q123 only: `*_period_plan`, `*_rev_period_plan` where `*` = overall, state_body, program, subprogram.

### Negative Totals

Negative totals are critical errors at overall, state body, and program levels. Subprogram negatives are warnings as they may be legitimate corrections.

| Data Type | Fields | Severity by Level |
|-----------|--------|-------------------|
| **Budget Law** | `*_total` | Error: overall, state_body, program<br>Warning: subprogram |
| **Spending Q1/Q12/Q123** | `*_annual_plan`, `*_rev_annual_plan`, `*_period_plan`, `*_rev_period_plan`, `*_actual` | Error: overall, state_body, program<br>Warning: subprogram |
| **Spending Q1234** | `*_annual_plan`, `*_rev_annual_plan`, `*_actual` | Error: overall, state_body, program<br>Warning: subprogram |
| **MTEP** | `*_total_y0`, `*_total_y1`, `*_total_y2` | Error: overall, state_body, program |

**Wildcard (`*`) represents:** `overall` (JSON), `state_body`, `program`, `subprogram` (CSV). MTEP has no subprogram.

### Period ≤ Annual Plan

Quarterly/period budgets cannot exceed full-year budgets. Violations indicate data entry errors or missing annual plan updates.

| Data Type | Checks | Severity |
|-----------|--------|----------|
| **Spending Q1/Q12/Q123** | `*_period_plan` ≤ `*_annual_plan`<br>`*_rev_period_plan` ≤ `*_rev_annual_plan` | Error |

**Wildcard (`*`) represents:** `overall` (JSON), `state_body`, `program`, `subprogram` (CSV).

### No Negative Percentages

Negative execution percentages are mathematically impossible and indicate data corruption. Critical at overall and state body levels; warnings at program/subprogram levels.

| Data Type | Fields | Severity by Level |
|-----------|--------|-------------------|
| **Spending Q1/Q12/Q123** | `*_actual_vs_rev_annual_plan`, `*_actual_vs_rev_period_plan` | Error: overall, state_body<br>Warning: program, subprogram |
| **Spending Q1234** | `*_actual_vs_rev_annual_plan` | Error: overall, state_body<br>Warning: program, subprogram |

**Wildcard (`*`) represents:** `overall` (JSON), `state_body`, `program`, `subprogram` (CSV).

### Execution Exceeds 100%

Execution percentages above 100% indicate spending exceeded revised plans (overspending). While this may be legitimate with budget revisions, it warrants review. All levels flagged as warnings.

| Data Type | Fields | Severity by Level |
|-----------|--------|-------------------|
| **Spending Q1/Q12/Q123** | `*_actual_vs_rev_annual_plan`, `*_actual_vs_rev_period_plan` | Warning: overall, state_body, program, subprogram |
| **Spending Q1234** | `*_actual_vs_rev_annual_plan` | Warning: overall, state_body, program, subprogram |

**Wildcard (`*`) represents:** `overall` (JSON), `state_body`, `program`, `subprogram` (CSV).

### Percentage Calculation Correctness

Reported percentages must match calculated values at all hierarchy levels (grand total, state body, program, subprogram). Checks verify correctness of both annual and period percentages where applicable.

| Data Type | Percentage Calculation Checks | Tolerance |
|-----------|------------------------------|-----------|
| **Spending Q1/Q12/Q123** | `*_actual_vs_rev_annual_plan` = `*_actual` / `*_rev_annual_plan`<br>`*_actual_vs_rev_period_plan` = `*_actual` / `*_rev_period_plan` | 0.1% |
| **Spending Q1234** | `*_actual_vs_rev_annual_plan` = `*_actual` / `*_rev_annual_plan` | 0.1% |

**Wildcard (`*`) represents:** `overall` (JSON), `state_body`, `program`, `subprogram` (CSV).

## Common Failure Scenarios

| Failure Pattern | Likely Cause | Recommended Action |
|----------------|--------------|-------------------|
| **Rollup mismatch (< 10 AMD)** | Harmless rounding in source Excel | Safe to proceed if tolerable for your use case |
| **Rollup mismatch (> 1,000 AMD)** | Serious data quality problem | Investigate original file; do not use for critical decisions |
| **Period plan exceeds annual** | Data entry error or annual plan not updated | Check specific programs; verify which figure is correct |
| **Percentage calculation off by < 1%** | Minor calculation error in source | Recalculate percentages yourself using actual amounts |
| **Empty program/subprogram names** | Data entry omission | Check if codes present; may still be usable |
| **Negative state body/program total** | Critical data corruption | Always investigate; never proceed without resolution |
| **Percentage > 100%** | Overspending or data error | Review specific programs; may indicate budget revisions |
| **Missing required fields** | Incorrect parsing or wrong file | Verify you're using the correct processed CSV |

## When to Proceed Despite Failures

**Generally safe:**

- Small rounding differences (< 10 AMD) in rollup checks
- Empty subprogram names if codes are present
- Negative subprogram totals (may be legitimate corrections)
- Execution > 100% warnings (may indicate legitimate budget revisions)

**Proceed with caution (document in your analysis):**

- Moderate differences (10-1,000 AMD) in rollup totals
- Missing percentage calculations - recalculate yourself
- Period exceeding annual - understand which programs and why

**Do not use without investigation:**

- Large differences (> 1,000 AMD) in rollup totals
- Negative state body or program totals
- Negative percentages (indicates data corruption)
- Missing required fields or extensive missing data

---

**For technical details** (tolerance values, implementation, adding new checks), see [Developer Guide - Validation Framework](developer_guide.md#validation-framework).
