# Data Validation

## What is Validation?

When we process Armenian budget data from official Excel files, we run comprehensive quality checks to ensure the data is accurate, complete, and trustworthy. Validation helps catch data entry errors, calculation mistakes, missing information, and structural problems that would make analysis unreliable.

Every processed CSV file can be validated to give you confidence that the numbers are correct before you use them for analysis, reporting, or decision-making.

It's helpful to distinguish between two types of data quality checks:

* A **Parser Test** validates the *syntax and structure of the raw source file*. It answers: "Can this file be read and converted into a structured DataFrame correctly?"
* A **Validation Check** validates the *semantics, consistency, and logical rules of the data after it has been successfully parsed*. It answers: "Now that I have the data, does it make sense?"

This validation framework focuses exclusively on the second type: checking the semantic and logical integrity of the processed data.

## How to Run Validation

```bash
# Validate dataset (console output only)
armenian-budget validate --years 2023 --source-type BUDGET_LAW

# Save detailed Markdown report (default: next to CSV file)
armenian-budget validate --years 2023 --source-type BUDGET_LAW --report
# Creates: data/processed/2023_BUDGET_LAW_validation.md

# Save Markdown reports to custom directory
armenian-budget validate --years 2023 --source-type BUDGET_LAW --report path/to/reports/
# Creates: path/to/reports/2023_BUDGET_LAW_validation.md

# Save JSON reports (default: next to CSV file)
armenian-budget validate --years 2023 --source-type BUDGET_LAW --report-json
# Creates: data/processed/2023_BUDGET_LAW_validation.json

# Save JSON reports to custom directory
armenian-budget validate --years 2022-2024 --source-type MTEP --report-json path/to/reports/
# Creates: path/to/reports/2022_MTEP_validation.json
#          path/to/reports/2023_MTEP_validation.json
#          path/to/reports/2024_MTEP_validation.json

# Multiple years/sources create one report per year/source combination
armenian-budget validate --years 2022,2023,2024 --report
```

**Report Output Behavior:**

- Validation always shows a summary in the console for each year
- Use `--report` to also save a detailed Markdown file for each year/source combination
- Use `--report-json` to save a detailed JSON file for each year/source combination
- Both flags accept an optional directory path:
  - **No path:** Reports saved next to CSV files in processed root
  - **With path:** Reports saved to specified directory
- When validating multiple years/sources, one report file is created per year/source combination
- Without these flags, no files are created (console only)

## Understanding Validation Reports

The validation report lists every check performed and shows:

- ✅ **PASS** - The check succeeded, no issues found
- ❌ **FAIL** - The check found problems (with count and details)
- ⚠️ **WARN** - Issues found but not critical

For each failure, the report shows exactly which state bodies, programs, or subprograms have problems and what the issue is (e.g., "expected 1000, got 950, difference: 50").

### Report Format Consistency

Markdown and JSON reports contain identical information. JSON field names are snake_case versions of markdown labels: `**Total Rules:**` → `"total_rules"`, `**Passed:**` → `"passed"`, `**With Warnings:**` → `"with_warnings"`, `**With Errors:**` → `"with_errors"`.

Use Markdown for human review and documentation. Use JSON for programmatic analysis and automation.

### Exit Codes

The validate command returns standard exit codes for scripting and CI/CD integration:

- **0**: All validations passed without errors
- **1**: No datasets were validated (missing files or invalid configuration)
- **2**: Validation errors found in one or more datasets

**Note:** Exit code 2 is returned when ANY dataset has errors, even if other datasets pass. Warnings do not affect the exit code.

**Example usage in scripts:**

```bash
#!/bin/bash
armenian-budget validate --years 2023 --source-type BUDGET_LAW
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Validation passed - safe to proceed"
elif [ $EXIT_CODE -eq 1 ]; then
    echo "❌ No datasets found - check file paths"
    exit 1
elif [ $EXIT_CODE -eq 2 ]; then
    echo "⚠️  Validation errors found - review reports"
    exit 1
fi
```

