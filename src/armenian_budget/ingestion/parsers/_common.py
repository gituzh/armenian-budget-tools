"""Shared parser helpers and state enums."""

from __future__ import annotations

import logging
from enum import Enum, auto
from armenian_budget.core.enums import SourceType


logger = logging.getLogger(__name__)


class ProcessingState(Enum):
    """
    State machine states for parsing the budget Excel:
    - INIT: Searching for the overall values row
    - READY: Ready to process entities after overall values
    - STATE_BODY: Processing a state body header row
    - PROGRAM: Processing a program header row
    - SUBPROGRAM: Processing a subprogram header row
    """

    INIT = auto()
    READY = auto()
    STATE_BODY = auto()
    PROGRAM = auto()
    SUBPROGRAM = auto()


class RowType(Enum):
    """
    Row types for parsing the budget Excel:
    - GRAND_TOTAL: Grand total row
    - STATE_BODY_HEADER: State body header row
    - PROGRAM_HEADER: Program header row
    - SUBPROGRAM_MARKER: Subprogram marker row
    - SUBPROGRAM_HEADER: Subprogram header row
    - DETAIL_LINE: Detail line row
    - EMPTY: All columns empty or whitespace
    - UNKNOWN: Doesn't match any pattern
    """

    GRAND_TOTAL = auto()
    STATE_BODY_HEADER = auto()
    PROGRAM_HEADER = auto()
    SUBPROGRAM_MARKER = auto()
    SUBPROGRAM_HEADER = auto()
    DETAIL_LINE = auto()
    EMPTY = auto()
    UNKNOWN = auto()


def is_numeric(val) -> bool:
    """Returns True if val can be converted to float."""
    try:
        float(val)
        return True
    except ValueError:
        return False


def normalize_str(s: str) -> str:
    """Trim, lowercase, and remove spaces from a string."""
    return str(s).strip().lower().replace(" ", "")


def get_expected_columns(source_type: SourceType) -> int:
    """Get the expected number of columns for entity headers based on source type."""
    if source_type == SourceType.BUDGET_LAW:
        return 4
    elif source_type in [
        SourceType.SPENDING_Q1,
        SourceType.SPENDING_Q12,
        SourceType.SPENDING_Q123,
    ]:
        return 10
    elif source_type == SourceType.SPENDING_Q1234:
        return 7
    else:
        raise ValueError(f"Unsupported source type: {source_type}")


def get_column_mappings(source_type: SourceType, prefix: str) -> dict[str, int]:
    """Get column mappings for different source types with prefix."""
    if source_type == SourceType.BUDGET_LAW:
        return {f"{prefix}total": 3}
    elif source_type in [
        SourceType.SPENDING_Q1,
        SourceType.SPENDING_Q12,
        SourceType.SPENDING_Q123,
    ]:
        return {
            f"{prefix}annual_plan": 3,
            f"{prefix}rev_annual_plan": 4,
            f"{prefix}period_plan": 5,
            f"{prefix}rev_period_plan": 6,
            f"{prefix}actual": 7,
            f"{prefix}actual_vs_rev_annual_plan": 8,
            f"{prefix}actual_vs_rev_period_plan": 9,
        }
    elif source_type == SourceType.SPENDING_Q1234:
        return {
            f"{prefix}annual_plan": 3,
            f"{prefix}rev_annual_plan": 4,
            f"{prefix}actual": 5,
            f"{prefix}actual_vs_rev_annual_plan": 6,
        }
    else:
        raise ValueError(f"Unsupported source type: {source_type}")


def sort_columns_by_excel_order(mappings: dict[str, int]) -> list[str]:
    """Sort column names by their original Excel column indices."""
    return [col_name for col_name, _ in sorted(mappings.items(), key=lambda x: x[1])]


__all__ = [
    "ProcessingState",
    "RowType",
    "SourceType",
    "is_numeric",
    "normalize_str",
    "get_expected_columns",
    "get_column_mappings",
    "sort_columns_by_excel_order",
]
