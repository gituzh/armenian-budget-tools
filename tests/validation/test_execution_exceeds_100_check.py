"""Tests for the ExecutionExceeds100Check validation.

This module verifies that the `ExecutionExceeds100Check` correctly identifies
execution rates exceeding 100% across overall JSON, state body, program,
and subprogram levels, and ensures the check only applies to spending reports.
"""

import pandas as pd
import pytest
from armenian_budget.core.enums import SourceType
from armenian_budget.validation.checks.execution_exceeds_100 import ExecutionExceeds100Check


@pytest.fixture
def valid_execution_data():
    """DataFrame and overall dict with valid execution data for SPENDING_Q1234."""
    data = {
        "state_body": ["Ministry A"],
        "program_code": [100],
        "subprogram_code": [101],
        "state_body_actual_vs_rev_annual_plan": [0.99],
        "program_actual_vs_rev_annual_plan": [1.0],
        "subprogram_actual_vs_rev_annual_plan": [0.5],
    }
    df = pd.DataFrame(data)
    overall = {"overall_actual_vs_rev_annual_plan": 0.98}
    return df, overall


def test_execution_exceeds_100_pass(valid_execution_data):  # pylint: disable=redefined-outer-name
    """Test that the check passes with valid execution rates."""
    df, overall = valid_execution_data
    check = ExecutionExceeds100Check()
    results = check.validate(df, overall, SourceType.SPENDING_Q1234)

    assert len(results) == 4  # overall, state_body, program, subprogram
    for result in results:
        assert result.check_id == "execution_exceeds_100"
        assert result.passed is True


def test_execution_exceeds_100_fail_overall(valid_execution_data):  # pylint: disable=redefined-outer-name
    """Test failure when overall execution > 100%."""
    df, overall = valid_execution_data
    overall["overall_actual_vs_rev_annual_plan"] = 1.01
    check = ExecutionExceeds100Check()
    results = check.validate(df, overall, SourceType.SPENDING_Q1234)

    overall_result = results[0]
    assert overall_result.passed is False
    assert (
        "Overall execution > 100%: overall_actual_vs_rev_annual_plan" in overall_result.messages[0]
    )


def test_execution_exceeds_100_fail_subprogram(valid_execution_data):  # pylint: disable=redefined-outer-name
    """Test failure when a subprogram execution > 100%."""
    df, overall = valid_execution_data
    df.loc[0, "subprogram_actual_vs_rev_annual_plan"] = 1.25
    check = ExecutionExceeds100Check()
    results = check.validate(df, overall, SourceType.SPENDING_Q1234)

    subprogram_result = results[3]
    assert subprogram_result.passed is False
    assert subprogram_result.fail_count == 1
    assert (
        "Row 0: Execution > 100% for 'subprogram_actual_vs_rev_annual_plan' (125.00%)"
        in subprogram_result.messages[0]
    )


def test_applies_to_source_type():
    """Test which source types the check applies to."""
    check = ExecutionExceeds100Check()
    assert check.applies_to_source_type(SourceType.SPENDING_Q1) is True
    assert check.applies_to_source_type(SourceType.SPENDING_Q12) is True
    assert check.applies_to_source_type(SourceType.SPENDING_Q123) is True
    assert check.applies_to_source_type(SourceType.SPENDING_Q1234) is True

    assert check.applies_to_source_type(SourceType.BUDGET_LAW) is False
    assert check.applies_to_source_type(SourceType.MTEP) is False
