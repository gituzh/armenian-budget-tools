"""Validation configuration constants.

This module centralizes all validation tolerances and severity rules.
Adjust these constants to tune validation behavior based on real data patterns.

Severity Levels:
    - "error": Critical issues that indicate data corruption or structural problems
    - "warning": Issues that warrant review but may be legitimate edge cases

Hierarchy Levels:
    - "overall": Grand total from overall.json
    - "state_body": State body/ministry level
    - "program": Program level
    - "subprogram": Subprogram level
"""

from __future__ import annotations

from armenian_budget.core.enums import SourceType

# ============================================================================
# TOLERANCE CONSTANTS
# ============================================================================

# Hierarchical totals tolerance by source type (in AMD)
BUDGET_LAW_ABS_TOL = 1.0  # Small rounding tolerance for floating-point precision
SPENDING_ABS_TOL = 5.0    # Small rounding differences acceptable
MTEP_ABS_TOL = 0.5        # Per-year tolerance for multi-year projections

# Percentage calculation tolerance (0.1% = 0.001)
PERCENTAGE_TOL = 0.001


# ============================================================================
# SEVERITY RULES
# ============================================================================
# Format: {check_id: {hierarchy_level: severity}}
# Hierarchy levels: "overall", "state_body", "program", "subprogram"

# Empty identifiers - different by source type
# Budget Law & Spending: Error for state_body/program, Warning for subprogram
# MTEP: Error for state_body/program (no subprograms)
EMPTY_IDENTIFIERS_SEVERITY = {
    "state_body": "error",
    "program": "error",
    "subprogram": "warning",
}

# Missing financial data - Error at top levels, Warning at subprogram
MISSING_FINANCIAL_DATA_SEVERITY = {
    "overall": "error",
    "state_body": "error",
    "program": "error",
    "subprogram": "warning",
}

# Hierarchical totals - Always error (data integrity critical)
HIERARCHICAL_TOTALS_SEVERITY = {
    "overall": "error",
    "state_body": "error",
    "program": "error",
    "subprogram": "error",
}

# Negative totals - Warning at all levels (may be legitimate corrections/adjustments)
NEGATIVE_TOTALS_SEVERITY = {
    "overall": "warning",
    "state_body": "warning",
    "program": "warning",
    "subprogram": "warning",
}

# Period ≤ Annual Plan - Always error (data entry mistakes)
PERIOD_VS_ANNUAL_SEVERITY = {
    "overall": "error",
    "state_body": "error",
    "program": "error",
    "subprogram": "error",
}

# Negative percentages - Error at overall/state_body, Warning at program/subprogram
NEGATIVE_PERCENTAGES_SEVERITY = {
    "overall": "error",
    "state_body": "error",
    "program": "warning",
    "subprogram": "warning",
}

# Execution exceeds 100% - Warning at all levels (may be legitimate with revisions)
EXECUTION_EXCEEDS_100_SEVERITY = {
    "overall": "warning",
    "state_body": "warning",
    "program": "warning",
    "subprogram": "warning",
}

# Percentage calculation correctness - Error at all levels
PERCENTAGE_CALCULATION_SEVERITY = {
    "overall": "error",
    "state_body": "error",
    "program": "error",
    "subprogram": "error",
}


# ============================================================================
# SEVERITY MAP (for get_severity helper)
# ============================================================================

_SEVERITY_MAP = {
    "empty_identifiers": EMPTY_IDENTIFIERS_SEVERITY,
    "missing_financial_data": MISSING_FINANCIAL_DATA_SEVERITY,
    "hierarchical_totals": HIERARCHICAL_TOTALS_SEVERITY,
    "negative_totals": NEGATIVE_TOTALS_SEVERITY,
    "period_vs_annual": PERIOD_VS_ANNUAL_SEVERITY,
    "negative_percentages": NEGATIVE_PERCENTAGES_SEVERITY,
    "execution_exceeds_100": EXECUTION_EXCEEDS_100_SEVERITY,
    "percentage_calculation": PERCENTAGE_CALCULATION_SEVERITY,
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_tolerance_for_source(source_type: SourceType) -> float:
    """Get hierarchical totals tolerance for a source type.

    Args:
        source_type: The type of data source being validated.

    Returns:
        Tolerance value in AMD.

    Examples:
        >>> get_tolerance_for_source(SourceType.BUDGET_LAW)
        0.0
        >>> get_tolerance_for_source(SourceType.SPENDING_Q1)
        5.0
    """
    if source_type == SourceType.BUDGET_LAW:
        return BUDGET_LAW_ABS_TOL
    elif source_type == SourceType.MTEP:
        return MTEP_ABS_TOL
    else:
        # All spending reports use same tolerance
        return SPENDING_ABS_TOL


def get_severity(check_id: str, hierarchy_level: str) -> str:
    """Get severity level for a specific check and hierarchy level.

    Args:
        check_id: Validation check identifier (e.g., "negative_totals").
        hierarchy_level: Hierarchy level ("overall", "state_body", "program", "subprogram").

    Returns:
        Severity level: "error" or "warning".

    Raises:
        ValueError: If check_id is unknown or hierarchy_level is invalid.

    Examples:
        >>> get_severity("negative_totals", "state_body")
        'error'
        >>> get_severity("negative_totals", "subprogram")
        'warning'
    """
    if check_id not in _SEVERITY_MAP:
        raise ValueError(f"Unknown check_id: {check_id}")

    severity_config = _SEVERITY_MAP[check_id]

    if hierarchy_level not in severity_config:
        raise ValueError(
            f"Invalid hierarchy_level '{hierarchy_level}' for check '{check_id}'. "
            f"Valid levels: {severity_config.keys()}"
        )

    return severity_config[hierarchy_level]
