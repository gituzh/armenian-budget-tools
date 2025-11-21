"""Tests for the RequiredFieldsCheck validation.

This module verifies that the `RequiredFieldsCheck` correctly identifies
missing required CSV and JSON fields for various source types.
"""

import numpy as np
import pandas as pd
import pytest
from armenian_budget.core.enums import SourceType
from armenian_budget.validation.checks.required_fields import RequiredFieldsCheck


@pytest.fixture
def budget_law_data():
    """Provides a minimal valid DataFrame and overall dict for BUDGET_LAW."""
    csv_fields, json_fields = (
        [
            "state_body",
            "program_code",
            "program_name",
            "program_goal",
            "program_result_desc",
            "subprogram_code",
            "subprogram_name",
            "subprogram_desc",
            "subprogram_type",
            "state_body_total",
            "program_total",
            "subprogram_total",
        ],
        ["overall_total"],
    )

    df = pd.DataFrame(columns=csv_fields)
    df["program_name"] = [np.nan, np.nan]  # Add a column with only nulls
    overall = {field: 100 for field in json_fields}
    return df, overall


def test_required_fields_pass(budget_law_data):  # pylint: disable=redefined-outer-name
    """Test that the check passes when all required fields are present."""
    df, overall = budget_law_data
    check = RequiredFieldsCheck()
    results = check.validate(df, overall, SourceType.BUDGET_LAW)

    assert len(results) == 1
    result = results[0]
    assert result.check_id == "required_fields"
    assert result.passed is True
    assert result.fail_count == 0
    assert not result.messages


def test_required_fields_pass_with_null_column(budget_law_data):  # pylint: disable=redefined-outer-name
    """Test that the check passes if a required column exists but contains only nulls."""
    df, overall = budget_law_data
    # The fixture already includes a column with only nulls
    df["subprogram_name"] = np.nan

    check = RequiredFieldsCheck()
    results = check.validate(df, overall, SourceType.BUDGET_LAW)

    assert len(results) == 1, "Should produce one result object."
    result = results[0]
    assert result.passed is True, "Check should pass as column header exists."
    assert result.fail_count == 0, "There should be no failures."
    assert not result.messages, "There should be no failure messages."


def test_required_fields_fail_missing_csv():
    """Test that the check fails if a CSV field is missing."""
    df = pd.DataFrame(columns=["state_body", "program_code"])  # Missing many fields
    overall = {"overall_total": 100}
    check = RequiredFieldsCheck()
    results = check.validate(df, overall, SourceType.BUDGET_LAW)

    assert len(results) == 1
    result = results[0]
    assert result.passed is False
    assert result.fail_count > 0
    assert "Missing fields: CSV: program_name" in result.messages[0]


def test_required_fields_fail_missing_json():
    """Test that the check fails if a JSON field is missing."""
    csv_fields = [
        "state_body",
        "program_code",
        "program_name",
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
    df = pd.DataFrame(columns=csv_fields)
    overall = {}  # Missing overall_total
    check = RequiredFieldsCheck()
    results = check.validate(df, overall, SourceType.BUDGET_LAW)

    assert len(results) == 1
    result = results[0]
    assert result.passed is False
    assert result.fail_count == 1
    assert result.messages == ["Missing fields: JSON: overall_total"]


def test_required_fields_fail_missing_both():
    """Test that the check fails if both CSV and JSON fields are missing."""
    df = pd.DataFrame(columns=["state_body"])
    overall = {}
    check = RequiredFieldsCheck()
    results = check.validate(df, overall, SourceType.BUDGET_LAW)

    assert len(results) == 1
    result = results[0]
    assert result.passed is False
    assert result.fail_count > 1
    assert "CSV: program_code" in result.messages[0]
    assert "JSON: overall_total" in result.messages[0]


def test_applies_to_all_source_types():
    """Test that the check applies to all source types."""
    check = RequiredFieldsCheck()
    for source_type in SourceType:
        assert check.applies_to_source_type(source_type) is True
