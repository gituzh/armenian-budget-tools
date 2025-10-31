"""Negative totals validation check.

Negative amounts indicate data corruption. Subprogram-level negatives may be legitimate
budget corrections, but negative totals at higher levels are always problematic.
"""

from __future__ import annotations

from typing import Dict, List

import pandas as pd

from armenian_budget.core.enums import SourceType
from armenian_budget.core.schemas import get_amount_fields
from ..config import get_severity
from ..models import CheckResult


class NegativeTotalsCheck:
    """Validate that amount fields are not negative."""

    def validate(
        self,
        df: pd.DataFrame,
        overall: Dict,
        source_type: SourceType,
    ) -> List[CheckResult]:
        """Check for negative values in amount fields at all hierarchy levels.

        Args:
            df: DataFrame containing CSV data.
            overall: Dictionary from overall.json file.
            source_type: Type of data source being validated.

        Returns:
            List of CheckResult objects (one per hierarchy level with issues).
        """
        results = []
        csv_fields, json_fields = get_amount_fields(source_type)

        # Check overall JSON
        negative_overall = [f for f in json_fields if overall.get(f, 0) < 0]
        if negative_overall:
            results.append(
                CheckResult(
                    check_id="negative_totals",
                    severity=get_severity("negative_totals", "overall"),
                    passed=False,
                    fail_count=len(negative_overall),
                    messages=[f"Negative overall fields: {', '.join(negative_overall)}"],
                )
            )
        else:
            results.append(
                CheckResult(
                    check_id="negative_totals",
                    severity=get_severity("negative_totals", "overall"),
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

            # Count negatives across all level fields
            total_negatives = 0
            negative_fields = []
            for field in level_fields:
                if field in df.columns:
                    negative_count = (df[field] < 0).sum()
                    if negative_count > 0:
                        total_negatives += negative_count
                        negative_fields.append(f"{field} ({negative_count} rows)")

            if total_negatives > 0:
                results.append(
                    CheckResult(
                        check_id="negative_totals",
                        severity=get_severity("negative_totals", level),
                        passed=False,
                        fail_count=total_negatives,
                        messages=[f"Negative {level} values: {', '.join(negative_fields)}"],
                    )
                )
            else:
                results.append(
                    CheckResult(
                        check_id="negative_totals",
                        severity=get_severity("negative_totals", level),
                        passed=True,
                        fail_count=0,
                    )
                )

        return results

    def applies_to_source_type(self, source_type: SourceType) -> bool:
        """Check applies to all source types."""
        return True
