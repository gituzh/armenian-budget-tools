"""Validation checks interface documentation.

This module documents the interface convention for validation checks.
Each check is responsible for validating a specific aspect of the data.

## Budget Validation Checks

Budget validation checks (for Budget Law, Spending Reports, MTEP) follow this pattern:

**Required methods:**
- `validate(df, overall, source_type) -> List[CheckResult]`
  - Runs the validation check on data
  - Returns list of CheckResult objects (one per hierarchy level or issue type)

- `applies_to_source_type(source_type) -> bool`
  - Returns True if check applies to the given source type
  - Used by registry to filter checks before execution

**Example:**
```python
# checks/my_check.py
from typing import Dict, List
import pandas as pd
from armenian_budget.core.enums import SourceType
from ..models import CheckResult
from ..config import get_severity

class MyCheck:
    def validate(
        self,
        df: pd.DataFrame,
        overall: Dict,
        source_type: SourceType
    ) -> List[CheckResult]:
        # Validation logic here
        return [CheckResult(...)]

    def applies_to_source_type(self, source_type: SourceType) -> bool:
        return True  # Applies to all types
```

## Other Check Types

For future check types (KPI validation, cross-validation, etc.), implement methods
appropriate to the validation type. The interface is convention-based (duck typing),
not enforced by type system.

## Adding a New Check

1. Create a new file in this directory (e.g., `my_check.py`)
2. Implement the methods shown above (or appropriate for your check type)
3. Add the check instance to ALL_CHECKS in registry.py
"""

__all__: list[str] = []
