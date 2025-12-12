"""Required fields validation check.

Ensures all expected columns are present in CSV and overall JSON based on source type.
Missing fields prevent analysis and indicate incomplete data processing.
"""

from __future__ import annotations

from typing import Dict, List

import pandas as pd

from armenian_budget.core.enums import SourceType
from armenian_budget.core.schemas import get_required_fields
from ..models import CheckResult


class RequiredFieldsCheck:
    """Validate that all required fields are present."""

    def validate(
        self,
        df: pd.DataFrame,
        overall: Dict,
        source_type: SourceType,
    ) -> List[CheckResult]:
        """Check that all required CSV and JSON fields are present.

        Args:
            df: DataFrame containing CSV data.
            overall: Dictionary from overall.json file.
            source_type: Type of data source being validated.

        Returns:
            List containing single CheckResult indicating pass/fail with missing fields.
        """
        missing = []

        # Get required fields for this source type
        required_csv, required_json = get_required_fields(source_type)

        # Check CSV columns
        csv_cols = set(df.columns)
        for field in required_csv:
            if field not in csv_cols:
                missing.append(f"CSV: {field}")

        # Check JSON fields
        for field in required_json:
            if field not in overall:
                missing.append(f"JSON: {field}")

        if missing:
            return [
                CheckResult(
                    check_id="required_fields",
                    severity="error",
                    passed=False,
                    fail_count=len(missing),
                    messages=[f"Missing fields: {', '.join(missing)}"],
                )
            ]

        return [
            CheckResult(
                check_id="required_fields",
                severity="error",
                passed=True,
                fail_count=0,
            )
        ]

    def applies_to_source_type(self, source_type: SourceType) -> bool:
        """Check applies to all source types."""
        return True
