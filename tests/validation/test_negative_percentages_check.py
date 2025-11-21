"""Tests for the NegativePercentagesCheck validation.

This module verifies that the `NegativePercentagesCheck` correctly identifies
negative percentage values across overall JSON, state body, program,
and subprogram levels, and ensures the check only applies to spending reports.
"""

import pandas as pd
import pytest
from armenian_budget.core.enums import SourceType
from armenian_budget.validation.checks.negative_percentages import NegativePercentagesCheck


@pytest.fixture
def valid_percentage_data():
    """DataFrame and overall dict with valid percentage data for SPENDING_Q1."""
    data = {
        "state_body": ["Ministry A"],
        "program_code": [100],
        "subprogram_code": [101],
        "state_body_actual_vs_rev_annual_plan": [0.95],
        "state_body_actual_vs_rev_period_plan": [0.24],
        "program_actual_vs_rev_annual_plan": [0.95],
        "program_actual_vs_rev_period_plan": [0.24],
        "subprogram_actual_vs_rev_annual_plan": [0.95],
        "subprogram_actual_vs_rev_period_plan": [0.24],
    }
    df = pd.DataFrame(data)
    overall = {
        "overall_actual_vs_rev_annual_plan": 0.95,
        "overall_actual_vs_rev_period_plan": 0.24,
    }
    return df, overall


def test_negative_percentages_pass(valid_percentage_data):  # pylint: disable=redefined-outer-name
    """Test that the check passes with non-negative percentages."""
    df, overall = valid_percentage_data
    check = NegativePercentagesCheck()
    results = check.validate(df, overall, SourceType.SPENDING_Q1)

    assert len(results) == 4  # overall, state_body, program, subprogram
    for result in results:
        assert result.check_id == "negative_percentages"
        assert result.passed is True


@pytest.mark.parametrize(
    "value_to_test, expect_pass",
    [
        (0.95, True),
        (0.0, True),
        (-0.01, False),
    ],
    ids=["positive", "zero", "negative"],
)
def test_negative_percentages_edge_cases(valid_percentage_data, value_to_test, expect_pass):  # pylint: disable=redefined-outer-name
    """Test the negative percentages check with positive, zero, and negative values."""
    df, overall = valid_percentage_data
    # Modify a program-level percentage to test different values
    df.loc[0, "program_actual_vs_rev_annual_plan"] = value_to_test

    check = NegativePercentagesCheck()
    results = check.validate(df, overall, SourceType.SPENDING_Q1)

    # Find the result for the 'program' level check
    program_result = results[2]  # overall, state_body, program

    assert program_result.passed is expect_pass
    if expect_pass:
        assert program_result.fail_count == 0
    else:
        assert program_result.fail_count == 1
        assert (
            f"Negative percentage for 'program_actual_vs_rev_annual_plan' ({value_to_test:.2%})"
            in program_result.messages[0]
        )


def test_negative_percentages_fail_overall(valid_percentage_data):  # pylint: disable=redefined-outer-name
    """Test failure when an overall percentage is negative."""
    df, overall = valid_percentage_data
    overall["overall_actual_vs_rev_annual_plan"] = -0.05
    check = NegativePercentagesCheck()
    results = check.validate(df, overall, SourceType.SPENDING_Q1)

    overall_result = results[0]
    assert overall_result.passed is False
    assert (
        "Negative overall percentages: overall_actual_vs_rev_annual_plan"
        in overall_result.messages[0]
    )


def test_negative_percentages_fail_program(valid_percentage_data):  # pylint: disable=redefined-outer-name
    """Test failure when a program-level percentage is negative."""
    df, overall = valid_percentage_data
    df.loc[0, "program_actual_vs_rev_period_plan"] = -0.01
    check = NegativePercentagesCheck()
    results = check.validate(df, overall, SourceType.SPENDING_Q123)

    program_result = results[2]
    assert program_result.passed is False
    assert program_result.fail_count == 1
    assert (
        "Row 0: Negative percentage for 'program_actual_vs_rev_period_plan' (-1.00%)"
        in program_result.messages[0]
    )


def test_applies_to_source_type():
    """Test which source types the check applies to."""
    check = NegativePercentagesCheck()
    assert check.applies_to_source_type(SourceType.SPENDING_Q1) is True
    assert check.applies_to_source_type(SourceType.SPENDING_Q12) is True
    assert check.applies_to_source_type(SourceType.SPENDING_Q123) is True
    assert check.applies_to_source_type(SourceType.SPENDING_Q1234) is True

    assert check.applies_to_source_type(SourceType.BUDGET_LAW) is False
    assert check.applies_to_source_type(SourceType.MTEP) is False
