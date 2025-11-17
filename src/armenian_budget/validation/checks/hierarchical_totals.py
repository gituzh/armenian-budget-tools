"""Hierarchical totals validation check.

Budget hierarchy must sum correctly at all levels. Differences within tolerance may be
rounding errors; larger differences indicate data quality problems.
"""

from __future__ import annotations

from typing import Dict, List

import pandas as pd

from armenian_budget.core.enums import SourceType
from armenian_budget.core.schemas import get_amount_fields
from ..config import get_tolerance_for_source
from ..models import CheckResult


class HierarchicalTotalsCheck:
    """Validate hierarchical totals sum correctly."""

    def validate(
        self,
        df: pd.DataFrame,
        overall: Dict,
        source_type: SourceType,
    ) -> List[CheckResult]:
        """Check that hierarchical totals sum correctly at all levels.

        Verifies:
        1. Overall JSON total = Σ unique state_body totals
        2. State body total = Σ program totals (for each state body)
        3. Program total = Σ subprogram totals (for each program)

        Args:
            df: DataFrame containing CSV data.
            overall: Dictionary from overall.json file.
            source_type: Type of data source being validated.

        Returns:
            List of CheckResult objects (one per hierarchy level per field).
        """
        results = []
        tolerance = get_tolerance_for_source(source_type)
        csv_fields, json_fields = get_amount_fields(source_type)

        # Extract field base names (e.g., "annual_plan" from "state_body_annual_plan")
        field_bases = self._get_field_bases(csv_fields)

        for base in field_bases:
            overall_field = f"overall_{base}"
            state_body_field = f"state_body_{base}"
            program_field = f"program_{base}"
            subprogram_field = f"subprogram_{base}"

            # Check 1: Overall vs State Bodies
            if overall_field in json_fields and state_body_field in df.columns:
                results.append(
                    self._check_overall_vs_state_bodies(
                        df, overall, overall_field, state_body_field, tolerance
                    )
                )

            # Check 2: State Body vs Programs
            if state_body_field in df.columns and program_field in df.columns:
                results.append(
                    self._check_state_body_vs_programs(
                        df, state_body_field, program_field, tolerance
                    )
                )

            # Check 3: Program vs Subprograms (skip for MTEP)
            if (
                source_type != SourceType.MTEP
                and program_field in df.columns
                and subprogram_field in df.columns
            ):
                results.append(
                    self._check_program_vs_subprograms(
                        df, program_field, subprogram_field, tolerance
                    )
                )

        return results

    def applies_to_source_type(self, source_type: SourceType) -> bool:
        """Check applies to all source types."""
        return True

    def _get_field_bases(self, csv_fields: List[str]) -> List[str]:
        """Extract field base names from CSV fields.

        Args:
            csv_fields: List of CSV field names.

        Returns:
            List of unique base names (e.g., "annual_plan", "total").
        """
        bases = set()
        for field in csv_fields:
            # Remove prefix (state_body_, program_, subprogram_)
            for prefix in ["state_body_", "program_", "subprogram_"]:
                if field.startswith(prefix):
                    bases.add(field[len(prefix) :])
                    break
        return sorted(bases)

    def _check_overall_vs_state_bodies(
        self,
        df: pd.DataFrame,
        overall: Dict,
        overall_field: str,
        state_body_field: str,
        tolerance: float,
    ) -> CheckResult:
        """Check overall JSON total equals sum of unique state body totals."""
        overall_value = overall.get(overall_field, 0)

        # Get unique state bodies and their totals
        unique_state_bodies = df.groupby("state_body")[state_body_field].first()
        state_body_sum = unique_state_bodies.sum()

        diff = abs(overall_value - state_body_sum)

        if diff <= tolerance:
            return CheckResult(
                check_id="hierarchical_totals",
                severity="error",
                passed=True,
                fail_count=0,
            )

        return CheckResult(
            check_id="hierarchical_totals",
            severity="error",
            passed=False,
            fail_count=1,
            messages=[
                f"Overall {overall_field}: expected {state_body_sum}, "
                f"got {overall_value}, diff {diff} (tolerance {tolerance})"
            ],
        )

    def _check_state_body_vs_programs(
        self,
        df: pd.DataFrame,
        state_body_field: str,
        program_field: str,
        tolerance: float,
    ) -> CheckResult:
        """Check each state body total equals sum of its program totals."""
        failures = []

        for state_body_name in df["state_body"].unique():
            state_body_df = df[df["state_body"] == state_body_name]

            # Get unique programs and their totals for this state body
            unique_programs = state_body_df.groupby("program_name")[program_field].first()
            program_sum = unique_programs.sum()

            # Get state body total (should be same for all rows)
            state_body_total = state_body_df[state_body_field].iloc[0]

            diff = abs(state_body_total - program_sum)
            if diff > tolerance:
                failures.append(
                    f"{state_body_name}: expected {program_sum}, got {state_body_total}, diff {diff}"
                )

        if not failures:
            return CheckResult(
                check_id="hierarchical_totals",
                severity="error",
                passed=True,
                fail_count=0,
            )

        return CheckResult(
            check_id="hierarchical_totals",
            severity="error",
            passed=False,
            fail_count=len(failures),
            messages=failures,
        )

    def _check_program_vs_subprograms(
        self,
        df: pd.DataFrame,
        program_field: str,
        subprogram_field: str,
        tolerance: float,
    ) -> CheckResult:
        """Check each program total equals sum of its subprogram totals."""
        failures = []

        for (state_body_name, program_name), group in df.groupby(["state_body", "program_name"]):
            program_total = group[program_field].iloc[0]
            subprogram_sum = group[subprogram_field].sum()

            diff = abs(program_total - subprogram_sum)
            if diff > tolerance:
                failures.append(
                    f"{state_body_name}/{program_name}: expected {subprogram_sum}, "
                    f"got {program_total}, diff {diff}"
                )

        if not failures:
            return CheckResult(
                check_id="hierarchical_totals",
                severity="error",
                passed=True,
                fail_count=0,
            )

        return CheckResult(
            check_id="hierarchical_totals",
            severity="error",
            passed=False,
            fail_count=len(failures),
            messages=failures,
        )
