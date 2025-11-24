"""Validation system for Armenian Budget Tools.

This module provides a comprehensive validation framework for budget data:

- **Models**: CheckResult, ValidationReport - validation result data structures
- **Checks**: Individual validation check implementations (see validation/checks/)
- **Config**: Tolerance constants and severity rules (import from .config)
- **Registry**: run_validation(), print_report() - check orchestration and execution

Public API:
    CheckResult: Individual check result with severity and failure details
    ValidationReport: Aggregated validation results with helper methods
    run_validation: Run all applicable validation checks on a dataset
    print_report: Display validation results to console

Usage:
    >>> from armenian_budget.validation import run_validation, print_report, SourceType
    >>> from pathlib import Path
    >>> processed_root = Path("data/processed")
    >>> report = run_validation(2023, SourceType.BUDGET_LAW, processed_root)
    >>> print_report(report)

For implementation details:
    - See validation/checks/__init__.py for check interface conventions
    - See validation/config.py for tolerance and severity configuration
    - See validation/registry.py for check orchestration
"""

from __future__ import annotations

from armenian_budget.core.enums import SourceType

from .models import CheckResult, ValidationReport
from .registry import print_report, run_validation

__all__ = [
    # Data models
    "CheckResult",
    "ValidationReport",
    # Runner functions
    "run_validation",
    "print_report",
    # Enums
    "SourceType",
]
