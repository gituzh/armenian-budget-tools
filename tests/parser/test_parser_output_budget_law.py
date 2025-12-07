"""Parser output verification tests for Budget Law data.

These tests verify that the Budget Law parser produces correctly structured
output from real Excel files.
"""

import pytest
from conftest import get_all_available_data, load_budget_data


def test_budget_law_program_codes_and_names_match(budget_law_data):  # pylint: disable=redefined-outer-name
    """Test that number of unique program codes matches number of unique program names."""
    df = budget_law_data.df
    unique_codes = len(df["program_code"].unique())
    unique_names = len(df["program_name"].unique())

    assert unique_codes == unique_names, (
        f"{budget_law_data.year}/{budget_law_data.source_type}: "
        f"Number of unique program codes ({unique_codes}) "
        f"doesn't match number of unique program names ({unique_names})"
    )


def test_budget_law_program_codes_format(budget_law_data):  # pylint: disable=redefined-outer-name
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

    # For 2025+, verify program_code_ext
    if budget_law_data.year >= 2025:
        assert "program_code_ext" in df.columns, (
            f"{budget_law_data.year}/{budget_law_data.source_type}: "
            f"program_code_ext column is missing"
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


# Non-empty CSV check for Budget Law datasets
_BL_PARAMS = [(y, t) for (y, t) in get_all_available_data() if str(t) == "BUDGET_LAW"]
_BL_IDS = [f"{y}_{t}" for (y, t) in _BL_PARAMS]


@pytest.mark.parametrize("year, source_type", _BL_PARAMS, ids=_BL_IDS)
def test_budget_law_csv_non_empty(year: int, source_type: str) -> None:
    """Test that parsed Budget Law CSV files are non-empty."""
    data = load_budget_data(year, source_type)
    assert len(data.df) > 0, f"{year}/{source_type}: CSV is empty ({data.file_path})"
