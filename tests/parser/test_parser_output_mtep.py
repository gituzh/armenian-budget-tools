"""Parser output verification tests for MTEP data.

These tests verify that the MTEP parser produces correctly structured
output from real Excel files.
"""

from __future__ import annotations

from typing import List

import pytest

from conftest import get_all_available_data, load_budget_data


# Discover available MTEP datasets from processed outputs
_MTEP_PARAMS: List[tuple[int, str]] = [
    item for item in get_all_available_data() if item[1] == "MTEP"
]
_MTEP_IDS = [f"{y}_{t}" for (y, t) in _MTEP_PARAMS]


@pytest.mark.parametrize("year, source_type", _MTEP_PARAMS, ids=_MTEP_IDS)
def test_mtep_csv_non_empty(year: int, source_type: str) -> None:
    """Test that parsed MTEP CSV files are non-empty."""
    data = load_budget_data(year, source_type)
    assert len(data.df) > 0, f"{year}/{source_type}: CSV is empty ({data.file_path})"


@pytest.mark.parametrize("year, source_type", _MTEP_PARAMS, ids=_MTEP_IDS)
def test_mtep_program_codes_integer(year: int, source_type: str) -> None:
    """Test that MTEP program codes are parsed as integers."""
    data = load_budget_data(year, source_type)
    assert str(data.df["program_code"].dtype).startswith("int"), (
        f"{year}/{source_type}: program_code should be integer, found {data.df['program_code'].dtype}"
    )


@pytest.mark.parametrize("year, source_type", _MTEP_PARAMS, ids=_MTEP_IDS)
def test_mtep_program_codes_and_names_match(year: int, source_type: str) -> None:
    """Test that number of unique program codes matches number of unique program names."""
    data = load_budget_data(year, source_type)
    df = data.df
    assert df["program_code"].nunique() == df["program_name"].nunique(), (
        f"{year}/{source_type}: unique program_code count differs from program_name count"
    )
