from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = (
    REPO_ROOT
    / "skills"
    / "armenian-budget-analyst"
    / "scripts"
    / "data_availability.py"
)


def load_script_module():
    spec = importlib.util.spec_from_file_location("data_availability", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_build_matrix_orders_known_and_unknown_columns(tmp_path):
    module = load_script_module()
    for name in [
        "2020_BUDGET_LAW.csv",
        "2020_BUDGET_LAW_GDP.json",
        "2020_SPENDING_Q1.csv",
        "2020_SPENDING_Q1234_GDP.json",
        "2020_Z_EXTRA.csv",
        "2020_AUXILIARY.csv",
        "2021_MTEP.csv",
    ]:
        (tmp_path / name).write_text("stub\n", encoding="utf-8")

    columns, rows = module.build_matrix(tmp_path)

    assert columns == [
        "BUDGET_LAW",
        "BUDGET_LAW_GDP",
        "SPENDING_Q1",
        "SPENDING_Q12",
        "SPENDING_Q123",
        "SPENDING_Q1234",
        "SPENDING_Q1234_GDP",
        "MTEP",
        "AUXILIARY",
        "Z_EXTRA",
    ]
    assert rows == [
        {
            "year": 2020,
            "BUDGET_LAW": "2020_BUDGET_LAW.csv",
            "BUDGET_LAW_GDP": "2020_BUDGET_LAW_GDP.json",
            "SPENDING_Q1": "2020_SPENDING_Q1.csv",
            "SPENDING_Q12": "-",
            "SPENDING_Q123": "-",
            "SPENDING_Q1234": "-",
            "SPENDING_Q1234_GDP": "2020_SPENDING_Q1234_GDP.json",
            "MTEP": "-",
            "AUXILIARY": "2020_AUXILIARY.csv",
            "Z_EXTRA": "2020_Z_EXTRA.csv",
        },
        {
            "year": 2021,
            "BUDGET_LAW": "-",
            "BUDGET_LAW_GDP": "-",
            "SPENDING_Q1": "-",
            "SPENDING_Q12": "-",
            "SPENDING_Q123": "-",
            "SPENDING_Q1234": "-",
            "SPENDING_Q1234_GDP": "-",
            "MTEP": "2021_MTEP.csv",
            "AUXILIARY": "-",
            "Z_EXTRA": "-",
        },
    ]


def test_bundled_data_root_candidates_include_skill_assets_and_repo_data():
    module = load_script_module()
    skill_root = REPO_ROOT / "skills" / "armenian-budget-analyst"
    candidates = module.bundled_data_root_candidates()

    assert (skill_root / "assets" / "data").resolve() in candidates
    assert (skill_root / "assets" / "data" / "processed").resolve() in candidates
    assert (REPO_ROOT / "data" / "processed").resolve() in candidates


def test_cli_both_outputs_markdown_and_json_for_repo_data():
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--data-root",
            str(REPO_ROOT / "data" / "processed"),
            "--format",
            "both",
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert (
        "| Year | BUDGET_LAW | BUDGET_LAW_GDP | SPENDING_Q1 | "
        "SPENDING_Q12 | SPENDING_Q123 | SPENDING_Q1234 | "
        "SPENDING_Q1234_GDP | MTEP |"
        in result.stdout
    )

    json_start = result.stdout.find("{")
    assert json_start != -1
    payload = json.loads(result.stdout[json_start:])

    assert payload["columns"][:6] == [
        "BUDGET_LAW",
        "BUDGET_LAW_GDP",
        "SPENDING_Q1",
        "SPENDING_Q12",
        "SPENDING_Q123",
        "SPENDING_Q1234",
    ]
    assert payload["columns"][6:8] == [
        "SPENDING_Q1234_GDP",
        "MTEP",
    ]
    assert any(row["BUDGET_LAW"] == "2019_BUDGET_LAW.csv" for row in payload["rows"])
    assert any(
        row["BUDGET_LAW_GDP"] == "2025_BUDGET_LAW_GDP.json"
        for row in payload["rows"]
    )
    assert any(
        row["SPENDING_Q123"] == "2025_SPENDING_Q123.csv" for row in payload["rows"]
    )
    assert any(
        row["SPENDING_Q1234_GDP"] == "2025_SPENDING_Q1234_GDP.json"
        for row in payload["rows"]
    )
    assert any(
        row["year"] == 2026 and row["SPENDING_Q1"] == "2026_SPENDING_Q1.csv"
        for row in payload["rows"]
    )
    assert any(row["MTEP"] == "2024_MTEP.csv" for row in payload["rows"])
