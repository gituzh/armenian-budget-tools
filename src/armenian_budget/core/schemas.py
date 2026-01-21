"""Data schemas and field definitions for Armenian Budget data.

This module defines the expected fields for each source type (CSV and JSON).
Used by parsers, validation, and other modules to ensure consistency.
"""

from __future__ import annotations

from typing import List, Tuple

from .enums import SourceType


def get_required_fields(source_type: SourceType) -> Tuple[List[str], List[str]]:
    """Get required CSV and JSON fields for a source type.

    Args:
        source_type: Type of data source.

    Returns:
        Tuple of (required_csv_fields, required_json_fields).

    Examples:
        >>> csv, json = get_required_fields(SourceType.BUDGET_LAW)
        >>> "state_body" in csv
        True
        >>> "overall_total" in json
        True
    """
    # Common identifier fields (all sources)
    common_csv = [
        "state_body",
        "program_code",
        "program_name",
    ]

    if source_type == SourceType.BUDGET_LAW:
        csv_fields = common_csv + [
            "program_goal",
            "program_result_desc",
            "subprogram_code",
            "subprogram_name",
            "subprogram_desc",
            "subprogram_type",
            "state_body_total",
            "program_total",
            "subprogram_total",
        ]
        json_fields = ["overall_total"]

    elif source_type == SourceType.MTEP:
        csv_fields = common_csv + [
            "state_body_total_y0",
            "state_body_total_y1",
            "state_body_total_y2",
            "program_total_y0",
            "program_total_y1",
            "program_total_y2",
        ]
        json_fields = [
            "overall_total_y0",
            "overall_total_y1",
            "overall_total_y2",
            "plan_years",
        ]

    elif source_type in (
        SourceType.SPENDING_Q1,
        SourceType.SPENDING_Q12,
        SourceType.SPENDING_Q123,
    ):
        # Q1/Q12/Q123 have period fields
        csv_fields = common_csv + [
            "program_goal",
            "program_result_desc",
            "subprogram_code",
            "subprogram_name",
            "subprogram_desc",
            "subprogram_type",
            "state_body_annual_plan",
            "state_body_rev_annual_plan",
            "state_body_period_plan",
            "state_body_rev_period_plan",
            "state_body_actual",
            "state_body_actual_vs_rev_annual_plan",
            "state_body_actual_vs_rev_period_plan",
            "program_annual_plan",
            "program_rev_annual_plan",
            "program_period_plan",
            "program_rev_period_plan",
            "program_actual",
            "program_actual_vs_rev_annual_plan",
            "program_actual_vs_rev_period_plan",
            "subprogram_annual_plan",
            "subprogram_rev_annual_plan",
            "subprogram_period_plan",
            "subprogram_rev_period_plan",
            "subprogram_actual",
            "subprogram_actual_vs_rev_annual_plan",
            "subprogram_actual_vs_rev_period_plan",
        ]
        json_fields = [
            "overall_annual_plan",
            "overall_rev_annual_plan",
            "overall_period_plan",
            "overall_rev_period_plan",
            "overall_actual",
            "overall_actual_vs_rev_annual_plan",
            "overall_actual_vs_rev_period_plan",
        ]

    else:  # SPENDING_Q1234
        # Q1234 has no period fields
        csv_fields = common_csv + [
            "program_goal",
            "program_result_desc",
            "subprogram_code",
            "subprogram_name",
            "subprogram_desc",
            "subprogram_type",
            "state_body_annual_plan",
            "state_body_rev_annual_plan",
            "state_body_actual",
            "state_body_actual_vs_rev_annual_plan",
            "program_annual_plan",
            "program_rev_annual_plan",
            "program_actual",
            "program_actual_vs_rev_annual_plan",
            "subprogram_annual_plan",
            "subprogram_rev_annual_plan",
            "subprogram_actual",
            "subprogram_actual_vs_rev_annual_plan",
        ]
        json_fields = [
            "overall_annual_plan",
            "overall_rev_annual_plan",
            "overall_actual",
            "overall_actual_vs_rev_annual_plan",
        ]

    return csv_fields, json_fields


