from pathlib import Path

import pytest

from armenian_budget.core.enums import SourceType
from armenian_budget.core.utils import (
    dataset_stem,
    get_processed_paths,
    validate_label,
    year_dir_name,
)


def test_dataset_stem():
    assert dataset_stem(2026, "BUDGET_LAW") == "2026_BUDGET_LAW"
    assert dataset_stem(2026, "BUDGET_LAW", "EDRAFT") == "2026_BUDGET_LAW_EDRAFT"


def test_year_dir_name():
    assert year_dir_name(2026) == "2026"
    assert year_dir_name(2026, "EDRAFT") == "2026_EDRAFT"


def test_processed_paths_with_label():
    root = Path("processed")

    csv_path, overall_path = get_processed_paths(
        2026, SourceType.BUDGET_LAW, root, "EDRAFT"
    )
    assert csv_path == root / "2026_BUDGET_LAW_EDRAFT.csv"
    assert overall_path == root / "2026_BUDGET_LAW_EDRAFT_overall.json"

    csv_path, overall_path = get_processed_paths(2026, SourceType.BUDGET_LAW, root)
    assert csv_path == root / "2026_BUDGET_LAW.csv"
    assert overall_path == root / "2026_BUDGET_LAW_overall.json"


def test_validate_label_accepts():
    assert validate_label("EDRAFT") == "EDRAFT"
    assert validate_label("DRAFT2") == "DRAFT2"


@pytest.mark.parametrize("label", ["edraft", "E_DRAFT", "E-DRAFT", "", "GDP"])
def test_validate_label_rejects(label):
    with pytest.raises(ValueError):
        validate_label(label)
