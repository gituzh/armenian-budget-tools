"""Validation system for Armenian Budget Tools.

This module provides a comprehensive validation framework for budget data:

- **Models**: CheckResult, ValidationReport - validation result data structures
- **Checks**: ValidationCheck protocol - interface for implementing new checks
- **Config**: Tolerance constants and severity rules (import from .config)
- **Registry**: run_validation(), print_report() - check orchestration and execution

Public API:
    CheckResult: Individual check result with severity and failure details
    ValidationReport: Aggregated validation results with helper methods
    ValidationCheck: Protocol for implementing custom validation checks
    run_validation: Run all applicable validation checks on a dataset
    print_report: Display validation results to console

Usage:
    >>> from armenian_budget.validation import run_validation, print_report
    >>> import pandas as pd
    >>> df = pd.read_csv("2023_BUDGET_LAW.csv")
    >>> report = run_validation(df, Path("2023_BUDGET_LAW.csv"))
    >>> print_report(report)

For implementation details:
    - See validation/checks/__init__.py for how to implement new checks
    - See validation/config.py for tolerance and severity configuration
    - See validation/registry.py for check orchestration
"""

from __future__ import annotations

from armenian_budget.core.enums import SourceType
from armenian_budget.core.utils import detect_source_type

from .checks import ValidationCheck
from .models import CheckResult, ValidationReport
from .registry import run_validation, print_report

__all__ = [
    # Data models
    "CheckResult",
    "ValidationReport",
    # Check interface
    "ValidationCheck",
    # Runner functions
    "run_validation",
    "print_report",
    # Enums
    "SourceType",
    # Utilities
    "detect_source_type",
]
