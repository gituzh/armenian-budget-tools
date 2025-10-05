from __future__ import annotations

import json
from pathlib import Path
from typing import List

import pandas as pd
import pytest

from armenian_budget.validation import runner

# Import from top-level tests.conftest when running pytest from repo root
import sys
from pathlib import Path as _Path

_root = _Path(__file__).resolve().parents[1]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
from conftest import get_all_available_data, load_budget_data  # type: ignore


def test_mtep_rollups_and_required_columns(tmp_path: Path) -> None:
    # Synthetic minimal MTEP-like dataframe
    data = {
        "state_body": ["Ministry A", "Ministry A", "Ministry B"],
        "program_code": [101, 102, 201],
        "program_name": ["P1", "P2", "P3"],
        "program_goal": ["g", "g", "g"],
        "program_result_desc": ["r", "r", "r"],
        # y0/y1/y2 totals per program
        "program_total_y0": [100.0, 50.0, 30.0],
        "program_total_y1": [110.0, 55.0, 33.0],
        "program_total_y2": [120.0, 60.0, 36.0],
        # state_body totals repeated per program row (as produced by parser)
        "state_body_total_y0": [150.0, 150.0, 30.0],
        "state_body_total_y1": [165.0, 165.0, 33.0],
        "state_body_total_y2": [180.0, 180.0, 36.0],
    }
    df = pd.DataFrame(data)

    # Save CSV to temp and craft overall json path
    csv_path = tmp_path / "2024_MTEP.csv"
    df.to_csv(csv_path, index=False)
    overall = {
        "plan_years": [2024, 2025, 2026],
        "overall_total_y0": float(
            df.drop_duplicates("state_body")["state_body_total_y0"].sum()
        ),
        "overall_total_y1": float(
            df.drop_duplicates("state_body")["state_body_total_y1"].sum()
        ),
        "overall_total_y2": float(
            df.drop_duplicates("state_body")["state_body_total_y2"].sum()
        ),
    }
    overall_path = tmp_path / "2024_MTEP_overall.json"
    overall_path.write_text(__import__("json").dumps(overall))

    # Run checks via runner
    rep = runner.run_all_checks(df, csv_path)
    assert not rep.has_errors(strict=True)


# Discover available MTEP datasets from processed outputs
_MTEP_PARAMS: List[tuple[int, str]] = [
    item for item in get_all_available_data() if item[1] == "MTEP"
]
_MTEP_IDS = [f"{y}_{t}" for (y, t) in _MTEP_PARAMS]


@pytest.mark.parametrize("year, source_type", _MTEP_PARAMS, ids=_MTEP_IDS)
def test_mtep_csv_non_empty(year: int, source_type: str) -> None:
    data = load_budget_data(year, source_type)
    assert len(data.df) > 0, f"{year}/{source_type}: CSV is empty ({data.file_path})"


@pytest.mark.parametrize("year, source_type", _MTEP_PARAMS, ids=_MTEP_IDS)
def test_mtep_overall_matches_csv(year: int, source_type: str) -> None:
    data = load_budget_data(year, source_type)
    df = data.df
    overall = data.overall_values if isinstance(data.overall_values, dict) else {}

    for y in ["y0", "y1", "y2"]:
        sb_col = f"state_body_total_{y}"
        key = f"overall_total_{y}"
        if sb_col in df.columns and key in overall:
            sb_sum = round(float(df.drop_duplicates("state_body")[sb_col].sum()), 2)
            ov = round(float(overall[key]), 2)
            assert abs(sb_sum - ov) <= 0.5, (
                f"{year}/{source_type}: {key} mismatch: overall={ov}, sum={sb_sum}"
            )


@pytest.mark.parametrize("year, source_type", _MTEP_PARAMS, ids=_MTEP_IDS)
def test_mtep_program_codes_integer(year: int, source_type: str) -> None:
    data = load_budget_data(year, source_type)
    assert str(data.df["program_code"].dtype).startswith("int"), (
        f"{year}/{source_type}: program_code should be integer, found {data.df['program_code'].dtype}"
    )


@pytest.mark.parametrize("year, source_type", _MTEP_PARAMS, ids=_MTEP_IDS)
def test_mtep_program_codes_and_names_match(year: int, source_type: str) -> None:
    data = load_budget_data(year, source_type)
    df = data.df
    assert df["program_code"].nunique() == df["program_name"].nunique(), (
        f"{year}/{source_type}: unique program_code count differs from program_name count"
    )


@pytest.mark.parametrize("year, source_type", _MTEP_PARAMS, ids=_MTEP_IDS)
def test_mtep_no_negative_totals(year: int, source_type: str) -> None:
    data = load_budget_data(year, source_type)
    df = data.df
    import warnings

    # Error if any state_body_total_y* negative
    for col in ["state_body_total_y0", "state_body_total_y1", "state_body_total_y2"]:
        if col in df.columns:
            neg = int((df[col] < 0).sum())
            assert neg == 0, f"{year}/{source_type}: negative values in {col}: {neg}"

    # Warn (but do not fail) if any program_total_y* negative
    for col in ["program_total_y0", "program_total_y1", "program_total_y2"]:
        if col in df.columns:
            mask = df[col] < 0
            neg = int(mask.sum())
            if neg:
                sample_cols = [
                    c
                    for c in ["state_body", "program_code", "program_name", col]
                    if c in df.columns
                ]
                sample = df.loc[mask, sample_cols].head(10).to_string(index=False)
                warnings.warn(
                    f"{year}/{source_type}: {neg} negative values in {col}.\nSample:\n{sample}",
                    UserWarning,
                )
