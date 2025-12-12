"""Tests for the PeriodVsAnnualCheck validation.

This module verifies that the `PeriodVsAnnualCheck` correctly identifies
instances where period plans exceed annual plans, for both original and revised
plans, across overall JSON, state body, program, and subprogram levels.
It also ensures the check only applies to relevant spending report types.
"""

import pandas as pd
import pytest
from armenian_budget.core.enums import SourceType
from armenian_budget.validation.checks.period_vs_annual import PeriodVsAnnualCheck


@pytest.fixture
def valid_period_data():
    """DataFrame and overall dict with valid period vs annual data for SPENDING_Q1."""
    data = {
        "state_body": ["Ministry A"],
        "program_code": [100],
        "subprogram_code": [101],
        "state_body_annual_plan": [1000.0],
        "state_body_period_plan": [250.0],
        "state_body_rev_annual_plan": [1100.0],
        "state_body_rev_period_plan": [275.0],
        "program_annual_plan": [1000.0],
        "program_period_plan": [250.0],
        "program_rev_annual_plan": [1100.0],
        "program_rev_period_plan": [275.0],
        "subprogram_annual_plan": [1000.0],
        "subprogram_period_plan": [250.0],
        "subprogram_rev_annual_plan": [1100.0],
        "subprogram_rev_period_plan": [275.0],
    }
    df = pd.DataFrame(data)
    overall = {
        "overall_annual_plan": 1000.0,
        "overall_period_plan": 250.0,
        "overall_rev_annual_plan": 1100.0,
        "overall_rev_period_plan": 275.0,
    }
    return df, overall


def test_period_vs_annual_pass(valid_period_data):  # pylint: disable=redefined-outer-name
    """Test that the check passes with valid data."""
    df, overall = valid_period_data
    check = PeriodVsAnnualCheck()
    results = check.validate(df, overall, SourceType.SPENDING_Q1)

    assert len(results) == 4  # overall, state_body, program, subprogram
    for result in results:
        assert result.check_id == "period_vs_annual"
        assert result.passed is True


def test_period_vs_annual_fail_overall(valid_period_data):  # pylint: disable=redefined-outer-name
    """Test failure when overall period plan > annual plan."""
    df, overall = valid_period_data
    overall["overall_period_plan"] = 1001.0
    check = PeriodVsAnnualCheck()
    results = check.validate(df, overall, SourceType.SPENDING_Q1)

    overall_result = results[0]
    assert overall_result.passed is False
    assert (
        "overall_period_plan (1001.0) exceeds limit overall_annual_plan (1000.0)"
        in overall_result.messages[0]
    )
    assert overall_result.severity == "error"


def test_period_vs_annual_fail_program_revised(valid_period_data):  # pylint: disable=redefined-outer-name
    """Test failure when a revised program period plan > annual plan."""
    df, overall = valid_period_data
    df.loc[0, "program_rev_period_plan"] = 1101.0
    check = PeriodVsAnnualCheck()
    results = check.validate(df, overall, SourceType.SPENDING_Q12)

    program_result = results[2]
    assert program_result.passed is False
    assert program_result.fail_count == 1
    assert (
        "Program violation: 'program_rev_period_plan' (1101.00) exceeds limit "
        "'program_rev_annual_plan' "
        "(1100.00) by 1.00" in program_result.messages[0]
    )
    assert program_result.severity == "error"


def test_period_vs_annual_fail_subprogram_warning(valid_period_data):  # pylint: disable=redefined-outer-name
    """Test that subprogram violation is a warning, not an error."""
    df, overall = valid_period_data
    df.loc[0, "subprogram_period_plan"] = 1001.0
    check = PeriodVsAnnualCheck()
    results = check.validate(df, overall, SourceType.SPENDING_Q1)

    subprogram_result = results[3]  # overall, state_body, program, subprogram
    assert subprogram_result.passed is False
    assert subprogram_result.fail_count == 1
    assert subprogram_result.severity == "warning"
    assert (
        "Subprogram violation: 'subprogram_period_plan' (1001.00) exceeds limit 'subprogram_annual_plan' "
        "(1000.00) by 1.00" in subprogram_result.messages[0]
    )


@pytest.mark.parametrize(
    "period_plan, annual_plan, expect_pass",
    [
        # Rule 1: Annual >= 0
        (200.0, 1000.0, True),  # period <= annual
        (1000.0, 1000.0, True),  # period == annual
        (1001.0, 1000.0, False),  # period > annual
        (0.0, 0.0, True),  # zero case
        # Rule 2: Annual < 0
        (-80.0, -100.0, True),  # period >= annual (less negative)
        (-100.0, -100.0, True),  # period == annual
        (-120.0, -100.0, False),  # period < annual (more negative)
        (0.0, -1276.0, True),  # period > annual (delayed return case, OK)
        # Rule 3: Mixed Signs
        (-10.0, 100.0, False),  # Annual +, Period - (not 0) -> Violation
        (10.0, -100.0, False),  # Annual -, Period + (not 0) -> Violation
        (0.0, 100.0, True),  # Annual +, Period 0 (Ok)
        (0.0, -100.0, True),  # Annual -, Period 0 (Ok)
        (-10.0, 0.0, False),  # Annual 0, Period - (strict zero enforcement)
    ],
    ids=[
        "pos_less",
        "pos_equal",
        "pos_greater",
        "pos_zero",
        "neg_less_neg",
        "neg_equal",
        "neg_more_neg",
        "neg_zero_period",
        "mixed_ann_pos_per_neg",
        "mixed_ann_neg_per_pos",
        "mixed_ann_pos_per_zero",
        "mixed_ann_neg_per_zero",
        "zero_annual_neg_period",
    ],
)
def test_period_vs_annual_boundaries(valid_period_data, period_plan, annual_plan, expect_pass):  # pylint: disable=redefined-outer-name
    """Test boundary conditions for the period vs annual check with new logic."""
    df, overall = valid_period_data
    # Modify the program level for testing
    df.loc[0, "program_period_plan"] = period_plan
    df.loc[0, "program_annual_plan"] = annual_plan

    check = PeriodVsAnnualCheck()
    results = check.validate(df, overall, SourceType.SPENDING_Q1)

    # The check is at index 2 (overall, state_body, program)
    program_result = results[2]
    assert program_result.passed is expect_pass
    if expect_pass:
        assert program_result.fail_count == 0
    else:
        assert program_result.fail_count == 1


def test_period_vs_annual_handles_missing_columns(valid_period_data):  # pylint: disable=redefined-outer-name
    """Test that the check doesn't crash and passes if a required column is missing."""
    df, overall = valid_period_data
    # Remove a column the check depends on
    del df["program_period_plan"]

    check = PeriodVsAnnualCheck()
    results = check.validate(df, overall, SourceType.SPENDING_Q1)

    # The program check (index 2) should still pass because it skips the logic
    # when a column is missing.
    program_result = results[2]
    assert program_result.passed is True
    assert program_result.fail_count == 0


def test_applies_to_source_type():
    """Test which source types the check applies to."""
    check = PeriodVsAnnualCheck()
    assert check.applies_to_source_type(SourceType.SPENDING_Q1) is True
    assert check.applies_to_source_type(SourceType.SPENDING_Q12) is True
    assert check.applies_to_source_type(SourceType.SPENDING_Q123) is True

    assert check.applies_to_source_type(SourceType.SPENDING_Q1234) is False
    assert check.applies_to_source_type(SourceType.BUDGET_LAW) is False
    assert check.applies_to_source_type(SourceType.MTEP) is False
