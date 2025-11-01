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
from armenian_budget.core.utils import detect_source_type
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


def run_validation(df: pd.DataFrame, csv_path: Path) -> ValidationReport:
    """Run all applicable validation checks on a dataset.

    Args:
        df: DataFrame containing CSV data (state body, program, subprogram rows).
        csv_path: Path to the CSV file being validated.

    Returns:
        ValidationReport containing aggregated results from all applicable checks.

    Raises:
        ValueError: If CSV filename doesn't match expected format or source type invalid.
        FileNotFoundError: If corresponding overall.json file not found.

    Examples:
        >>> df = pd.read_csv("data/2023_BUDGET_LAW.csv")
        >>> report = run_validation(df, Path("data/2023_BUDGET_LAW.csv"))
        >>> print(report.summary())
    """
    # Detect source type from filename
    source_type = detect_source_type(csv_path)

    # Load overall.json file
    overall_path = csv_path.parent / f"{csv_path.stem}_overall.json"
    if not overall_path.exists():
        raise FileNotFoundError(
            f"Overall JSON file not found: {overall_path}. "
            f"Expected format: {{csv_stem}}_overall.json"
        )

    with open(overall_path, "r", encoding="utf-8") as f:
        overall = json.load(f)

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
