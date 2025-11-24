"""Hierarchical structure sanity check.

Verify that the budget hierarchy has reasonable structure (not degenerate/flat).
This is a sanity check to catch parser failures or data quality issues.
"""

from __future__ import annotations

from typing import Dict, List

import pandas as pd

from armenian_budget.core.enums import SourceType
from ..config import get_severity
from ..models import CheckResult


class HierarchicalStructureSanityCheck:
    """Validate that the budget hierarchy has reasonable structure."""

    def validate(self, df: pd.DataFrame) -> List[CheckResult]:
        """Check that the hierarchical structure is not degenerate.

        Verifies:
        1. Not all state bodies have identical program counts (variety exists)
        2. At least one state body has multiple programs (depth exists)

        Args:
            df: DataFrame containing CSV data.

        Returns:
            List with one CheckResult object.
        """
        messages = []

        # Count programs per state body
        program_counts = df.groupby("state_body")["program_code"].nunique()

        # Check 1: Not all state bodies should have identical counts
        if program_counts.nunique() == 1:
            messages.append(
                f"All state bodies have identical program count ({program_counts.iloc[0]}). "
                "This suggests degenerate hierarchy or parser failure."
            )

        # Check 2: At least one state body should have multiple programs
        if program_counts.max() == 1:
            messages.append(
                "No state body has multiple programs. "
                "This suggests flat/broken hierarchical structure."
            )

        if messages:
            return [
                CheckResult(
                    check_id="hierarchical_structure_sanity",
                    severity=get_severity("hierarchical_structure_sanity", "overall"),
                    passed=False,
                    fail_count=len(messages),
                    messages=messages,
                )
            ]
        else:
            return [
                CheckResult(
                    check_id="hierarchical_structure_sanity",
                    severity=get_severity("hierarchical_structure_sanity", "overall"),
                    passed=True,
                    fail_count=0,
                )
            ]

    def applies_to_source_type(self, source_type: SourceType) -> bool:
        """Check only applies to BUDGET_LAW (has hierarchical structure)."""
        return source_type == SourceType.BUDGET_LAW
