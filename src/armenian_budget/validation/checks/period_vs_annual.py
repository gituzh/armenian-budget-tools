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

        def check_pair(p_val, a_val, p_name, a_name):
            # Rule 1: Annual >= 0 AND Period > Annual
            if a_val >= 0 and p_val > a_val:
                return f"{p_name} ({p_val}) exceeds limit {a_name} ({a_val})"
            # Rule 2: Annual < 0 AND Period < Annual
            if a_val < 0 and p_val < a_val:
                return f"{p_name} ({p_val}) exceeds limit {a_name} ({a_val})"
            # Rule 3: Mixed Signs
            if ((a_val >= 0 and p_val < 0) or (a_val <= 0 and p_val > 0)) and p_val != 0:
                return f"{p_name} ({p_val}) exceeds limit {a_name} ({a_val})"
            return None

        if "overall_period_plan" in overall and "overall_annual_plan" in overall:
            msg = check_pair(
                overall["overall_period_plan"],
                overall["overall_annual_plan"],
                "overall_period_plan",
                "overall_annual_plan",
            )
            if msg:
                violations.append(msg)

        if "overall_rev_period_plan" in overall and "overall_rev_annual_plan" in overall:
            msg = check_pair(
                overall["overall_rev_period_plan"],
                overall["overall_rev_annual_plan"],
                "overall_rev_period_plan",
                "overall_rev_annual_plan",
            )
            if msg:
                violations.append(msg)

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

            messages = []

            # Check period_plan vs annual_plan
            if period_field in df.columns and annual_field in df.columns:
                # Rule 1: Annual >= 0 AND Period > Annual
                violations_rule1 = df[
                    (df[annual_field] >= 0) & (df[period_field] > df[annual_field])
                ]

                # Rule 2: Annual < 0 AND Period < Annual
                violations_rule2 = df[
                    (df[annual_field] < 0) & (df[period_field] < df[annual_field])
                ]

                # Rule 3: Mixed Signs (and Period is not 0)
                violations_rule3 = df[
                    (
                        ((df[annual_field] >= 0) & (df[period_field] < 0))
                        | ((df[annual_field] <= 0) & (df[period_field] > 0))
                    )
                    & (df[period_field] != 0)
                ]

                violations = pd.concat(
                    [violations_rule1, violations_rule2, violations_rule3]
                ).drop_duplicates()

                for _, row in violations.iterrows():
                    diff = row[period_field] - row[annual_field]
                    messages.append(
                        f"{level.capitalize()} violation: '{period_field}' "
                        f"({row[period_field]:.2f}) exceeds limit '{annual_field}' "
                        f"({row[annual_field]:.2f}) by {abs(diff):.2f} for "
                        f"{row.get('state_body', '')} | {row.get('program_code', '')} | "
                        f"{row.get('subprogram_code', '')}"
                    )

            # Check rev_period_plan vs rev_annual_plan
            if rev_period_field in df.columns and rev_annual_field in df.columns:
                # Rule 1: Annual >= 0 AND Period > Annual
                violations_rule1_rev = df[
                    (df[rev_annual_field] >= 0) & (df[rev_period_field] > df[rev_annual_field])
                ]

                # Rule 2: Annual < 0 AND Period < Annual
                violations_rule2_rev = df[
                    (df[rev_annual_field] < 0) & (df[rev_period_field] < df[rev_annual_field])
                ]

                # Rule 3: Mixed Signs (and Period is not 0)
                violations_rule3_rev = df[
                    (
                        ((df[rev_annual_field] >= 0) & (df[rev_period_field] < 0))
                        | ((df[rev_annual_field] <= 0) & (df[rev_period_field] > 0))
                    )
                    & (df[rev_period_field] != 0)
                ]

                violations_rev = pd.concat(
                    [violations_rule1_rev, violations_rule2_rev, violations_rule3_rev]
                ).drop_duplicates()

                for _, row in violations_rev.iterrows():
                    diff = row[rev_period_field] - row[rev_annual_field]
                    messages.append(
                        f"{level.capitalize()} violation: '{rev_period_field}' "
                        f"({row[rev_period_field]:.2f}) exceeds limit '{rev_annual_field}' "
                        f"({row[rev_annual_field]:.2f}) by {abs(diff):.2f} for "
                        f"{row.get('state_body', '')} | {row.get('program_code', '')} | "
                        f"{row.get('subprogram_code', '')}"
                    )

            if messages:
                results.append(
                    CheckResult(
                        check_id="period_vs_annual",
                        severity=get_severity("period_vs_annual", level),
                        passed=False,
                        fail_count=len(messages),
                        messages=messages,
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