def get_financial_fields(source_type: SourceType) -> Tuple[List[str], List[str]]:
    """Get financial (numeric) fields for a source type.

    Returns fields that should not be null/NaN (amounts and percentages).
    Excludes identifier fields (state_body, program_name, etc.).

    Args:
        source_type: Type of data source.

    Returns:
        Tuple of (csv_financial_fields, json_financial_fields).

    Examples:
        >>> csv, json = get_financial_fields(SourceType.BUDGET_LAW)
        >>> "state_body_total" in csv
        True
        >>> "overall_total" in json
        True
    """
    if source_type == SourceType.BUDGET_LAW:
        csv_fields = [
            "state_body_total",
            "program_total",
            "subprogram_total",
        ]
        json_fields = ["overall_total"]

    elif source_type == SourceType.MTEP:
        csv_fields = [
            "state_body_total_y0",
            "state_body_total_y1",
            "state_body_total_y2",
            "program_total_y0",
            "program_total_y1",
            "program_total_y2",
        ]
        json_fields = [
            "overall_total_y0",
            "overall_total_y1",
            "overall_total_y2",
        ]

    elif source_type in (
        SourceType.SPENDING_Q1,
        SourceType.SPENDING_Q12,
        SourceType.SPENDING_Q123,
    ):
        # Q1/Q12/Q123 have period fields
        csv_fields = [
            "state_body_annual_plan",
            "state_body_rev_annual_plan",
            "state_body_period_plan",
            "state_body_rev_period_plan",
            "state_body_actual",
            "state_body_actual_vs_rev_annual_plan",
            "state_body_actual_vs_rev_period_plan",
            "program_annual_plan",
            "program_rev_annual_plan",
            "program_period_plan",
            "program_rev_period_plan",
            "program_actual",
            "program_actual_vs_rev_annual_plan",
            "program_actual_vs_rev_period_plan",
            "subprogram_annual_plan",
            "subprogram_rev_annual_plan",
            "subprogram_period_plan",
            "subprogram_rev_period_plan",
            "subprogram_actual",
            "subprogram_actual_vs_rev_annual_plan",
            "subprogram_actual_vs_rev_period_plan",
        ]
        json_fields = [
            "overall_annual_plan",
            "overall_rev_annual_plan",
            "overall_period_plan",
            "overall_rev_period_plan",
            "overall_actual",
            "overall_actual_vs_rev_annual_plan",
            "overall_actual_vs_rev_period_plan",
        ]

    else:  # SPENDING_Q1234
        # Q1234 has no period fields
        csv_fields = [
            "state_body_annual_plan",
            "state_body_rev_annual_plan",
            "state_body_actual",
            "state_body_actual_vs_rev_annual_plan",
            "program_annual_plan",
            "program_rev_annual_plan",
            "program_actual",
            "program_actual_vs_rev_annual_plan",
            "subprogram_annual_plan",
            "subprogram_rev_annual_plan",
            "subprogram_actual",
            "subprogram_actual_vs_rev_annual_plan",
        ]
        json_fields = [
            "overall_annual_plan",
            "overall_rev_annual_plan",
            "overall_actual",
            "overall_actual_vs_rev_annual_plan",
        ]

    return csv_fields, json_fields


