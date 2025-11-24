"""Parser output verification tests for Spending Report data.

These tests verify that the Spending Report parser produces correctly structured
output from real Excel files.
"""

import pytest

from conftest import load_budget_data, get_all_available_data


# Precompute spending parameter sets and stable IDs
_SPENDING_PARAMS = [
    (y, t) for (y, t) in get_all_available_data() if str(t).startswith("SPENDING_")
]
_SPENDING_IDS = [f"{y}_{t}" for (y, t) in _SPENDING_PARAMS]


@pytest.mark.parametrize("year, source_type", _SPENDING_PARAMS, ids=_SPENDING_IDS)
def test_spending_csv_non_empty(year: int, source_type: str) -> None:
    """Test that parsed Spending Report CSV files are non-empty."""
    data = load_budget_data(year, source_type)
    assert len(data.df) > 0, f"{year}/{source_type}: CSV is empty ({data.file_path})"
