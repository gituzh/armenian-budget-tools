"""Validation system for Armenian Budget Tools.

This module provides a comprehensive validation framework for budget data:

- **Models**: CheckResult, ValidationReport - validation result data structures
- **Checks**: ValidationCheck protocol - interface for implementing new checks
- **Config**: Tolerance constants and severity rules (import from .config)

Public API:
    CheckResult: Individual check result with severity and failure details
    ValidationReport: Aggregated validation results with helper methods
    ValidationCheck: Protocol for implementing custom validation checks

Usage:
    >>> from armenian_budget.validation import ValidationReport, CheckResult
    >>> report = ValidationReport(results=[...], source_type=..., csv_path=...)
    >>> if report.has_errors():
    ...     print(f"Found {report.get_error_count()} errors")

For implementation details:
    - See validation/checks/__init__.py for how to implement new checks
    - See validation/config.py for tolerance and severity configuration
    - See validation/registry.py (coming in Phase 6) for check orchestration
"""

from __future__ import annotations

from .checks import ValidationCheck
from .models import CheckResult, ValidationReport

__all__ = [
    # Data models
    "CheckResult",
    "ValidationReport",
    # Check interface
    "ValidationCheck",
]