def get_amount_fields(source_type: SourceType) -> Tuple[List[str], List[str]]:
    """Get amount (non-percentage) fields for hierarchical and negative checks.

    Returns only amount fields, excludes percentage fields like *_actual_vs_rev_annual_plan.
    Used for hierarchical totals and negative totals validation.

    Args:
        source_type: Type of data source.

    Returns:
        Tuple of (csv_amount_fields, json_amount_fields).

    Examples:
        >>> csv, json = get_amount_fields(SourceType.BUDGET_LAW)
        >>> "state_body_total" in csv
        True
        >>> "state_body_actual_vs_rev_annual_plan" in csv
        False
    """
    if source_type == SourceType.BUDGET_LAW:
        csv_fields = [
            "state_body_total",
            "program_total",
            "subprogram_total",
        ]
        json_fields = ["overall_total"]

    elif source_type == SourceType.MTEP:
        csv_fields = [
            "state_body_total_y0",
            "state_body_total_y1",
            "state_body_total_y2",
            "program_total_y0",
            "program_total_y1",
            "program_total_y2",
        ]
        json_fields = [
            "overall_total_y0",
            "overall_total_y1",
            "overall_total_y2",
        ]

    elif source_type in (
        SourceType.SPENDING_Q1,
        SourceType.SPENDING_Q12,
        SourceType.SPENDING_Q123,
    ):
        # Q1/Q12/Q123 have period fields (amounts only, not percentages)
        csv_fields = [
            "state_body_annual_plan",
            "state_body_rev_annual_plan",
            "state_body_period_plan",
            "state_body_rev_period_plan",
            "state_body_actual",
            "program_annual_plan",
            "program_rev_annual_plan",
            "program_period_plan",
            "program_rev_period_plan",
            "program_actual",
            "subprogram_annual_plan",
            "subprogram_rev_annual_plan",
            "subprogram_period_plan",
            "subprogram_rev_period_plan",
            "subprogram_actual",
        ]
        json_fields = [
            "overall_annual_plan",
            "overall_rev_annual_plan",
            "overall_period_plan",
            "overall_rev_period_plan",
            "overall_actual",
        ]

    else:  # SPENDING_Q1234
        # Q1234 has no period fields (amounts only, not percentages)
        csv_fields = [
            "state_body_annual_plan",
            "state_body_rev_annual_plan",
            "state_body_actual",
            "program_annual_plan",
            "program_rev_annual_plan",
            "program_actual",
            "subprogram_annual_plan",
            "subprogram_rev_annual_plan",
            "subprogram_actual",
        ]
        json_fields = [
            "overall_annual_plan",
            "overall_rev_annual_plan",
            "overall_actual",
        ]

    return csv_fields, json_fields


def get_percentage_fields(source_type: SourceType) -> Tuple[List[str], List[str]]:
    """Get percentage fields for spending reports.

    Returns only percentage fields like *_actual_vs_rev_annual_plan.
    Used for negative percentages, execution >100%, and percentage calculation checks.

    Args:
        source_type: Type of data source.

    Returns:
        Tuple of (csv_percentage_fields, json_percentage_fields).
        Returns empty lists for BUDGET_LAW and MTEP (no percentages).

    Examples:
        >>> csv, json = get_percentage_fields(SourceType.SPENDING_Q1)
        >>> "state_body_actual_vs_rev_annual_plan" in csv
        True
        >>> "state_body_actual" in csv
        False
    """
    if source_type in (SourceType.BUDGET_LAW, SourceType.MTEP):
        # Budget Law and MTEP have no percentage fields
        return [], []

    elif source_type in (
        SourceType.SPENDING_Q1,
        SourceType.SPENDING_Q12,
        SourceType.SPENDING_Q123,
    ):
        # Q1/Q12/Q123 have two percentage fields per level
        csv_fields = [
            "state_body_actual_vs_rev_annual_plan",
            "state_body_actual_vs_rev_period_plan",
            "program_actual_vs_rev_annual_plan",
            "program_actual_vs_rev_period_plan",
            "subprogram_actual_vs_rev_annual_plan",
            "subprogram_actual_vs_rev_period_plan",
        ]
        json_fields = [
            "overall_actual_vs_rev_annual_plan",
            "overall_actual_vs_rev_period_plan",
        ]

    else:  # SPENDING_Q1234
        # Q1234 has one percentage field per level
        csv_fields = [
            "state_body_actual_vs_rev_annual_plan",
            "program_actual_vs_rev_annual_plan",
            "subprogram_actual_vs_rev_annual_plan",
        ]
        json_fields = [
            "overall_actual_vs_rev_annual_plan",
        ]

    return csv_fields, json_fields
