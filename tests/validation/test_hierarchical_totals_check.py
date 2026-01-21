"""Tests for the HierarchicalTotalsCheck validation.

This module verifies that the `HierarchicalTotalsCheck` correctly identifies
mismatches in hierarchical sums across overall, state body, program, and subprogram levels.
It also ensures correct handling for MTEP data where subprogram checks are skipped.
"""

import pandas as pd
import pytest
from armenian_budget.core.enums import SourceType
from armenian_budget.validation.checks.hierarchical_totals import HierarchicalTotalsCheck


@pytest.fixture
def valid_hierarchy_df():
    """DataFrame with a valid hierarchy for BUDGET_LAW."""
    data = {
        "state_body": ["Ministry A", "Ministry A", "Ministry B"],
        "program_name": ["Program 1", "Program 1", "Program 2"],
        "subprogram_name": ["Sub 1.1", "Sub 1.2", "Sub 2.1"],
        "state_body_total": [150.0, 150.0, 50.0],
        "program_total": [150.0, 150.0, 50.0],
        "subprogram_total": [100.0, 50.0, 50.0],
    }
    return pd.DataFrame(data)


@pytest.fixture
def valid_hierarchy_overall():
    """Overall dict that matches the valid_hierarchy_df."""
    return {"overall_total": 200.0}


def test_hierarchical_totals_pass(valid_hierarchy_df, valid_hierarchy_overall):  # pylint: disable=redefined-outer-name
    """Test that the check passes with a valid hierarchy."""
    check = HierarchicalTotalsCheck()
    results = check.validate(valid_hierarchy_df, valid_hierarchy_overall, SourceType.BUDGET_LAW)

    assert len(results) == 3  # overall_vs_sb, sb_vs_prog, prog_vs_subprog
    for result in results:
        assert result.check_id == "hierarchical_totals"
        assert result.passed is True
        assert result.fail_count == 0


def test_hierarchical_totals_fail_overall(valid_hierarchy_df):  # pylint: disable=redefined-outer-name
    """Test failure when overall total does not match sum of state bodies."""
    overall = {"overall_total": 198.9}  # Should be 200
    check = HierarchicalTotalsCheck()
    results = check.validate(valid_hierarchy_df, overall, SourceType.BUDGET_LAW)

    overall_check = results[0]
    assert overall_check.passed is False
    assert overall_check.fail_count == 1
    assert "Overall overall_total: expected 200.0, got 198.9" in overall_check.messages[0]


def test_hierarchical_totals_fail_state_body(valid_hierarchy_df, valid_hierarchy_overall):  # pylint: disable=redefined-outer-name
    """Test failure when a state body total does not match sum of its programs."""
    valid_hierarchy_df.loc[valid_hierarchy_df["state_body"] == "Ministry A", "state_body_total"] = (
        148.9
    )
    check = HierarchicalTotalsCheck()
    results = check.validate(valid_hierarchy_df, valid_hierarchy_overall, SourceType.BUDGET_LAW)

    sb_check = results[1]
    assert sb_check.passed is False
    assert sb_check.fail_count == 1
    assert "Ministry A: expected 150.0, got 148.9" in sb_check.messages[0]


def test_hierarchical_totals_fail_program(valid_hierarchy_df, valid_hierarchy_overall):  # pylint: disable=redefined-outer-name
    """Test failure when a program total does not match sum of its subprograms."""
    valid_hierarchy_df.loc[valid_hierarchy_df["program_name"] == "Program 1", "program_total"] = (
        148.9
    )
    check = HierarchicalTotalsCheck()
    results = check.validate(valid_hierarchy_df, valid_hierarchy_overall, SourceType.BUDGET_LAW)

    prog_check = results[2]
    assert prog_check.passed is False
    assert prog_check.fail_count == 1
    assert "Ministry A/Program 1: expected 150.0, got 148.9" in prog_check.messages[0]


# Define tolerance values for different scenarios
BUDGET_LAW_TOLERANCE = 1.0
SPENDING_TOLERANCE = 5.0
EPSILON = 0.01


@pytest.mark.parametrize(
    "diff, expect_pass",
    [
        (BUDGET_LAW_TOLERANCE - EPSILON, True),  # Just inside tolerance
        (BUDGET_LAW_TOLERANCE, True),  # Exactly on tolerance
        (BUDGET_LAW_TOLERANCE + EPSILON, False),  # Just outside tolerance
    ],
    ids=["inside_tolerance", "on_tolerance", "outside_tolerance"],
)
def test_hierarchical_totals_tolerance_boundaries(
    valid_hierarchy_df,  # pylint: disable=redefined-outer-name
    valid_hierarchy_overall,  # pylint: disable=redefined-outer-name
    diff,
    expect_pass,
):
    """Test the tolerance boundaries for all hierarchical checks."""
    check = HierarchicalTotalsCheck()
    df = valid_hierarchy_df.copy()
    overall = valid_hierarchy_overall.copy()

    # --- Test Overall vs State Body ---
    overall_modified = overall.copy()
    overall_modified["overall_total"] += diff
    results_overall = check.validate(df, overall_modified, SourceType.BUDGET_LAW)
    overall_check = results_overall[0]
    assert overall_check.passed is expect_pass, f"Overall check failed with diff {diff}"

    # --- Test State Body vs Program ---
    df_modified = df.copy()
    df_modified.loc[df_modified["state_body"] == "Ministry A", "state_body_total"] += diff
    results_sb = check.validate(df_modified, overall, SourceType.BUDGET_LAW)
    sb_check = results_sb[1]
    assert sb_check.passed is expect_pass, f"State Body check failed with diff {diff}"

    # --- Test Program vs Subprogram ---
    df_modified = df.copy()
    df_modified.loc[df_modified["program_name"] == "Program 1", "program_total"] += diff
    results_prog = check.validate(df_modified, overall, SourceType.BUDGET_LAW)
    prog_check = results_prog[2]
    assert prog_check.passed is expect_pass, f"Program check failed with diff {diff}"


def test_hierarchical_totals_mtep_skips_subprogram():
    """Test that for MTEP, the program vs subprogram check is skipped."""
    data = {
        "state_body": ["Ministry A"],
        "program_name": ["Program 1"],
        "state_body_total_y0": [100.0],
        "program_total_y0": [100.0],
        "state_body_total_y1": [100.0],
        "program_total_y1": [100.0],
        "state_body_total_y2": [100.0],
        "program_total_y2": [100.0],
    }
    df = pd.DataFrame(data)
    overall = {
        "overall_total_y0": 100.0,
        "overall_total_y1": 100.0,
        "overall_total_y2": 100.0,
    }
    check = HierarchicalTotalsCheck()
    results = check.validate(df, overall, SourceType.MTEP)

    # 3 bases (y0, y1, y2) * 2 checks (overall, sb) = 6 results
    assert len(results) == 6
    for result in results:
        assert result.passed is True
        # No message should contain "subprogram"
        assert "subprogram" not in str(result.messages) if result.messages else True


def test_applies_to_all_source_types():
    """Test that the check applies to all source types."""
    check = HierarchicalTotalsCheck()
    for source_type in SourceType:
        assert check.applies_to_source_type(source_type) is True
