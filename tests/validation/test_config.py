"""Tests for the validation configuration functions and constants.

This module verifies that the `get_tolerance_for_source` and `get_severity` functions
from `armenian_budget.validation.config` return expected values and handle invalid inputs.
It also includes a meta-test to ensure all expected check IDs are present in the severity map.
"""

import pytest
from armenian_budget.core.enums import SourceType
from armenian_budget.validation.config import get_tolerance_for_source, get_severity


def test_get_tolerance_for_source():
    """Test that get_tolerance_for_source() returns the expected values for each source type."""
    assert get_tolerance_for_source(SourceType.BUDGET_LAW) == 1.0
    assert get_tolerance_for_source(SourceType.MTEP) == 0.5
    assert get_tolerance_for_source(SourceType.SPENDING_Q1) == 5.0
    assert get_tolerance_for_source(SourceType.SPENDING_Q12) == 5.0
    assert get_tolerance_for_source(SourceType.SPENDING_Q123) == 5.0
    assert get_tolerance_for_source(SourceType.SPENDING_Q1234) == 5.0


def test_get_severity_valid():
    """Test that get_severity() returns the expected values for valid check IDs and
    hierarchy levels.
    """
    assert get_severity("empty_identifiers", "state_body") == "error"
    assert get_severity("empty_identifiers", "subprogram") == "warning"

    assert get_severity("negative_totals", "overall") == "warning"
    assert get_severity("negative_totals", "program") == "warning"

    assert get_severity("hierarchical_totals", "state_body") == "error"

    assert get_severity("negative_percentages", "state_body") == "error"
    assert get_severity("negative_percentages", "program") == "warning"


def test_get_severity_invalid_check_id():
    """Test that get_severity() raises ValueError for unknown check IDs."""
    with pytest.raises(ValueError, match="Unknown check_id: non_existent_check"):
        get_severity("non_existent_check", "program")


def test_get_severity_invalid_hierarchy_level():
    """Test that get_severity() raises ValueError for unknown hierarchy levels."""
    with pytest.raises(
        ValueError, match="Invalid hierarchy_level 'non_existent_level' for check 'negative_totals'"
    ):
        get_severity("negative_totals", "non_existent_level")


def test_all_checks_have_severity_configured():
    """Verify that get_severity() works for all known checks.

    This test ensures that all check implementations have proper severity
    configuration by testing the public API rather than internal data structures.

    Note: 'required_fields' is intentionally excluded as it computes severity
    dynamically and doesn't use the severity map.
    """
    # Based on check files in src/armenian_budget/validation/checks/
    # and the plan in docs/_validation_impl.md
    expected_check_ids = [
        "empty_identifiers",
        "missing_financial_data",
        "hierarchical_totals",
        "negative_totals",
        "period_vs_annual",
        "negative_percentages",
        "execution_exceeds_100",
        "percentage_calculation",
    ]

    # Test that get_severity() works for each check
    # Using 'program' as a representative hierarchy level that all checks support
    for check_id in expected_check_ids:
        try:
            severity = get_severity(check_id, "program")
            assert severity in ["error", "warning"], (
                f"Check '{check_id}' returned invalid severity: {severity}"
            )
        except ValueError as e:
            pytest.fail(f"Check ID '{check_id}' is missing from severity configuration: {e}")
