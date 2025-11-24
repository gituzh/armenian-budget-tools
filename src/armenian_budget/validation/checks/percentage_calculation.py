"""Percentage calculation correctness validation check.

Reported percentages must match calculated values (actual / denominator) within tolerance.
Mismatches indicate calculation errors or inconsistencies in the source data.
"""

from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd

from armenian_budget.core.enums import SourceType
from ..config import PERCENTAGE_TOL, get_severity
from ..models import CheckResult


class PercentageCalculationCheck:
    """Validate that reported percentages match calculated values."""

    def validate(
        self,
        df: pd.DataFrame,
        overall: Dict,
        source_type: SourceType,
    ) -> List[CheckResult]:
        """Check that reported percentages = actual / denominator (within tolerance).

        Verifies:
        - *_actual_vs_rev_annual_plan = *_actual / *_rev_annual_plan
        - *_actual_vs_rev_period_plan = *_actual / *_rev_period_plan (Q1/Q12/Q123 only)

        Args:
            df: DataFrame containing CSV data.
            overall: Dictionary from overall.json file.
            source_type: Type of data source being validated.

        Returns:
            List of CheckResult objects (one per hierarchy level per percentage type).
        """
        results = []

        # Define percentage calculations to check
        if source_type in (
            SourceType.SPENDING_Q1,
            SourceType.SPENDING_Q12,
            SourceType.SPENDING_Q123,
        ):
            # Q1/Q12/Q123 have two percentage types
            checks = [
                ("actual_vs_rev_annual_plan", "actual", "rev_annual_plan"),
                ("actual_vs_rev_period_plan", "actual", "rev_period_plan"),
            ]
        else:  # SPENDING_Q1234
            # Q1234 has one percentage type
            checks = [
                ("actual_vs_rev_annual_plan", "actual", "rev_annual_plan"),
            ]

        # Check each percentage type
        for pct_field, numerator_field, denominator_field in checks:
            # Check overall JSON
            overall_pct = f"overall_{pct_field}"
            overall_num = f"overall_{numerator_field}"
            overall_denom = f"overall_{denominator_field}"

            if (
                overall_pct in overall
                and overall_num in overall
                and overall_denom in overall
                and pd.notna(overall[overall_denom])
                and overall[overall_denom] != 0
            ):
                expected = overall[overall_num] / overall[overall_denom]
                reported = overall[overall_pct]

                if not np.isclose(expected, reported, atol=PERCENTAGE_TOL):
                    results.append(
                        CheckResult(
                            check_id="percentage_calculation",
                            severity=get_severity("percentage_calculation", "overall"),
                            passed=False,
                            fail_count=1,
                            messages=[
                                f"Overall {pct_field}: expected {expected:.4f}, "
                                f"reported {reported:.4f}, diff {abs(expected - reported):.4f} "
                                f"(tolerance {PERCENTAGE_TOL})"
                            ],
                        )
                    )
                else:
                    results.append(
                        CheckResult(
                            check_id="percentage_calculation",
                            severity=get_severity("percentage_calculation", "overall"),
                            passed=True,
                            fail_count=0,
                        )
                    )
            else:
                # Denominator is zero or missing - pass (can't validate)
                results.append(
                    CheckResult(
                        check_id="percentage_calculation",
                        severity=get_severity("percentage_calculation", "overall"),
                        passed=True,
                        fail_count=0,
                    )
                )

            # Check CSV by hierarchy level
            for level in ["state_body", "program", "subprogram"]:
                level_pct = f"{level}_{pct_field}"
                level_num = f"{level}_{numerator_field}"
                level_denom = f"{level}_{denominator_field}"

                if (
                    level_pct in df.columns
                    and level_num in df.columns
                    and level_denom in df.columns
                ):
                    # Calculate expected percentage (avoid division by zero)
                    df_check = df[pd.notna(df[level_denom]) & (df[level_denom] != 0)].copy()
                    if len(df_check) == 0:
                        # All denominators are zero - pass
                        results.append(
                            CheckResult(
                                check_id="percentage_calculation",
                                severity=get_severity("percentage_calculation", level),
                                passed=True,
                                fail_count=0,
                            )
                        )
                        continue

                    df_check["expected"] = df_check[level_num] / df_check[level_denom]

                    mismatch_rows = df_check[
                        ~np.isclose(df_check[level_pct], df_check["expected"], atol=PERCENTAGE_TOL)
                    ]

                    messages = []
                    for index, row in mismatch_rows.iterrows():
                        messages.append(
                            f"Row {index}: Mismatch for '{level_pct}'. "
                            f"Expected: {row['expected']:.4f}, "
                            f"Reported: {row[level_pct]:.4f}, "
                            f"Diff: {abs(row['expected'] - row[level_pct]):.4f} "
                            f"in {row.get('state_body', '')} | {row.get('program_code', '')} | "
                            f"{row.get('subprogram_code', '')}"
                        )

                    if messages:
                        results.append(
                            CheckResult(
                                check_id="percentage_calculation",
                                severity=get_severity("percentage_calculation", level),
                                passed=False,
                                fail_count=len(messages),
                                messages=messages,
                            )
                        )
                    else:
                        results.append(
                            CheckResult(
                                check_id="percentage_calculation",
                                severity=get_severity("percentage_calculation", level),
                                passed=True,
                                fail_count=0,
                            )
                        )
                else:
                    # Fields not present - pass (not applicable)
                    results.append(
                        CheckResult(
                            check_id="percentage_calculation",
                            severity=get_severity("percentage_calculation", level),
                            passed=True,
                            fail_count=0,
                        )
                    )

        return results

    def applies_to_source_type(self, source_type: SourceType) -> bool:
        """Check applies to all spending reports only (Budget Law and MTEP have no percentages)."""
        return source_type in (
            SourceType.SPENDING_Q1,
            SourceType.SPENDING_Q12,
            SourceType.SPENDING_Q123,
            SourceType.SPENDING_Q1234,
        )
