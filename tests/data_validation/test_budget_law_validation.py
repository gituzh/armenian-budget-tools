"""Tests specifically for budget law data validation."""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
test_dir = Path(__file__).parent.parent
if str(test_dir) not in sys.path:
    sys.path.insert(0, str(test_dir))

from conftest import budget_law_data, BudgetDataInfo

# Import validation helpers with fallback
try:
    from utils.validation_helpers import (
        validate_financial_totals_consistency,
        validate_data_quality_basic,
    )
except ImportError:
    sys.path.insert(0, str(test_dir / "utils"))
    from validation_helpers import (
        validate_financial_totals_consistency,
        validate_data_quality_basic,
    )


def test_budget_law_financial_consistency(budget_law_data):
    """Test that budget law financial totals are consistent across all levels."""
    errors = validate_financial_totals_consistency(budget_law_data)

    if errors:
        pytest.fail("\n".join(errors))


def test_budget_law_data_quality(budget_law_data):
    """Test basic data quality for budget law files."""
    errors = validate_data_quality_basic(budget_law_data)

    if errors:
        pytest.fail("\n".join(errors))


def test_budget_law_program_codes_and_names_match(budget_law_data):
    """Test that number of unique program codes matches number of unique program names."""
    df = budget_law_data.df
    unique_codes = len(df["program_code"].unique())
    unique_names = len(df["program_name"].unique())

    assert unique_codes == unique_names, (
        f"{budget_law_data.year}/{budget_law_data.source_type}: "
        f"Number of unique program codes ({unique_codes}) "
        f"doesn't match number of unique program names ({unique_names})"
    )


def test_budget_law_program_distribution(budget_law_data):
    """Test that programs are properly distributed across state bodies."""
    df = budget_law_data.df

    program_counts = (
        df.groupby("state_body")["program_code"]
        .nunique()
        .sort_values(ascending=False)
    )

    assert program_counts.nunique() > 1, (
        f"{budget_law_data.year}/{budget_law_data.source_type}: All state bodies have the same number of programs"
    )

    assert program_counts.max() > 1, (
        f"{budget_law_data.year}/{budget_law_data.source_type}: No state body has multiple programs"
    )


def test_budget_law_grand_total_consistency(budget_law_data):
    """Test that grand total matches sum of all totals."""
    df = budget_law_data.df
    overall_values = budget_law_data.overall_values

    # Extract grand total
    if isinstance(overall_values, dict):
        grand_total = overall_values.get("overall_total", 0)
    else:
        grand_total = overall_values

    # Calculate sums (rounded to 2 decimal places)
    state_body_sum = round(
        df.drop_duplicates(subset="state_body")["state_body_total"].sum(), 2
    )
    program_sum = round(
        df.drop_duplicates(subset="program_code")["program_total"].sum(), 2
    )
    subprogram_sum = round(df["subprogram_total"].sum(), 2)
    grand_total = round(grand_total, 2)

    # Compare grand total with each type of sum
    assert grand_total == state_body_sum, (
        f"{budget_law_data.year}/{budget_law_data.source_type}: "
        f"Grand total ({grand_total}) differs from state body totals ({state_body_sum}) "
        f"by {grand_total - state_body_sum}"
    )

    assert grand_total == program_sum, (
        f"{budget_law_data.year}/{budget_law_data.source_type}: "
        f"Grand total ({grand_total}) differs from program totals ({program_sum}) "
        f"by {grand_total - program_sum}"
    )

    assert grand_total == subprogram_sum, (
        f"{budget_law_data.year}/{budget_law_data.source_type}: "
        f"Grand total ({grand_total}) differs from subprogram totals ({subprogram_sum}) "
        f"by {grand_total - subprogram_sum}"
    )


def test_budget_law_program_codes_format(budget_law_data):
    """Test that program and subprogram codes are integers and properly formatted."""
    df = budget_law_data.df

    # Check program_code is integer
    assert df["program_code"].dtype in ["int64", "int32"], (
        f"{budget_law_data.year}/{budget_law_data.source_type}: "
        f"program_code should be integer type, found {df['program_code'].dtype}"
    )

    # Check subprogram_code is integer
    assert df["subprogram_code"].dtype in ["int64", "int32"], (
        f"{budget_law_data.year}/{budget_law_data.source_type}: "
        f"subprogram_code should be integer type, found {df['subprogram_code'].dtype}"
    )

    # For 2025, verify program_code_ext
    if budget_law_data.year == 2025:
        assert "program_code_ext" in df.columns, (
            f"{budget_law_data.year}/{budget_law_data.source_type}: program_code_ext column is missing"
        )

        assert df["program_code_ext"].dtype in ["int64", "int32"], (
            f"{budget_law_data.year}/{budget_law_data.source_type}: "
            f"program_code_ext should be integer type, found {df['program_code_ext'].dtype}"
        )

        # Verify program_code matches program_code_ext
        mismatches = df[df["program_code"] != df["program_code_ext"]]
        assert len(mismatches) == 0, (
            f"{budget_law_data.year}/{budget_law_data.source_type}: "
            f"Found {len(mismatches)} rows where program_code doesn't match program_code_ext"
        )


def test_budget_law_no_negative_totals(budget_law_data):
    """Test that budget law files don't have negative total values."""
    import warnings

    df = budget_law_data.df

    negative_state_body = (df["state_body_total"] < 0).sum()
    negative_program = (df["program_total"] < 0).sum()
    negative_subprogram = (df["subprogram_total"] < 0).sum()

    # Fail for state body negative values (critical error)
    assert negative_state_body == 0, (
        f"{budget_law_data.year}/{budget_law_data.source_type}: "
        f"Found {negative_state_body} negative state body totals"
    )

    # Warn for program negative values
    if negative_program > 0:
        negative_program_rows = df[df["program_total"] < 0]
        warning_msg = (
            f"\n{budget_law_data.year}/{budget_law_data.source_type}: "
            f"Found {negative_program} negative program totals:"
            f"\nNegative rows:"
            f"\n{negative_program_rows[['state_body', 'program_code', 'program_name', 'program_total']].to_string()}"
        )
        warnings.warn(warning_msg, UserWarning)

    # Warn for subprogram negative values
    if negative_subprogram > 0:
        negative_subprogram_rows = df[df["subprogram_total"] < 0]
        warning_msg = (
            f"\n{budget_law_data.year}/{budget_law_data.source_type}: "
            f"Found {negative_subprogram} negative subprogram totals:"
            f"\nNegative rows:"
            f"\n{negative_subprogram_rows[['state_body', 'program_code', 'subprogram_code', 'subprogram_name', 'subprogram_total']].to_string()}"
        )
        warnings.warn(warning_msg, UserWarning)
