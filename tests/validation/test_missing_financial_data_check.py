"""Tests for the MissingFinancialDataCheck validation.

This module verifies that the `MissingFinancialDataCheck` correctly identifies
missing (null/NaN) financial data in both overall JSON and DataFrame CSV,
and handles source-specific logic like skipping subprogram checks for MTEP.
"""

import pandas as pd
import numpy as np
import pytest
from armenian_budget.core.enums import SourceType
from armenian_budget.validation.checks.missing_financial_data import MissingFinancialDataCheck


@pytest.fixture
def valid_financial_data():
    """DataFrame and overall dict with valid financial data for BUDGET_LAW."""
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


def test_missing_financial_data_pass(valid_financial_data):  # pylint: disable=redefined-outer-name
    """Test that the check passes with valid financial data."""
    df, overall = valid_financial_data
    check = MissingFinancialDataCheck()
    results = check.validate(df, overall, SourceType.BUDGET_LAW)

    assert len(results) == 4  # overall, state_body, program, subprogram
    for result in results:
        assert result.check_id == "missing_financial_data"
        assert result.passed is True
        assert result.fail_count == 0


def test_missing_financial_data_fail_json(valid_financial_data):  # pylint: disable=redefined-outer-name
    """Test failure when an overall (JSON) field is missing."""
    df, _ = valid_financial_data
    overall = {"overall_total": None}
    check = MissingFinancialDataCheck()
    results = check.validate(df, overall, SourceType.BUDGET_LAW)

    overall_result = results[0]  # First result is 'overall'
    assert overall_result.passed is False
    assert overall_result.fail_count == 1
    assert "Missing overall fields: overall_total" in overall_result.messages


def test_missing_financial_data_fail_csv_program(valid_financial_data):  # pylint: disable=redefined-outer-name
    """Test failure when a program-level CSV field is missing."""
    df, overall = valid_financial_data
    df.loc[0, "program_total"] = np.nan
    check = MissingFinancialDataCheck()
    results = check.validate(df, overall, SourceType.BUDGET_LAW)

    program_result = results[2]  # Third result is 'program'
    assert program_result.passed is False
    assert program_result.fail_count == 1
    assert "Row 0: Missing data for 'program_total'" in program_result.messages[0]


def test_missing_financial_data_fail_csv_subprogram(valid_financial_data):  # pylint: disable=redefined-outer-name
    """Test failure when a subprogram-level CSV field is missing."""
    df, overall = valid_financial_data
    df.loc[0, "subprogram_total"] = None
    check = MissingFinancialDataCheck()
    results = check.validate(df, overall, SourceType.BUDGET_LAW)

    subprogram_result = results[3]  # Fourth result is 'subprogram'
    assert subprogram_result.passed is False
    assert subprogram_result.fail_count == 1
    assert "Row 0: Missing data for 'subprogram_total'" in subprogram_result.messages[0]


def test_missing_financial_data_ignores_zeros():
    """Test that the check correctly flags NaN but ignores zero values."""
    data = {
        "state_body": ["Ministry A", "Ministry B", "Ministry C"],
        "program_code": [100, 200, 300],
        "subprogram_code": [101, 201, 301],
        "state_body_total": [1000.0, 0, 500.0],  # Contains a zero
        "program_total": [1000.0, 200.0, np.nan],  # Contains a NaN
        "subprogram_total": [1000.0, 200.0, 500.0],
    }
    df = pd.DataFrame(data)
    overall = {"overall_total": 1500.0}
    check = MissingFinancialDataCheck()
    results = check.validate(df, overall, SourceType.BUDGET_LAW)

    # The check for state_body_total should pass because 0 is valid data
    state_body_result = results[1]  # Second result is 'state_body'
    assert state_body_result.passed is True, "Should pass as 0 is not missing data."

    # The check for program_total should fail
    program_result = results[2]  # Third result is 'program'
    assert program_result.passed is False, "Should fail due to NaN value."
    assert program_result.fail_count == 1, "Should only count the NaN row as a failure."
    assert "Row 2: Missing data for 'program_total'" in program_result.messages[0]


def test_missing_financial_data_mtep_skips_subprogram():
    """Test that for MTEP, the subprogram check is skipped."""
    data = {
        "state_body": ["Ministry A"],
        "program_code": [100],
        "state_body_total_y0": [1000.0],
        "program_total_y0": [1000.0],
        "state_body_total_y1": [1000.0],
        "program_total_y1": [1000.0],
        "state_body_total_y2": [1000.0],
        "program_total_y2": [1000.0],
    }
    df = pd.DataFrame(data)
    overall = {"overall_total_y0": 1000.0, "overall_total_y1": 1000.0, "overall_total_y2": 1000.0}
    check = MissingFinancialDataCheck()
    results = check.validate(df, overall, SourceType.MTEP)

    # overall, state_body, program (subprogram is skipped)
    assert len(results) == 3
    severities = [r.severity for r in results]
    assert (
        "warning" not in severities
    )  # Subprogram level is warning, so if it's not there, no warning


def test_applies_to_all_source_types():
    """Test that the check applies to all source types."""
    check = MissingFinancialDataCheck()
    for source_type in SourceType:
        assert check.applies_to_source_type(source_type) is True
