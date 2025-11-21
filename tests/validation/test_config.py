"""Tests for the validation configuration functions and constants.

This module verifies that the `get_tolerance_for_source` and `get_severity` functions
from `armenian_budget.validation.config` return expected values and handle invalid inputs.
It also includes a meta-test to ensure all expected check IDs are present in the severity map.
"""

import pytest
from armenian_budget.core.enums import SourceType
from armenian_budget.validation.config import get_tolerance_for_source, get_severity


def test_get_tolerance_for_source():
    assert get_tolerance_for_source(SourceType.BUDGET_LAW) == 1.0
    assert get_tolerance_for_source(SourceType.MTEP) == 0.5
    assert get_tolerance_for_source(SourceType.SPENDING_Q1) == 5.0
    assert get_tolerance_for_source(SourceType.SPENDING_Q12) == 5.0
    assert get_tolerance_for_source(SourceType.SPENDING_Q123) == 5.0
    assert get_tolerance_for_source(SourceType.SPENDING_Q1234) == 5.0


def test_get_severity_valid():
    # Test a few representative cases
    assert get_severity("empty_identifiers", "state_body") == "error"
    assert get_severity("empty_identifiers", "subprogram") == "warning"

    assert get_severity("negative_totals", "overall") == "warning"
    assert get_severity("negative_totals", "program") == "warning"

    assert get_severity("hierarchical_totals", "state_body") == "error"

    assert get_severity("negative_percentages", "state_body") == "error"
    assert get_severity("negative_percentages", "program") == "warning"


def test_get_severity_invalid_check_id():
    with pytest.raises(ValueError, match="Unknown check_id: non_existent_check"):
        get_severity("non_existent_check", "program")


def test_get_severity_invalid_hierarchy_level():
    with pytest.raises(
        ValueError, match="Invalid hierarchy_level 'non_existent_level' for check 'negative_totals'"
    ):
        get_severity("negative_totals", "non_existent_level")


def test_all_check_ids_in_map():
    # This test ensures that all check implementation files will have a corresponding entry in the severity map.
    # This is a bit of a meta-test.
    from armenian_budget.validation.config import _SEVERITY_MAP

    # Based on files in src/armenian_budget/validation/checks/
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
        # "required_fields" is missing from the map, but it doesn't use get_severity.
        # It computes severity manually. Let's check the implementation.
    ]

    # After checking required_fields.py, it doesn't use get_severity. It has its own logic.
    # So we don't need to add it to the map.

    for check_id in expected_check_ids:
        assert check_id in _SEVERITY_MAP, (
            f"Check ID '{check_id}' is missing from _SEVERITY_MAP in config.py"
        )
