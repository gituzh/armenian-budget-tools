"""Validation data models.

This module defines core data structures for validation results:
- CheckResult: Outcome of a single validation check
- ValidationReport: Aggregated results from all checks
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from armenian_budget.core.enums import SourceType


@dataclass(frozen=True)
class CheckResult:
    """Result of a single validation check.

    Attributes:
        check_id: Unique identifier for the check (e.g., "hierarchical_totals").
        severity: Severity level - "error" for critical issues, "warning" for review items.
        passed: True if check passed without issues, False otherwise.
        fail_count: Number of failures detected (0 if passed).
        messages: Detailed failure messages with context (e.g., which rows failed).

    Examples:
        >>> CheckResult(
        ...     check_id="negative_totals",
        ...     severity="error",
        ...     passed=False,
        ...     fail_count=3,
        ...     messages=["State body X has negative total: -1000"]
        ... )
    """

    check_id: str
    severity: str  # "error" | "warning"
    passed: bool
    fail_count: int
    messages: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate field constraints."""
        if self.severity not in ("error", "warning"):
            raise ValueError(f"Invalid severity: {self.severity}. Must be 'error' or 'warning'.")
        if self.passed and self.fail_count != 0:
            raise ValueError("passed=True requires fail_count=0")
        if not self.passed and self.fail_count == 0:
            raise ValueError("passed=False requires fail_count > 0")


@dataclass
class ValidationReport:
    """Aggregated validation results for a dataset.

    Attributes:
        results: List of check results (one per validation check).
        source_type: Type of data source being validated.
        csv_path: Path to the CSV file being validated.
        overall_path: Path to the corresponding overall.json file (if exists).

    Examples:
        >>> report = ValidationReport(
        ...     results=[check1, check2, check3],
        ...     source_type=SourceType.BUDGET_LAW,
        ...     csv_path=Path("data/2023_BUDGET_LAW.csv"),
        ...     overall_path=Path("data/2023_BUDGET_LAW_overall.json")
        ... )
        >>> report.has_errors()
        True
        >>> report.get_error_count()
        2
    """

    results: List[CheckResult]
    source_type: SourceType
    csv_path: Path
    overall_path: Optional[Path] = None

    def has_errors(self, strict: bool = False) -> bool:
        """Check if validation failed.

        Args:
            strict: If True, treat warnings as errors. Default False.

        Returns:
            True if any errors found (or warnings in strict mode), False otherwise.
        """
        for result in self.results:
            if result.severity == "error" and not result.passed:
                return True
            if strict and result.severity == "warning" and not result.passed:
                return True
        return False

    def get_error_count(self) -> int:
        """Count total number of error-level failures.

        Returns:
            Total count of failures from all error-severity checks.
        """
        return sum(
            r.fail_count for r in self.results if r.severity == "error" and not r.passed
        )

    def get_warning_count(self) -> int:
        """Count total number of warning-level failures.

        Returns:
            Total count of failures from all warning-severity checks.
        """
        return sum(
            r.fail_count for r in self.results if r.severity == "warning" and not r.passed
        )

    def get_failed_checks(self, severity: Optional[str] = None) -> List[CheckResult]:
        """Get all failed checks, optionally filtered by severity.

        Args:
            severity: Filter by severity level ("error" or "warning"). None returns all.

        Returns:
            List of failed CheckResult objects.

        Examples:
            >>> errors = report.get_failed_checks(severity="error")
            >>> warnings = report.get_failed_checks(severity="warning")
            >>> all_failures = report.get_failed_checks()
        """
        return [
            r for r in self.results
            if not r.passed and (severity is None or r.severity == severity)
        ]

    def summary(self) -> str:
        """Generate a concise text summary of validation results.

        Returns:
            Multi-line summary string showing pass/fail counts.

        Examples:
            >>> print(report.summary())
            Validation Summary:
              Source: BUDGET_LAW (data/2023_BUDGET_LAW.csv)
              Checks: 10 total, 8 passed, 2 failed
              Errors: 2
              Warnings: 0
        """
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        errors = self.get_error_count()
        warnings = self.get_warning_count()

        return (
            f"Validation Summary:\n"
            f"  Source: {self.source_type.value} ({self.csv_path.name})\n"
            f"  Checks: {total} total, {passed} passed, {failed} failed\n"
            f"  Errors: {errors}\n"
            f"  Warnings: {warnings}"
        )

    def to_markdown(self) -> str:
        """Generate detailed Markdown validation report.

        Returns:
            Formatted Markdown string with validation results, including:
            - Header with file information and timestamp
            - Summary section with pass/fail counts
            - Passed checks list
            - Failed checks with detailed messages
            - Footer with interpretation guidance link

        Examples:
            >>> markdown = report.to_markdown()
            >>> with open("validation_report.md", "w") as f:
            ...     f.write(markdown)
        """
        from datetime import datetime

        # Calculate statistics
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        errors = self.get_error_count()
        warnings = self.get_warning_count()

        # Group results by status
        passed_checks = [r for r in self.results if r.passed]
        failed_checks = self.get_failed_checks()

        # Build markdown content
        lines = [
            f"# Validation Report: {self.csv_path.name}",
            "",
            f"**Source Type:** {self.source_type.value}",
            f"**File:** {self.csv_path}",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            "",
            f"- **Total Checks:** {total}",
            f"- **Passed:** {passed} ✅",
            f"- **Failed:** {failed} {'❌' if failed > 0 else ''}",
            f"- **Errors:** {errors}",
            f"- **Warnings:** {warnings}",
            "",
        ]

        # Passed checks section
        if passed_checks:
            lines.append("## ✅ Passed Checks")
            lines.append("")
            # Group passed checks by check_id to avoid repetition
            check_groups = {}
            for result in passed_checks:
                if result.check_id not in check_groups:
                    check_groups[result.check_id] = []
                check_groups[result.check_id].append(result)

            for check_id in sorted(check_groups.keys()):
                count = len(check_groups[check_id])
                lines.append(f"- **{check_id}** ({count} passed)")
            lines.append("")

        # Failed checks section
        if failed_checks:
            lines.append("## ❌ Failed Checks")
            lines.append("")

            # Group failed checks by check_id
            check_groups = {}
            for result in failed_checks:
                if result.check_id not in check_groups:
                    check_groups[result.check_id] = []
                check_groups[result.check_id].append(result)

            for check_id in sorted(check_groups.keys()):
                results = check_groups[check_id]
                # Determine icon based on severity
                icon = "❌" if results[0].severity == "error" else "⚠️"
                severity_label = results[0].severity.capitalize()
                total_failures = sum(r.fail_count for r in results)

                lines.append(f"### {icon} {check_id} ({severity_label}) - {total_failures} failures")
                lines.append("")

                # Add all messages from all results for this check
                for result in results:
                    for msg in result.messages:
                        lines.append(f"- {msg}")
                lines.append("")
        else:
            lines.append("## ✅ All Checks Passed")
            lines.append("")
            lines.append("No validation issues found.")
            lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append("For detailed information about validation checks and how to interpret results,")
        lines.append("see [docs/validation.md](https://github.com/your-org/armenian-budget-tools/blob/main/docs/validation.md).")
        lines.append("")

        return "\n".join(lines)
