import pytest
import pandas as pd
import os
from pathlib import Path
import warnings


def get_available_budget_years():
    """Get all available budget years from the output directory."""
    output_dir = Path("output")
    years = []
    for year_dir in output_dir.glob("*"):
        if year_dir.is_dir() and year_dir.name.isdigit():
            csv_path = year_dir / "budget_by_program_and_subprogram.csv"
            if csv_path.exists():
                years.append(int(year_dir.name))
    return sorted(years)


@pytest.fixture(params=get_available_budget_years())
def budget_data(request):
    """
    Parametrized fixture that loads budget data for each available year.
    Returns a tuple of (year, DataFrame).
    """
    year = request.param
    file_path = f"output/{year}/budget_by_program_and_subprogram.csv"
    df = pd.read_csv(file_path, encoding="utf-8-sig")
    return year, df


def test_program_codes_and_names_match(budget_data):
    """Test that number of unique program codes matches number of unique program names."""
    year, df = budget_data
    unique_codes = len(df["program_code"].unique())
    unique_names = len(df["program_name"].unique())

    assert unique_codes == unique_names, (
        f"{year}: Number of unique program codes ({unique_codes}) "
        f"doesn't match number of unique program names ({unique_names})"
    )


def test_subprogram_sums_match_program_totals(budget_data):
    """Test that sum of subprograms within each program equals program total."""
    year, df = budget_data

    # Calculate sums of subprograms by state body and program
    subprogram_sums = (
        df.groupby(["state_body", "program_code"])["subprogram_total"]
        .sum()
        .reset_index()
    )

    # Get program totals
    program_totals = df.drop_duplicates(subset=["state_body", "program_code"])[
        ["state_body", "program_code", "program_total"]
    ]

    # Merge and check for mismatches
    merged = subprogram_sums.merge(
        program_totals, on=["state_body", "program_code"]
    )
    mismatches = merged[
        round(merged["subprogram_total"], 2)
        != round(merged["program_total"], 2)
    ]

    assert len(mismatches) == 0, (
        f"{year}: Found mismatches between subprogram sums and program totals:\n"
        f"{mismatches.to_string()}"
    )


def test_program_distribution(budget_data):
    """Test that programs are properly distributed across state bodies."""
    year, df = budget_data

    program_counts = (
        df.groupby("state_body")["program_code"]
        .nunique()
        .sort_values(ascending=False)
    )

    assert (
        program_counts.nunique() > 1
    ), f"{year}: All state bodies have the same number of program codes"
    assert (
        program_counts.max() > 1
    ), f"{year}: No state body has multiple programs"


def test_grand_total_consistency(budget_data):
    """Test that grand total matches sum of all totals."""
    year, df = budget_data
    
    # Read grand total from file
    grand_total_path = Path(f"output/{year}/grand_total.txt")
    assert grand_total_path.exists(), f"{year}: Grand total file not found"
    
    with open(grand_total_path, 'r') as f:
        content = f.read()
        grand_total = float(content.split(":")[1].strip())
    
    # Calculate all types of totals (rounded to 2 decimal places)
    state_body_sum = round(
        df.drop_duplicates(subset="state_body")["state_body_total"].sum(),
        2,
    )
    program_sum = round(
        df.drop_duplicates(subset="program_code")["program_total"].sum(),
        2,
    )
    subprogram_sum = round(df["subprogram_total"].sum(), 2)
    grand_total = round(grand_total, 2)
    
    # Compare grand total with each type of sum
    assert grand_total == state_body_sum, (
        f"{year}: Grand total ({grand_total}) doesn't match "
        f"sum of state body totals ({state_body_sum})"
    )
    
    assert grand_total == program_sum, (
        f"{year}: Grand total ({grand_total}) doesn't match "
        f"sum of program totals ({program_sum})"
    )
    
    assert grand_total == subprogram_sum, (
        f"{year}: Grand total ({grand_total}) doesn't match "
        f"sum of subprogram totals ({subprogram_sum})"
    )


def test_state_body_total_consistency(budget_data):
    """Test that state body totals match sum of their programs and subprograms."""
    year, df = budget_data
    
    # For each state body
    state_bodies = df["state_body"].unique()
    for state_body in state_bodies:
        state_body_data = df[df["state_body"] == state_body]
        
        # Get state body total
        state_body_total = round(
            state_body_data["state_body_total"].iloc[0],
            2
        )
        
        # Calculate sum of programs for this state body
        program_sum = round(
            state_body_data.drop_duplicates(
                subset="program_code"
            )["program_total"].sum(),
            2
        )
        
        # Calculate sum of subprograms for this state body
        subprogram_sum = round(
            state_body_data["subprogram_total"].sum(),
            2
        )
        
        # Compare totals
        assert state_body_total == program_sum, (
            f"{year}: State body '{state_body}' total ({state_body_total}) "
            f"doesn't match sum of its program totals ({program_sum})"
        )
        
        assert state_body_total == subprogram_sum, (
            f"{year}: State body '{state_body}' total ({state_body_total}) "
            f"doesn't match sum of its subprogram totals ({subprogram_sum})"
        )


def test_program_total_consistency(budget_data):
    """Test that program totals match sum of their subprograms."""
    year, df = budget_data
    
    # Group subprograms by state body and program
    subprogram_sums = (
        df.groupby(["state_body", "program_code"])["subprogram_total"]
        .sum()
        .reset_index()
    )
    
    # Get program totals
    program_totals = df.drop_duplicates(subset=["state_body", "program_code"])[
        ["state_body", "program_code", "program_total"]
    ]
    
    # Merge and check for mismatches
    merged = subprogram_sums.merge(
        program_totals, 
        on=["state_body", "program_code"]
    )
    
    mismatches = merged[
        round(merged["subprogram_total"], 2) != round(merged["program_total"], 2)
    ]
    
    assert len(mismatches) == 0, (
        f"{year}: Found mismatches between program totals and their subprogram sums:\n"
        f"{mismatches.to_string()}"
    )


def test_data_quality(budget_data):
    """Test data quality (null values, empty strings, negative values warnings)."""
    year, df = budget_data
    
    required_columns = [
        "state_body", "state_body_total",
        "program_code", "program_name", "program_total",
        "subprogram_code", "subprogram_name", "subprogram_total"
    ]
    
    for column in required_columns:
        # Check for null values
        null_count = df[column].isnull().sum()
        assert null_count == 0, (
            f"{year}: Found {null_count} null values in column '{column}'"
        )
        
        # Check for empty strings in text columns
        if df[column].dtype == "object":
            empty_count = (df[column].str.strip() == "").sum()
            assert empty_count == 0, (
                f"{year}: Found {empty_count} empty strings in column '{column}'"
            )
        
        # Warn about negative values in total columns
        if column in ["state_body_total", "program_total", "subprogram_total"]:
            negative_rows = df[df[column] < 0]
            if not negative_rows.empty:
                warning_msg = (
                    f"\n{year}: Found {len(negative_rows)} negative values in column '{column}':"
                    f"\nNegative rows:"
                    f"\n{negative_rows[['state_body', 'program_code', 'subprogram_code', column]].to_string()}"
                )
                warnings.warn(warning_msg, UserWarning)
