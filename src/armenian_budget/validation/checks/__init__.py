"""Validation checks base interface.

This module defines the protocol (interface) that all validation checks must implement.
Each check is responsible for validating a specific aspect of the data (e.g., hierarchical
totals, negative values, percentage calculations).

To implement a new validation check:

1. Create a new file in this directory (e.g., `my_check.py`)
2. Define a class that implements the ValidationCheck protocol
3. Implement the required methods: `validate()` and `applies_to_source_type()`
4. Add the check to the ALL_CHECKS list in registry.py

Example:
    ```python
    # checks/my_check.py
    from typing import List
    import pandas as pd
    from armenian_budget.core.enums import SourceType
    from ..models import CheckResult
    from ..config import get_severity

    class MyCheck:
        def validate(
            self,
            df: pd.DataFrame,
            overall: dict,
            source_type: SourceType
        ) -> List[CheckResult]:
            # Validation logic here
            return [CheckResult(...)]

        def applies_to_source_type(self, source_type: SourceType) -> bool:
            # Return True if check applies to this source type
            return True  # Applies to all types
    ```
"""

from __future__ import annotations

from typing import Dict, List, Protocol

import pandas as pd

from armenian_budget.core.enums import SourceType
from ..models import CheckResult


class ValidationCheck(Protocol):
    """Protocol defining the interface for validation checks.

    All validation checks must implement this interface. Use duck typing
    (Protocol) for flexibility - no need to inherit from a base class.

    Methods:
        validate: Run the validation check and return results.
        applies_to_source_type: Determine if check is applicable to a source type.
    """

    def validate(
        self,
        df: pd.DataFrame,
        overall: Dict,
        source_type: SourceType,
    ) -> List[CheckResult]:
        """Run the validation check.

        Args:
            df: DataFrame containing the CSV data (state body, program, subprogram rows).
            overall: Dictionary from overall.json file (grand totals and metadata).
            source_type: Type of data source being validated.

        Returns:
            List of CheckResult objects (one per hierarchy level or issue type).
            Return empty list if validation passes completely.

        Raises:
            ValueError: If inputs are malformed or missing required fields.

        Examples:
            >>> results = check.validate(df, overall, SourceType.BUDGET_LAW)
            >>> if not results:
            ...     print("All checks passed!")
            >>> else:
            ...     for r in results:
            ...         if not r.passed:
            ...             print(f"Failed: {r.check_id} ({r.fail_count} issues)")
        """
        ...

    def applies_to_source_type(self, source_type: SourceType) -> bool:
        """Check if this validation applies to a given source type.

        Some validations only apply to specific source types:
        - Spending-specific: period ≤ annual plan, execution percentages
        - Budget Law: strict hierarchical totals (0.0 tolerance)
        - MTEP: multi-year projections

        Args:
            source_type: Type of data source.

        Returns:
            True if check should run for this source type, False to skip.

        Examples:
            >>> check.applies_to_source_type(SourceType.SPENDING_Q1)
            True
            >>> check.applies_to_source_type(SourceType.BUDGET_LAW)
            False  # If spending-only check
        """
        ...


__all__ = ["ValidationCheck"]
