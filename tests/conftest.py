"""Shared pytest configuration, fixtures, and utilities for budget data testing."""

import pytest
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Tuple, Union
from dataclasses import dataclass


@dataclass
class BudgetDataInfo:
    """Container for budget data information."""

    year: int
    source_type: str
    df: pd.DataFrame
    overall_values: Union[Dict, float]
    file_path: str
    overall_path: str


def get_available_data_by_type() -> Dict[str, List[Tuple[int, str]]]:
    """
    Get all available data organized by source type.

    Scans the processed location: data/processed

    Returns:
        Dict mapping source_type to list of (year, source_type) tuples
    """
    output_dir = Path(__file__).parent.parent / "data" / "processed"
    data_by_type = {
        "BUDGET_LAW": [],
        "SPENDING_Q1": [],
        "SPENDING_Q12": [],
        "SPENDING_Q123": [],
        "SPENDING_Q1234": [],
    }
    if not output_dir.exists():
        return data_by_type

    for csv_path in output_dir.glob("*.csv"):
        name = csv_path.name
        if "_" not in name:
            continue
        try:
            year_part, type_part_with_ext = name.split("_", 1)
            year = int(year_part)
            source_type = type_part_with_ext[:-4]  # strip .csv
        except Exception:
            continue
        overall_path = output_dir / f"{year}_{source_type}_overall.json"
        if overall_path.exists() and source_type in data_by_type:
            data_by_type[source_type].append((year, source_type))

    # Sort each list by year
    for source_type in data_by_type:
        data_by_type[source_type].sort()

    return data_by_type


def get_all_available_data() -> List[Tuple[int, str]]:
    """Get all available budget data (year, source_type) combinations from data/processed."""
    output_dir = Path(__file__).parent.parent / "data" / "processed"
    data_combinations: List[Tuple[int, str]] = []

    if not output_dir.exists():
        return data_combinations

    for csv_path in output_dir.glob("*.csv"):
        name = csv_path.name
        if "_" not in name:
            continue
        try:
            year_part, type_part_with_ext = name.split("_", 1)
            year = int(year_part)
            source_type = type_part_with_ext[:-4]  # strip .csv
        except Exception:
            continue
        overall_path = output_dir / f"{year}_{source_type}_overall.json"
        if overall_path.exists():
            data_combinations.append((year, source_type))

    return sorted(data_combinations)


def load_budget_data(year: int, source_type: str) -> BudgetDataInfo:
    """Load budget data for a specific year and source type from data/processed."""
    base_dir = Path(__file__).parent.parent
    file_path = base_dir / f"data/processed/{year}_{source_type}.csv"
    overall_path = base_dir / f"data/processed/{year}_{source_type}_overall.json"

    df = pd.read_csv(file_path, encoding="utf-8-sig")

    with open(overall_path, "r", encoding="utf-8") as f:
        overall_values = json.load(f)

    return BudgetDataInfo(
        year=year,
        source_type=source_type,
        df=df,
        overall_values=overall_values,
        file_path=str(file_path),
        overall_path=str(overall_path),
    )


@pytest.fixture(params=get_all_available_data(), ids=lambda x: f"{x[0]}_{x[1]}")
def all_budget_data(request):
    """Fixture that provides all available budget data."""
    year, source_type = request.param
    return load_budget_data(year, source_type)


@pytest.fixture(
    params=[data for data in get_all_available_data() if data[1] == "BUDGET_LAW"],
    ids=lambda x: f"{x[0]}_{x[1]}",
)
def budget_law_data(request):
    """Fixture that provides only budget law data."""
    year, source_type = request.param
    return load_budget_data(year, source_type)


@pytest.fixture(
    params=[data for data in get_all_available_data() if data[1].startswith("SPENDING_")],
    ids=lambda x: f"{x[0]}_{x[1]}",
)
def spending_data(request):
    """Fixture that provides only spending report data."""
    year, source_type = request.param
    return load_budget_data(year, source_type)


def get_financial_columns(source_type: str) -> Dict[str, List[str]]:
    """
    Get the financial columns for each level based on source type.

    Returns:
        Dict with keys 'state_body', 'program', 'subprogram' mapping to column lists
    """
    if source_type == "BUDGET_LAW":
        return {
            "state_body": ["state_body_total"],
            "program": ["program_total"],
            "subprogram": ["subprogram_total"],
        }
    elif source_type in ["SPENDING_Q1", "SPENDING_Q12", "SPENDING_Q123"]:
        base_cols = [
            "annual_plan",
            "rev_annual_plan",
            "period_plan",
            "rev_period_plan",
            "actual",
        ]
        return {
            "state_body": [f"state_body_{col}" for col in base_cols],
            "program": [f"program_{col}" for col in base_cols],
            "subprogram": [f"subprogram_{col}" for col in base_cols],
        }
    elif source_type == "SPENDING_Q1234":
        base_cols = ["annual_plan", "rev_annual_plan", "actual"]
        return {
            "state_body": [f"state_body_{col}" for col in base_cols],
            "program": [f"program_{col}" for col in base_cols],
            "subprogram": [f"subprogram_{col}" for col in base_cols],
        }
    else:
        raise ValueError(f"Unknown source type: {source_type}")


def get_percentage_columns(source_type: str) -> Dict[str, List[str]]:
    """
    Get the percentage columns for each level based on source type.

    Returns:
        Dict with keys 'state_body', 'program', 'subprogram' mapping to percentage column lists
    """
    if source_type == "BUDGET_LAW":
        return {"state_body": [], "program": [], "subprogram": []}
    elif source_type in ["SPENDING_Q1", "SPENDING_Q12", "SPENDING_Q123"]:
        pct_cols = ["actual_vs_rev_annual_plan", "actual_vs_rev_period_plan"]
        return {
            "state_body": [f"state_body_{col}" for col in pct_cols],
            "program": [f"program_{col}" for col in pct_cols],
            "subprogram": [f"subprogram_{col}" for col in pct_cols],
        }
    elif source_type == "SPENDING_Q1234":
        pct_cols = ["actual_vs_rev_annual_plan"]
        return {
            "state_body": [f"state_body_{col}" for col in pct_cols],
            "program": [f"program_{col}" for col in pct_cols],
            "subprogram": [f"subprogram_{col}" for col in pct_cols],
        }
    else:
        raise ValueError(f"Unknown source type: {source_type}")


@pytest.fixture
def budget_law_by_year():
    """Fixture providing budget law data organized by year."""
    data_by_year = {}
    for year, source_type in get_all_available_data():
        if source_type == "BUDGET_LAW":
            data_by_year[year] = load_budget_data(year, source_type)
    return data_by_year


@pytest.fixture
def spending_by_year():
    """Fixture providing spending data organized by year."""
    data_by_year = {}
    for year, source_type in get_all_available_data():
        if source_type.startswith("SPENDING_"):
            if year not in data_by_year:
                data_by_year[year] = {}
            data_by_year[year][source_type] = load_budget_data(year, source_type)
    return data_by_year
