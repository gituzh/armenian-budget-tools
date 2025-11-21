"""Tests for the EmptyIdentifiersCheck validation.

This module verifies that the `EmptyIdentifiersCheck` correctly identifies
empty identifier fields (state_body, program_name, subprogram_name)
and handles source-specific logic like skipping subprogram checks for MTEP.
"""

import pandas as pd
import pytest

from armenian_budget.core.enums import SourceType
from armenian_budget.validation.checks.empty_identifiers import EmptyIdentifiersCheck


@pytest.fixture
def valid_identifiers_df():
    """DataFrame with valid (non-empty) identifiers."""
    data = {
        "state_body": ["Ministry of Finance", "Ministry of Health"],
        "program_name": ["Program A", "Program B"],
        "subprogram_name": ["Subprogram A1", "Subprogram B1"],
        "program_code": [100, 200],
        "subprogram_code": [101, 201],
    }
    return pd.DataFrame(data)


def test_empty_identifiers_pass(valid_identifiers_df):  # pylint: disable=redefined-outer-name
    """Test that the check passes with valid identifiers."""
    check = EmptyIdentifiersCheck()
    results = check.validate(valid_identifiers_df, {}, SourceType.BUDGET_LAW)

    assert len(results) == 3
    for result in results:
        assert result.check_id == "empty_identifiers"
        assert result.passed is True
        assert result.fail_count == 0


def test_empty_identifiers_fail_comprehensive():
    """Test failure with None, empty string, and whitespace across different fields."""
    data = {
        "state_body": [None, "Ministry of Health", "Ministry of Education", "Ministry of Justice"],
        "program_name": ["Program A", "", "Program C", "Program D"],
        "subprogram_name": ["Subprogram A1", "Subprogram B1", "   ", "Subprogram D1"],
        "program_code": [100, 200, 300, 400],
        "subprogram_code": [101, 201, 301, 401],
    }
    df = pd.DataFrame(data)
    check = EmptyIdentifiersCheck()
    results = check.validate(df, {}, SourceType.SPENDING_Q1)

    # State body check should fail for the first row (None)
    state_body_result = results[0]
    assert state_body_result.passed is False
    assert state_body_result.fail_count == 1
    assert "Row 0" in state_body_result.messages[0]

    # Program name check should fail for the second row ("")
    program_result = results[1]
    assert program_result.passed is False
    assert program_result.fail_count == 1
    assert "Row 1" in program_result.messages[0]

    # Subprogram name check should fail for the third row ("   ")
    subprogram_result = results[2]
    assert subprogram_result.passed is False
    assert subprogram_result.fail_count == 1
    assert "Row 2" in subprogram_result.messages[0]


def test_empty_identifiers_robustness_with_non_string_data():
    """Test that the check doesn't crash with non-string data like numbers."""
    data = {
        "state_body": ["Ministry of Finance", "Ministry of Health"],
        "program_name": ["Program A", "Program B"],
        "subprogram_name": [12345, "Subprogram B1"],  # Contains a number
        "program_code": [100, 200],
        "subprogram_code": [101, 201],
    }
    df = pd.DataFrame(data)
    check = EmptyIdentifiersCheck()

    # The check should run without raising an exception
    try:
        results = check.validate(df, {}, SourceType.BUDGET_LAW)
        # It should pass, as '12345' is not an empty identifier
        subprogram_result = results[2]  # Assumes subprogram is the 3rd result
        assert subprogram_result.passed is True
    except Exception as e:
        pytest.fail(f"Check crashed on non-string data: {e}")


def test_empty_identifiers_mtep_skips_subprogram():
    """Test that for MTEP, the subprogram check is skipped."""
    data = {
        "state_body": ["Ministry of Finance", "Ministry of Health"],
        "program_name": ["Program A", "Program B"],
        # No subprogram_name column for MTEP
        "program_code": [100, 200],
    }
    df = pd.DataFrame(data)
    check = EmptyIdentifiersCheck()
    results = check.validate(df, {}, SourceType.MTEP)

    # Should only have results for state_body and program_name, not subprogram
    assert len(results) == 2


def test_applies_to_all_source_types():
    """Test that the check applies to all source types."""
    check = EmptyIdentifiersCheck()
    for source_type in SourceType:
        assert check.applies_to_source_type(source_type) is True
