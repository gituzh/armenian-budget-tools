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

        # Define identifier fields to check: (column_name, hierarchy_level)
        identifiers = [
            ("state_body", "state_body"),
            ("program_name", "program"),
            ("subprogram_name", "subprogram"),
        ]

        for field_name, level in identifiers:
            # Skip subprogram for MTEP (no subprograms)
            if level == "subprogram" and source_type == SourceType.MTEP:
                continue

            # Skip if field not in dataframe
            if field_name not in df.columns:
                continue

            # Check for empty values (null or whitespace-only strings)
            empty_mask = df[field_name].isna() | (df[field_name].str.strip() == "")
            count = empty_mask.sum()

            if count > 0:
                results.append(
                    CheckResult(
                        check_id="empty_identifiers",
                        severity=get_severity("empty_identifiers", level),
                        passed=False,
                        fail_count=count,
                        messages=[f"Found {count} rows with empty {field_name}"],
                    )
                )
            else:
                results.append(
                    CheckResult(
                        check_id="empty_identifiers",
                        severity=get_severity("empty_identifiers", level),
                        passed=True,
                        fail_count=0,
                    )
                )

        return results

    def applies_to_source_type(self, source_type: SourceType) -> bool:
        """Check applies to all source types."""
        return True
