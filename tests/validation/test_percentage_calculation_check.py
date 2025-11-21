"""Tests for the PercentageCalculationCheck validation.

This module verifies that the `PercentageCalculationCheck` correctly identifies
mismatches between reported and calculated percentage values across overall JSON,
state body, program, and subprogram levels. It also handles division by zero scenarios
and ensures the check only applies to spending reports.
"""

import pandas as pd
import pytest
import numpy as np
from armenian_budget.core.enums import SourceType
from armenian_budget.validation.checks.percentage_calculation import PercentageCalculationCheck


@pytest.fixture
def valid_percentage_calc_data():
    """DataFrame and overall dict with valid percentage calculation data for SPENDING_Q1."""
    data = {
        "state_body": ["Ministry A"],
        "program_code": [100],
        "subprogram_code": [101],
        # Annual
        "state_body_actual": [95.0],
        "state_body_rev_annual_plan": [100.0],
        "state_body_actual_vs_rev_annual_plan": [0.95],
        "program_actual": [95.0],
        "program_rev_annual_plan": [100.0],
        "program_actual_vs_rev_annual_plan": [0.95],
        "subprogram_actual": [95.0],
        "subprogram_rev_annual_plan": [100.0],
        "subprogram_actual_vs_rev_annual_plan": [0.95],
        # Period
        "state_body_rev_period_plan": [25.0],
        "state_body_actual_vs_rev_period_plan": [3.8],  # 95 / 25 = 3.8
        "program_rev_period_plan": [25.0],
        "program_actual_vs_rev_period_plan": [3.8],
        "subprogram_rev_period_plan": [25.0],
        "subprogram_actual_vs_rev_period_plan": [3.8],
    }
    df = pd.DataFrame(data)
    overall = {
        "overall_actual": 95.0,
        "overall_rev_annual_plan": 100.0,
        "overall_actual_vs_rev_annual_plan": 0.95,
        "overall_rev_period_plan": 25.0,
        "overall_actual_vs_rev_period_plan": 3.8,
    }
    return df, overall


def test_percentage_calculation_pass(valid_percentage_calc_data):  # pylint: disable=redefined-outer-name
    """Test that the check passes with correct calculations."""
    df, overall = valid_percentage_calc_data
    check = PercentageCalculationCheck()
    results = check.validate(df, overall, SourceType.SPENDING_Q1)

    for result in results:
        assert result.check_id == "percentage_calculation"
        assert result.passed is True, f"Check failed unexpectedly: {result.messages}"


def test_percentage_calculation_fail_overall(valid_percentage_calc_data):  # pylint: disable=redefined-outer-name
    """Test failure when an overall percentage calculation is incorrect."""
    df, overall = valid_percentage_calc_data
    overall["overall_actual_vs_rev_annual_plan"] = 0.94  # Should be 0.95
    check = PercentageCalculationCheck()
    results = check.validate(df, overall, SourceType.SPENDING_Q1)

    fail_result = results[0]  # First result is overall annual
    assert fail_result.passed is False
    assert (
        "Overall actual_vs_rev_annual_plan: expected 0.9500, reported 0.9400"
        in fail_result.messages[0]
    )


def test_percentage_calculation_fail_program(valid_percentage_calc_data):  # pylint: disable=redefined-outer-name
    """Test failure when a program-level percentage calculation is incorrect."""
    df, overall = valid_percentage_calc_data
    df.loc[0, "program_actual_vs_rev_period_plan"] = 3.7  # Should be 3.8
    check = PercentageCalculationCheck()
    results = check.validate(df, overall, SourceType.SPENDING_Q1)

    # program period check is the 7th result (0-indexed)
    fail_result = results[6]

    assert fail_result is not None
    assert fail_result.passed is False
    assert (
        "Row 0: Mismatch for 'program_actual_vs_rev_period_plan'. Expected: 3.8000, Reported: 3.7000"
        in fail_result.messages[0]
    )


@pytest.mark.parametrize(
    "diff, expect_pass",
    [
        (0.001, True),  # On tolerance boundary
        (0.0009, True),  # Inside tolerance
        (0.0011, False),  # Outside tolerance
    ],
    ids=["on_boundary", "inside_boundary", "outside_boundary"],
)
def test_percentage_calculation_tolerance_boundaries(valid_percentage_calc_data, diff, expect_pass):  # pylint: disable=redefined-outer-name
    """Test the tolerance boundaries for percentage calculations."""
    df, overall = valid_percentage_calc_data
    # Modify the reported percentage to test the tolerance
    df.loc[0, "program_actual_vs_rev_annual_plan"] += diff
    check = PercentageCalculationCheck()
    results = check.validate(df, overall, SourceType.SPENDING_Q1)

    # Get the program level result for the annual plan percentage (3rd result)
    program_result = results[2]

    assert program_result.passed is expect_pass
    if not expect_pass:
        assert "program_actual_vs_rev_annual_plan" in program_result.messages[0]


@pytest.mark.parametrize(
    "denominator",
    [0, None, np.nan],
    ids=["zero", "none", "nan"],
)
def test_percentage_calculation_division_by_zero(valid_percentage_calc_data, denominator):  # pylint: disable=redefined-outer-name
    """Test that division by zero is handled gracefully."""
    df, overall = valid_percentage_calc_data
    df.loc[0, "program_rev_annual_plan"] = denominator
    check = PercentageCalculationCheck()
    results = check.validate(df, overall, SourceType.SPENDING_Q1)

    # We expect the check to pass because it should skip the calculation
    # when the denominator is zero/null, not crash.
    all_passed = all(r.passed for r in results)
    assert all_passed, "The check should not fail when the denominator is zero or null."


def test_percentage_calculation_pass_zero_denominator(valid_percentage_calc_data):  # pylint: disable=redefined-outer-name
    """Test that the check passes when the denominator is zero."""
    df, overall = valid_percentage_calc_data
    df.loc[0, "subprogram_rev_annual_plan"] = 0
    # Expected percentage is undefined, but reported is often 0 in this case
    df.loc[0, "subprogram_actual_vs_rev_annual_plan"] = 0
    check = PercentageCalculationCheck()
    results = check.validate(df, overall, SourceType.SPENDING_Q1)

    # The check should pass because division by zero is skipped
    subprogram_annual_result = results[3]  # 4th result is subprogram annual
    assert subprogram_annual_result.passed is True, (
        f"Check failed with zero denominator: {subprogram_annual_result.messages}"
    )


def test_applies_to_source_type():
    """Test which source types the check applies to."""
    check = PercentageCalculationCheck()
    assert check.applies_to_source_type(SourceType.SPENDING_Q1) is True
    assert check.applies_to_source_type(SourceType.SPENDING_Q12) is True
    assert check.applies_to_source_type(SourceType.BUDGET_LAW) is False