### Report Structure

Validation reports contain identical information in both Markdown and JSON formats.

#### Markdown Format

Markdown reports are human-readable with clear sections:

1. **Header** - Source type, file paths, generation timestamp
2. **Summary** - Check counts (total, passed, warnings, errors) and issue counts
3. **Passed Checks** - List of successful validations
4. **Warnings Section** - Warning-level checks with detailed failure messages
5. **Errors Section** - Error-level checks with detailed failure messages
6. **Footer** - Link to validation documentation

Each failure message includes specific context (entity names, actual vs expected values, etc.).

#### JSON Format

JSON reports are machine-readable with this structure:

```json
{
  "metadata": {
    "source_type": "BUDGET_LAW",
    "csv_path": "data/processed/2023_BUDGET_LAW.csv",
    "overall_path": "data/processed/2023_BUDGET_LAW_overall.json",
    "generated_at": "2023-12-01T12:00:00"
  },
  "summary": {
    "total_rules": 10,
    "passed": 8,
    "with_warnings": 1,
    "with_errors": 1,
    "errors": 5,
    "warnings": 3
  },
  "passed_checks": [
    {
      "check_id": "required_fields",
      "severity": "error",
      "messages": []
    }
  ],
  "warning_checks": [
    {
      "check_id": "negative_totals",
      "severity": "warning",
      "fail_count": 3,
      "messages": [
        "State body 'Ministry of Finance' has negative program total: -1000.0 AMD"
      ]
    }
  ],
  "error_checks": [
    {
      "check_id": "hierarchical_totals",
      "severity": "error",
      "fail_count": 2,
      "messages": [
        "Overall total mismatch for field 'total': expected 100000.0, got 99995.0, diff 5.0"
      ]
    }
  ]
}
```

**Field Naming:** JSON uses snake_case versions of Markdown labels:

- "Total Rules" → `"total_rules"`
- "Passed" → `"passed"`
- "With Warnings" → `"with_warnings"`
- "With Errors" → `"with_errors"`

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
| **Spending Reports** | Error | Error | Error | 2000.0 AMD |
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

### Hierarchical Structure Sanity

Verifies that the budget hierarchy has reasonable structure (not degenerate/flat). Catches parser failures or data quality issues where the hierarchy collapses to a single level.

**Checks:**

1. State bodies don't all have identical program counts (variety exists)
2. At least one state body has multiple programs (depth exists)

**Applies to:** BUDGET_LAW only (other source types don't require hierarchical depth)

**Severity:** Warning at overall level

This is a sanity check - failures suggest fundamental problems with parsing or source data structure rather than minor data quality issues.

### Period vs Annual Plan Consistency

Period budgets generally should not exceed annual budgets, but the logic depends on the sign of the amounts (spending vs. returns).

**Rules:**

1.  **Positive Annual Plan (Spending):** Violation if `Period > Annual`. You cannot plan to spend more in a period than for the whole year.
2.  **Negative Annual Plan (Returns/Reductions):** Violation if `Period < Annual` (i.e., more negative). You cannot plan to return more in a period than authorized for the whole year.
3.  **Mixed Signs:** Violation if `Period` and `Annual` have different signs (unless `Period` is zero). This indicates a fundamental mismatch in the direction of the flow.

| Data Type | Checks | Severity |
|-----------|--------|----------|
| **Spending Q1/Q12/Q123** | `*_period_plan` vs `*_annual_plan`<br>`*_rev_period_plan` vs `*_rev_annual_plan` | Error: overall, state_body, program<br>Warning: subprogram |

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
| **Spending Q1/Q12/Q123** | `*_actual_vs_rev_annual_plan` = `*_actual` / `*_rev_annual_plan`<br>`*_actual_vs_rev_period_plan` = `*_actual` / `*_rev_period_plan` | 0.25% |
| **Spending Q1234** | `*_actual_vs_rev_annual_plan` = `*_actual` / `*_rev_annual_plan` | 0.25% |

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
