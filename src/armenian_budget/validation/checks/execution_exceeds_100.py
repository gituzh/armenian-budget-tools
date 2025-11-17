"""Execution exceeds 100% validation check.

Execution rates above 100% indicate overspending relative to the revised budget.
May be legitimate with additional budget revisions but warrants review.
"""

from __future__ import annotations

from typing import Dict, List

import pandas as pd

from armenian_budget.core.enums import SourceType
from armenian_budget.core.schemas import get_percentage_fields
from ..config import get_severity
from ..models import CheckResult


class ExecutionExceeds100Check:
    """Validate that execution percentages do not exceed 100%."""

    def validate(
        self,
        df: pd.DataFrame,
        overall: Dict,
        source_type: SourceType,
    ) -> List[CheckResult]:
        """Check for execution rates > 100% in percentage fields at all hierarchy levels.

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
        exceeds_overall = [f for f in json_fields if overall.get(f, 0) > 1.0]
        if exceeds_overall:
            results.append(
                CheckResult(
                    check_id="execution_exceeds_100",
                    severity=get_severity("execution_exceeds_100", "overall"),
                    passed=False,
                    fail_count=len(exceeds_overall),
                    messages=[f"Overall execution > 100%: {', '.join(exceeds_overall)}"],
                )
            )
        else:
            results.append(
                CheckResult(
                    check_id="execution_exceeds_100",
                    severity=get_severity("execution_exceeds_100", "overall"),
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
                    exceeds_rows = df[df[field] > 1.0]
                    for index, row in exceeds_rows.iterrows():
                        messages.append(
                            f"Row {index}: Execution > 100% for '{field}' ({row[field]:.2%}) in {row.get('state_body', '')} | {row.get('program_code', '')} | {row.get('subprogram_code', '')}"
                        )

            if messages:
                results.append(
                    CheckResult(
                        check_id="execution_exceeds_100",
                        severity=get_severity("execution_exceeds_100", level),
                        passed=False,
                        fail_count=len(messages),
                        messages=messages,
                    )
                )
            else:
                results.append(
                    CheckResult(
                        check_id="execution_exceeds_100",
                        severity=get_severity("execution_exceeds_100", level),
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
