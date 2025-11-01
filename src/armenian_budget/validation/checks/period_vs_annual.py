"""Period vs Annual Plan validation check.

Period budgets cannot exceed annual budgets. Violations indicate data entry errors
or structural problems in the budget planning process.
"""

from __future__ import annotations

from typing import Dict, List

import pandas as pd

from armenian_budget.core.enums import SourceType
from ..config import get_severity
from ..models import CheckResult


class PeriodVsAnnualCheck:
    """Validate that period plans do not exceed annual plans."""

    def validate(
        self,
        df: pd.DataFrame,
        overall: Dict,
        source_type: SourceType,
    ) -> List[CheckResult]:
        """Check that period_plan ≤ annual_plan at all hierarchy levels.

        Verifies:
        1. period_plan ≤ annual_plan
        2. rev_period_plan ≤ rev_annual_plan

        Args:
            df: DataFrame containing CSV data.
            overall: Dictionary from overall.json file.
            source_type: Type of data source being validated.

        Returns:
            List of CheckResult objects (one per hierarchy level with issues).
        """
        results = []

        # Check overall JSON
        violations = []
        if "overall_period_plan" in overall and "overall_annual_plan" in overall:
            if overall["overall_period_plan"] > overall["overall_annual_plan"]:
                violations.append(
                    f"overall_period_plan ({overall['overall_period_plan']}) > "
                    f"overall_annual_plan ({overall['overall_annual_plan']})"
                )
        if "overall_rev_period_plan" in overall and "overall_rev_annual_plan" in overall:
            if overall["overall_rev_period_plan"] > overall["overall_rev_annual_plan"]:
                violations.append(
                    f"overall_rev_period_plan ({overall['overall_rev_period_plan']}) > "
                    f"overall_rev_annual_plan ({overall['overall_rev_annual_plan']})"
                )

        if violations:
            results.append(
                CheckResult(
                    check_id="period_vs_annual",
                    severity=get_severity("period_vs_annual", "overall"),
                    passed=False,
                    fail_count=len(violations),
                    messages=[f"Overall violations: {', '.join(violations)}"],
                )
            )
        else:
            results.append(
                CheckResult(
                    check_id="period_vs_annual",
                    severity=get_severity("period_vs_annual", "overall"),
                    passed=True,
                    fail_count=0,
                )
            )

        # Check CSV by hierarchy level
        for level in ["state_body", "program", "subprogram"]:
            period_field = f"{level}_period_plan"
            annual_field = f"{level}_annual_plan"
            rev_period_field = f"{level}_rev_period_plan"
            rev_annual_field = f"{level}_rev_annual_plan"

            # Check both period vs annual comparisons
            total_violations = 0
            violation_details = []

            # Check period_plan ≤ annual_plan
            if period_field in df.columns and annual_field in df.columns:
                period_violations = (df[period_field] > df[annual_field]).sum()
                if period_violations > 0:
                    total_violations += period_violations
                    violation_details.append(f"{period_field} > {annual_field} ({period_violations} rows)")

            # Check rev_period_plan ≤ rev_annual_plan
            if rev_period_field in df.columns and rev_annual_field in df.columns:
                rev_violations = (df[rev_period_field] > df[rev_annual_field]).sum()
                if rev_violations > 0:
                    total_violations += rev_violations
                    violation_details.append(f"{rev_period_field} > {rev_annual_field} ({rev_violations} rows)")

            if total_violations > 0:
                results.append(
                    CheckResult(
                        check_id="period_vs_annual",
                        severity=get_severity("period_vs_annual", level),
                        passed=False,
                        fail_count=total_violations,
                        messages=[f"{level.capitalize()} violations: {', '.join(violation_details)}"],
                    )
                )
            else:
                results.append(
                    CheckResult(
                        check_id="period_vs_annual",
                        severity=get_severity("period_vs_annual", level),
                        passed=True,
                        fail_count=0,
                    )
                )

        return results

    def applies_to_source_type(self, source_type: SourceType) -> bool:
        """Check only applies to Q1/Q12/Q123 spending reports (has period fields)."""
        return source_type in (
            SourceType.SPENDING_Q1,
            SourceType.SPENDING_Q12,
            SourceType.SPENDING_Q123,
        )
