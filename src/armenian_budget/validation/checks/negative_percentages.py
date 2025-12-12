"""Negative percentages validation check.

Negative percentages are mathematically impossible and indicate data corruption
or calculation errors in the source data.
"""

from __future__ import annotations

from typing import Dict, List

import pandas as pd

from armenian_budget.core.enums import SourceType
from armenian_budget.core.schemas import get_percentage_fields
from ..config import get_severity
from ..models import CheckResult


class NegativePercentagesCheck:
    """Validate that percentage fields are not negative."""

    def validate(
        self,
        df: pd.DataFrame,
        overall: Dict,
        source_type: SourceType,
    ) -> List[CheckResult]:
        """Check for negative values in percentage fields at all hierarchy levels.

        Args:
            df: DataFrame containing CSV data.
            overall: Dictionary from overall.json file.
            source_type: Type of data source being validated.

        Returns:
            List of CheckResult objects (one per hierarchy level with issues).
        """
        results = []
        csv_fields, json_fields = get_percentage_fields(source_type)

        # Check overall JSON
        negative_overall = [f for f in json_fields if overall.get(f, 0) < 0]
        if negative_overall:
            results.append(
                CheckResult(
                    check_id="negative_percentages",
                    severity=get_severity("negative_percentages", "overall"),
                    passed=False,
                    fail_count=len(negative_overall),
                    messages=[f"Negative overall percentages: {', '.join(negative_overall)}"],
                )
            )
        else:
            results.append(
                CheckResult(
                    check_id="negative_percentages",
                    severity=get_severity("negative_percentages", "overall"),
                    passed=True,
                    fail_count=0,
                )
            )

        # Check CSV by hierarchy level
        for level in ["state_body", "program", "subprogram"]:
            # Get percentage fields for this level
            level_fields = [f for f in csv_fields if f.startswith(f"{level}_")]

            messages = []
            for field in level_fields:
                if field in df.columns:
                    negative_rows = df[df[field] < 0]
                    for index, row in negative_rows.iterrows():
                        messages.append(
                            f"Row {index}: Negative percentage for '{field}' ({row[field]:.2%}) in "
                            f"{row.get('state_body', '')} | {row.get('program_code', '')} | "
                            f"{row.get('subprogram_code', '')}"
                        )

            if messages:
                results.append(
                    CheckResult(
                        check_id="negative_percentages",
                        severity=get_severity("negative_percentages", level),
                        passed=False,
                        fail_count=len(messages),
                        messages=messages,
                    )
                )
            else:
                results.append(
                    CheckResult(
                        check_id="negative_percentages",
                        severity=get_severity("negative_percentages", level),
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
