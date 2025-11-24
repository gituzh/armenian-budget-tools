"""Tests for the NegativeTotalsCheck validation.

This module verifies that the `NegativeTotalsCheck` correctly identifies
negative values in amount fields across overall JSON, state body, program,
and subprogram levels for various source types.
"""

import pandas as pd
import pytest
from armenian_budget.core.enums import SourceType
from armenian_budget.validation.checks.negative_totals import NegativeTotalsCheck


@pytest.fixture
def non_negative_data():
    """DataFrame and overall dict with non-negative data for BUDGET_LAW."""
    data = {
        "state_body": ["Ministry A"],
        "program_code": [100],
        "subprogram_code": [101],
        "state_body_total": [1000.0],
        "program_total": [1000.0],
        "subprogram_total": [1000.0],
    }
    df = pd.DataFrame(data)
    overall = {"overall_total": 1000.0}
    return df, overall


def test_negative_totals_pass(non_negative_data):  # pylint: disable=redefined-outer-name
    """Test that the check passes with non-negative data."""
    df, overall = non_negative_data
    check = NegativeTotalsCheck()
    results = check.validate(df, overall, SourceType.BUDGET_LAW)

    assert len(results) == 4  # overall, state_body, program, subprogram
    for result in results:
        assert result.check_id == "negative_totals"
        assert result.passed is True
        assert result.fail_count == 0


@pytest.mark.parametrize(
    "value_to_test, expect_pass",
    [
        (100.0, True),
        (0.0, True),
        (-0.01, False),
        (-100.0, False),
    ],
    ids=["positive", "zero", "small_negative", "large_negative"],
)
def test_negative_totals_edge_cases(non_negative_data, value_to_test, expect_pass):  # pylint: disable=redefined-outer-name
    """Test the negative totals check with various edge case values."""
    df, overall = non_negative_data
    # Modify a program_total to test different values
    df.loc[0, "program_total"] = value_to_test

    check = NegativeTotalsCheck()
    results = check.validate(df, overall, SourceType.BUDGET_LAW)

    # Find the result for the 'program' level check
    program_result = results[2]

    assert program_result.passed is expect_pass
    if expect_pass:
        assert program_result.fail_count == 0
    else:
        assert program_result.fail_count == 1
        assert f"has negative value: {value_to_test:.2f}" in program_result.messages[0]


def test_negative_totals_fail_overall(non_negative_data):  # pylint: disable=redefined-outer-name
    """Test failure when an overall (JSON) field is negative."""
    df, _ = non_negative_data
    overall = {"overall_total": -100.0}
    check = NegativeTotalsCheck()
    results = check.validate(df, overall, SourceType.BUDGET_LAW)

    overall_result = results[0]
    assert overall_result.passed is False
    assert overall_result.fail_count == 1
    assert "Overall field 'overall_total' has negative value: -100.00" in overall_result.messages


def test_negative_totals_fail_state_body(non_negative_data):  # pylint: disable=redefined-outer-name
    """Test failure when a state_body level field is negative."""
    df, overall = non_negative_data
    df.loc[0, "state_body_total"] = -50.0
    check = NegativeTotalsCheck()
    results = check.validate(df, overall, SourceType.BUDGET_LAW)

    sb_result = results[1]
    assert sb_result.passed is False
    assert sb_result.fail_count == 1
    assert "State_body field 'state_body_total' has negative value: -50.00" in sb_result.messages[0]


def test_negative_totals_fail_program(non_negative_data):  # pylint: disable=redefined-outer-name
    """Test failure when a program level field is negative."""
    df, overall = non_negative_data
    df.loc[0, "program_total"] = -50.0
    check = NegativeTotalsCheck()
    results = check.validate(df, overall, SourceType.BUDGET_LAW)

    prog_result = results[2]
    assert prog_result.passed is False
    assert prog_result.fail_count == 1
    assert "Program field 'program_total' has negative value: -50.00" in prog_result.messages[0]


def test_negative_totals_fail_subprogram(non_negative_data):  # pylint: disable=redefined-outer-name
    """Test failure when a subprogram level field is negative."""
    df, overall = non_negative_data
    df.loc[0, "subprogram_total"] = -50.0
    check = NegativeTotalsCheck()
    results = check.validate(df, overall, SourceType.BUDGET_LAW)

    subprog_result = results[3]
    assert subprog_result.passed is False
    assert subprog_result.fail_count == 1
    assert (
        "Subprogram field 'subprogram_total' has negative value: -50.00"
        in subprog_result.messages[0]
    )


def test_applies_to_all_source_types():
    """Test that the check applies to all source types."""
    check = NegativeTotalsCheck()
    for source_type in SourceType:
        assert check.applies_to_source_type(source_type) is True
