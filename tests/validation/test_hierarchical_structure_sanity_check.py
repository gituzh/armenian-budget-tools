"""Tests for the HierarchicalStructureSanityCheck validation.

This module verifies that the `HierarchicalStructureSanityCheck` correctly
identifies degenerate or flat hierarchical structures in budget data.
"""

import pandas as pd
import pytest
from armenian_budget.core.enums import SourceType
from armenian_budget.validation.checks.hierarchical_structure_sanity import (
    HierarchicalStructureSanityCheck,
)
from armenian_budget.validation.config import get_severity


@pytest.fixture
def normal_hierarchy_data():
    """DataFrame and overall dict with normal hierarchical structure."""
    data = {
        "state_body": [
            "Ministry A",
            "Ministry A",
            "Ministry A",
            "Ministry B",
            "Ministry B",
            "Ministry C",
        ],
        "program_code": [100, 101, 102, 200, 201, 300],
        "program_name": ["Prog 100", "Prog 101", "Prog 102", "Prog 200", "Prog 201", "Prog 300"],
        "subprogram_code": [1001, 1011, 1021, 2001, 2011, 3001],
    }
    df = pd.DataFrame(data)
    overall = {}
    return df, overall


def test_hierarchical_structure_sanity_pass(normal_hierarchy_data):  # pylint: disable=redefined-outer-name
    """Test that the check passes with normal hierarchical structure."""
    df, _overall = normal_hierarchy_data
    check = HierarchicalStructureSanityCheck()
    results = check.validate(df)

    assert len(results) == 1
    result = results[0]
    assert result.check_id == "hierarchical_structure_sanity"
    assert result.passed is True
    assert result.fail_count == 0
    assert result.severity == get_severity("hierarchical_structure_sanity", "overall")


def test_hierarchical_structure_sanity_fail_identical_counts():
    """Test failure when all state bodies have identical program counts."""
    # All state bodies have exactly 2 programs each
    data = {
        "state_body": [
            "Ministry A",
            "Ministry A",
            "Ministry B",
            "Ministry B",
            "Ministry C",
            "Ministry C",
        ],
        "program_code": [100, 101, 200, 201, 300, 301],
        "program_name": ["Prog 100", "Prog 101", "Prog 200", "Prog 201", "Prog 300", "Prog 301"],
        "subprogram_code": [1001, 1011, 2001, 2011, 3001, 3011],
    }
    df = pd.DataFrame(data)

    check = HierarchicalStructureSanityCheck()
    results = check.validate(df)

    assert len(results) == 1
    result = results[0]
    assert result.check_id == "hierarchical_structure_sanity"
    assert result.passed is False
    assert result.fail_count == 1
    assert "identical program count" in result.messages[0]


def test_hierarchical_structure_sanity_fail_no_multi_program():
    """Test failure when no state body has multiple programs (but counts vary)."""
    # State bodies have different program counts (2, 3, 1) but none have multiple
    # Wait - all have at least 1, so this case can't exist without also failing identical count
    # Let's test a case where counts vary but max is still 1
    # Actually, if max == 1, then all counts must be 1 (or 0), so identical count also fails
    # This test needs to be the "both fail" case
    data = {
        "state_body": ["Ministry A", "Ministry B", "Ministry C"],
        "program_code": [100, 200, 300],
        "program_name": ["Prog 100", "Prog 200", "Prog 300"],
        "subprogram_code": [1001, 2001, 3001],
    }
    df = pd.DataFrame(data)

    check = HierarchicalStructureSanityCheck()
    results = check.validate(df)

    assert len(results) == 1
    result = results[0]
    assert result.check_id == "hierarchical_structure_sanity"
    assert result.passed is False
    # Both conditions fail: identical count (1) AND no multi-program
    assert result.fail_count == 2
    assert any("No state body has multiple programs" in msg for msg in result.messages)
    assert any("identical program count" in msg for msg in result.messages)


def test_hierarchical_structure_sanity_source_type_filter():
    """Test that the check only runs for BUDGET_LAW source type."""
    check = HierarchicalStructureSanityCheck()
    assert check.applies_to_source_type(SourceType.BUDGET_LAW) is True
    assert check.applies_to_source_type(SourceType.SPENDING_Q1) is False
    assert check.applies_to_source_type(SourceType.MTEP) is False
