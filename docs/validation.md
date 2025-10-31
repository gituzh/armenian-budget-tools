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

Budget lines must be identifiable. Empty identifiers prevent proper analysis.

| Data Type | Empty State Body | Empty Program Name | Empty Subprogram Name |
|-----------|------------------|--------------------|-----------------------|
| **Budget Law** | Error | Error | Warning |
| **Spending Reports** | Error | Error | Warning |
| **MTEP** | Error | Error | - |

### No Missing Financial Data

Financial amounts and percentages must not be empty (null/NaN). Missing values prevent analysis.

| Data Type | Missing Financial Fields | Severity by Level |
|-----------|-------------------------|-------------------|
| **Budget Law** | `*_total` | Error: overall, state_body, program<br>Warning: subprogram |
| **Spending Q1/Q12/Q123** | `*_annual_plan`, `*_rev_annual_plan`, `*_period_plan`, `*_rev_period_plan`, `*_actual`, `*_actual_vs_rev_annual_plan`, `*_actual_vs_rev_period_plan` | Error: overall, state_body, program<br>Warning: subprogram |
| **Spending Q1234** | `*_annual_plan`, `*_rev_annual_plan`, `*_actual`, `*_actual_vs_rev_annual_plan` | Error: overall, state_body, program<br>Warning: subprogram |
| **MTEP** | `*_total_y0`, `*_total_y1`, `*_total_y2`, `plan_years` | Error: overall, state_body, program |

**Wildcard (`*`) represents:** `overall` (JSON), `state_body`, `program`, `subprogram` (CSV). MTEP has no subprogram.

### Hierarchical Totals

Budget hierarchy must sum correctly: grand total = Σ state bodies, state body = Σ programs, program = Σ subprograms. Differences within tolerance may be rounding; larger differences indicate data quality problems.

| Data Type | Grand Total = Σ State Bodies | State Body = Σ Programs | Program = Σ Subprograms | Tolerance |
|-----------|------------------------------|-------------------------|-------------------------|-----------|
| **Budget Law** | Error | Error | Error | 1.0 AMD |
| **Spending Reports** | Error | Error | Error | 5.0 AMD |
| **MTEP** | Error | Error | - | 0.5 AMD per year |

**Note:** For Spending Reports, hierarchical checks apply to amount fields (not percentages): `*_annual_plan`, `*_rev_annual_plan`, `*_actual`, and for Q1/Q12/Q123 only: `*_period_plan`, `*_rev_period_plan` where `*` = overall, state_body, program, subprogram.

### Negative Totals

Negative values may indicate data quality issues or legitimate corrections/adjustments. All flagged as warnings for review.

| Data Type | Fields | Severity by Level |
|-----------|--------|-------------------|
| **Budget Law** | `*_total` | Warning: overall, state_body, program, subprogram |
| **Spending Q1/Q12/Q123** | `*_annual_plan`, `*_rev_annual_plan`, `*_period_plan`, `*_rev_period_plan`, `*_actual` | Warning: overall, state_body, program, subprogram |
| **Spending Q1234** | `*_annual_plan`, `*_rev_annual_plan`, `*_actual` | Warning: overall, state_body, program, subprogram |
| **MTEP** | `*_total_y0`, `*_total_y1`, `*_total_y2` | Warning: overall, state_body, program |

**Wildcard (`*`) represents:** `overall` (JSON), `state_body`, `program`, `subprogram` (CSV). MTEP has no subprogram.

### Period ≤ Annual Plan

Period budgets cannot exceed annual budgets. Violations indicate data entry errors.

| Data Type | Checks | Severity |
|-----------|--------|----------|
| **Spending Q1/Q12/Q123** | `*_period_plan` ≤ `*_annual_plan`<br>`*_rev_period_plan` ≤ `*_rev_annual_plan` | Error |

**Wildcard (`*`) represents:** `overall` (JSON), `state_body`, `program`, `subprogram` (CSV).

### No Negative Percentages

Negative percentages are mathematically impossible and indicate data corruption.

| Data Type | Fields | Severity by Level |
|-----------|--------|-------------------|
| **Spending Q1/Q12/Q123** | `*_actual_vs_rev_annual_plan`, `*_actual_vs_rev_period_plan` | Error: overall, state_body<br>Warning: program, subprogram |
| **Spending Q1234** | `*_actual_vs_rev_annual_plan` | Error: overall, state_body<br>Warning: program, subprogram |

**Wildcard (`*`) represents:** `overall` (JSON), `state_body`, `program`, `subprogram` (CSV).

### Execution Exceeds 100%

Execution above 100% indicates overspending. May be legitimate with budget revisions but warrants review.

| Data Type | Fields | Severity by Level |
|-----------|--------|-------------------|
| **Spending Q1/Q12/Q123** | `*_actual_vs_rev_annual_plan`, `*_actual_vs_rev_period_plan` | Warning: overall, state_body, program, subprogram |
| **Spending Q1234** | `*_actual_vs_rev_annual_plan` | Warning: overall, state_body, program, subprogram |

**Wildcard (`*`) represents:** `overall` (JSON), `state_body`, `program`, `subprogram` (CSV).

### Percentage Calculation Correctness

Reported percentages must match calculated values at all hierarchy levels.

| Data Type | Percentage Calculation Checks | Tolerance |
|-----------|------------------------------|-----------|
| **Spending Q1/Q12/Q123** | `*_actual_vs_rev_annual_plan` = `*_actual` / `*_rev_annual_plan`<br>`*_actual_vs_rev_period_plan` = `*_actual` / `*_rev_period_plan` | 0.1% |
| **Spending Q1234** | `*_actual_vs_rev_annual_plan` = `*_actual` / `*_rev_annual_plan` | 0.1% |

**Wildcard (`*`) represents:** `overall` (JSON), `state_body`, `program`, `subprogram` (CSV).

## Interpreting Validation Results

Validation always completes and generates a full report with error and warning counts. Use this guide to determine if your data is trustworthy for analysis.

**Critical data issues (do not use for decisions):**

- Large hierarchical mismatches (> 1,000 AMD) - indicates serious data corruption
- Negative percentages - mathematically impossible, indicates corruption
- Missing required fields - data is incomplete

**Review required (document in analysis):**

- Moderate hierarchical differences (10-1,000 AMD) - understand source
- Period exceeding annual plan - verify which figure is correct
- Percentage calculation errors - recalculate yourself using actual amounts
- Execution > 100% - may indicate legitimate budget revisions
- Negative totals - may be legitimate corrections or data quality issues

**Safe to proceed:**

- Small hierarchical differences (< 10 AMD) - harmless rounding
- Empty subprogram names (if codes present) - may still be usable

---

**For technical details** (tolerance values, implementation, adding new checks), see [Developer Guide - Validation Framework](developer_guide.md#validation-framework).
