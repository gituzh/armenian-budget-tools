"""Excel parsers for Armenian budget and spending data.

This package provides separate modules for the historical (2019–2024)
Excel format and the 2025 Excel format.

Public API:
 - flatten_budget_excel_2019_2024
 - flatten_budget_excel_2025
 - SourceType, ProcessingState, RowType (from 2019–2024 module)
"""

from armenian_budget.core.enums import SourceType
from ._common import (
    ProcessingState,
    RowType,
    is_numeric,
    normalize_str,
)
from .excel_2019_2024 import (
    flatten_budget_excel_2019_2024,
    _detect_row_type_2019_2024,
    _extract_subprogram_code,
    _parse_fraction,
)
from .excel_2025 import flatten_budget_excel_2025, _detect_row_type_2025

__all__ = [
    # 2019–2024
    "flatten_budget_excel_2019_2024",
    "SourceType",
    "ProcessingState",
    "RowType",
    "_detect_row_type_2019_2024",
    "_extract_subprogram_code",
    # common helpers
    "is_numeric",
    "normalize_str",
    "_parse_fraction",
    # 2025
    "flatten_budget_excel_2025",
    "_detect_row_type_2025",
]
