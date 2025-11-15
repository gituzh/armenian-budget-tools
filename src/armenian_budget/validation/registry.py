"""Validation check registry and runner.

This module orchestrates validation checks:
- ALL_CHECKS: List of all available validation check instances
- run_validation(): Executes applicable checks and returns ValidationReport
- print_report(): Displays validation results to console
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import pandas as pd

from armenian_budget.core.enums import SourceType
from armenian_budget.core.utils import get_processed_paths
from .checks.required_fields import RequiredFieldsCheck
from .checks.empty_identifiers import EmptyIdentifiersCheck
from .checks.missing_financial_data import MissingFinancialDataCheck
from .checks.hierarchical_totals import HierarchicalTotalsCheck
from .checks.negative_totals import NegativeTotalsCheck
from .checks.period_vs_annual import PeriodVsAnnualCheck
from .checks.negative_percentages import NegativePercentagesCheck
from .checks.execution_exceeds_100 import ExecutionExceeds100Check
from .checks.percentage_calculation import PercentageCalculationCheck
from .models import CheckResult, ValidationReport


# Registry of all available validation checks
# Order matches implementation phases for documentation clarity
ALL_CHECKS = [
    # Phase 3: Core Structural Checks
    RequiredFieldsCheck(),
    EmptyIdentifiersCheck(),
    MissingFinancialDataCheck(),
    # Phase 4: Hierarchical & Financial Checks
    HierarchicalTotalsCheck(),
    NegativeTotalsCheck(),
    # Phase 5: Spending-Specific Checks
    PeriodVsAnnualCheck(),
    NegativePercentagesCheck(),
    ExecutionExceeds100Check(),
    PercentageCalculationCheck(),
]


def run_validation(
    year: int, source_type: SourceType, processed_root: Path
) -> ValidationReport:
    """Run all applicable validation checks on a dataset.

    Args:
        year: The year of the budget data to validate (e.g., 2023).
        source_type: The source type of the data (e.g., BUDGET_LAW, SPENDING_Q1).
        processed_root: Path to the processed data root directory.

    Returns:
        ValidationReport containing aggregated results from all applicable checks.

    Raises:
        FileNotFoundError: If processed_root, CSV file, or overall.json file not found.
        ValueError: If CSV or JSON files cannot be parsed.

    Examples:
        >>> from pathlib import Path
        >>> processed_root = Path("data/processed")
        >>> report = run_validation(2023, SourceType.BUDGET_LAW, processed_root)
        >>> print(report.summary())
    """
    # Check that processed_root exists
    if not processed_root.exists():
        raise FileNotFoundError(
            f"Processed data root not found: {processed_root}. "
            f"Run 'armenian-budget process' first to generate processed data."
        )

    # Construct file paths using utility function
    csv_path, overall_path = get_processed_paths(year, source_type, processed_root)

    # Validate CSV file exists
    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV file not found: {csv_path}. "
            f"Expected format: {{year}}_{{SOURCE_TYPE}}.csv"
        )

    # Validate overall.json file exists
    if not overall_path.exists():
        raise FileNotFoundError(
            f"Overall JSON file not found: {overall_path}. "
            f"Expected format: {{year}}_{{SOURCE_TYPE}}_overall.json"
        )

    # Load CSV data
    try:
        df = pd.read_csv(csv_path, encoding="utf-8-sig")
    except (OSError, pd.errors.ParserError) as e:
        raise ValueError(f"Failed to read CSV file {csv_path}: {e}") from e

    # Load overall.json file
    try:
        with open(overall_path, "r", encoding="utf-8") as f:
            overall = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise ValueError(f"Failed to read overall JSON file {overall_path}: {e}") from e

    # Filter and execute applicable checks
    all_results: List[CheckResult] = []
    for check in ALL_CHECKS:
        if check.applies_to_source_type(source_type):
            results = check.validate(df, overall, source_type)
            all_results.extend(results)

    # Create and return validation report
    return ValidationReport(
        results=all_results,
        source_type=source_type,
        csv_path=csv_path,
        overall_path=overall_path,
    )


def print_report(report: ValidationReport) -> None:
    """Print validation report to console.

    Displays a summary followed by details of all failed checks.

    Args:
        report: ValidationReport to display.

    Examples:
        >>> report = run_validation(df, csv_path)
        >>> print_report(report)
        Validation Summary:
          Source: BUDGET_LAW (2023_BUDGET_LAW.csv)
          Checks: 15 total, 13 passed, 2 failed
          Errors: 2
          Warnings: 0

        Failed Checks:
        ❌ hierarchical_totals (error): 2 failures
           - Overall overall_total: expected 100000, got 99999, diff 1 (tolerance 1.0)
    """
    # Print summary
    print(report.summary())
    print()

    # Get failed checks
    failed = report.get_failed_checks()

    if not failed:
        print("✅ All validation checks passed!")
        return

    # Print failed checks
    print("Failed Checks:")
    for result in failed:
        # Use emoji for severity
        icon = "❌" if result.severity == "error" else "⚠️"
        print(f"{icon} {result.check_id} ({result.severity}): {result.fail_count} failures")

        # Print messages (indented)
        for msg in result.messages:
            print(f"   - {msg}")
