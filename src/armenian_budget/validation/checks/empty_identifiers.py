"""Empty identifiers validation check.

Budget lines must be identifiable. Empty state body, program name, or subprogram
name prevent proper analysis and aggregation.
"""

from __future__ import annotations

from typing import Dict, List

import pandas as pd

from armenian_budget.core.enums import SourceType
from ..config import get_severity
from ..models import CheckResult


class EmptyIdentifiersCheck:
    """Validate that identifier fields are not empty."""

    def validate(
        self,
        df: pd.DataFrame,
        overall: Dict,
        source_type: SourceType,
    ) -> List[CheckResult]:
        """Check for empty identifiers at each hierarchy level.

        Args:
            df: DataFrame containing CSV data.
            overall: Dictionary from overall.json file (not used by this check).
            source_type: Type of data source being validated.

        Returns:
            List of CheckResult objects (one per hierarchy level with issues).
        """
        results = []

        # Check state_body
        empty_state_body = df["state_body"].isna() | (df["state_body"].str.strip() == "")
        count_state_body = empty_state_body.sum()
        if count_state_body > 0:
            results.append(
                CheckResult(
                    check_id="empty_identifiers",
                    severity=get_severity("empty_identifiers", "state_body"),
                    passed=False,
                    fail_count=count_state_body,
                    messages=[f"Found {count_state_body} rows with empty state_body"],
                )
            )
        else:
            results.append(
                CheckResult(
                    check_id="empty_identifiers",
                    severity=get_severity("empty_identifiers", "state_body"),
                    passed=True,
                    fail_count=0,
                )
            )

        # Check program_name
        empty_program = df["program_name"].isna() | (df["program_name"].str.strip() == "")
        count_program = empty_program.sum()
        if count_program > 0:
            results.append(
                CheckResult(
                    check_id="empty_identifiers",
                    severity=get_severity("empty_identifiers", "program"),
                    passed=False,
                    fail_count=count_program,
                    messages=[f"Found {count_program} rows with empty program_name"],
                )
            )
        else:
            results.append(
                CheckResult(
                    check_id="empty_identifiers",
                    severity=get_severity("empty_identifiers", "program"),
                    passed=True,
                    fail_count=0,
                )
            )

        # Check subprogram_name (skip for MTEP which has no subprograms)
        if source_type != SourceType.MTEP and "subprogram_name" in df.columns:
            empty_subprogram = df["subprogram_name"].isna() | (
                df["subprogram_name"].str.strip() == ""
            )
            count_subprogram = empty_subprogram.sum()
            if count_subprogram > 0:
                results.append(
                    CheckResult(
                        check_id="empty_identifiers",
                        severity=get_severity("empty_identifiers", "subprogram"),
                        passed=False,
                        fail_count=count_subprogram,
                        messages=[f"Found {count_subprogram} rows with empty subprogram_name"],
                    )
                )
            else:
                results.append(
                    CheckResult(
                        check_id="empty_identifiers",
                        severity=get_severity("empty_identifiers", "subprogram"),
                        passed=True,
                        fail_count=0,
                    )
                )

        return results

    def applies_to_source_type(self, source_type: SourceType) -> bool:
        """Check applies to all source types."""
        return True
