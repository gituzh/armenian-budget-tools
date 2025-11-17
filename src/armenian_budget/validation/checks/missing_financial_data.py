"""Missing financial data validation check.

Financial amounts and percentages must not be empty (null/NaN). Missing values
prevent analysis and indicate incomplete data processing.
"""

from __future__ import annotations

from typing import Dict, List

import pandas as pd

from armenian_budget.core.enums import SourceType
from armenian_budget.core.schemas import get_financial_fields
from ..config import get_severity
from ..models import CheckResult


class MissingFinancialDataCheck:
    """Validate that financial fields are not null/NaN."""

    def validate(
        self,
        df: pd.DataFrame,
        overall: Dict,
        source_type: SourceType,
    ) -> List[CheckResult]:
        """Check for missing (null/NaN) financial data at each hierarchy level.

        Args:
            df: DataFrame containing CSV data.
            overall: Dictionary from overall.json file.
            source_type: Type of data source being validated.

        Returns:
            List of CheckResult objects (one per hierarchy level with issues).
        """
        results = []
        csv_fields, json_fields = get_financial_fields(source_type)

        # Check overall JSON
        missing_overall = [f for f in json_fields if overall.get(f) is None]
        if missing_overall:
            results.append(
                CheckResult(
                    check_id="missing_financial_data",
                    severity=get_severity("missing_financial_data", "overall"),
                    passed=False,
                    fail_count=len(missing_overall),
                    messages=[f"Missing overall fields: {', '.join(missing_overall)}"],
                )
            )
        else:
            results.append(
                CheckResult(
                    check_id="missing_financial_data",
                    severity=get_severity("missing_financial_data", "overall"),
                    passed=True,
                    fail_count=0,
                )
            )

        # Check CSV by hierarchy level
        for level in ["state_body", "program", "subprogram"]:
            # Get fields for this level
            level_fields = [f for f in csv_fields if f.startswith(f"{level}_")]

            # Skip subprogram for MTEP
            if level == "subprogram" and source_type == SourceType.MTEP:
                continue

            messages = []
            for field in level_fields:
                if field in df.columns:
                    missing_rows = df[df[field].isna()]
                    for index, row in missing_rows.iterrows():
                        messages.append(
                            f"Row {index}: Missing data for '{field}' in {row.get('state_body', '')} | {row.get('program_code', '')} | {row.get('subprogram_code', '')}"
                        )

            if messages:
                results.append(
                    CheckResult(
                        check_id="missing_financial_data",
                        severity=get_severity("missing_financial_data", level),
                        passed=False,
                        fail_count=len(messages),
                        messages=messages,
                    )
                )
            else:
                results.append(
                    CheckResult(
                        check_id="missing_financial_data",
                        severity=get_severity("missing_financial_data", level),
                        passed=True,
                        fail_count=0,
                    )
                )

        return results

    def applies_to_source_type(self, source_type: SourceType) -> bool:
        """Check applies to all source types."""
        return True
