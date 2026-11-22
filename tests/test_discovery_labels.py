import json
from pathlib import Path

import pytest

from armenian_budget.ingestion.discovery import discover_best_file

PARSERS_YAML = Path(__file__).resolve().parents[1] / "config" / "parsers.yaml"
# Matches the global budget-law pattern in config/parsers.yaml
WORKBOOK_NAME = "ծրագրեր և միջոցառումներ.xlsx"


def _workbook(folder: Path, fill: bytes) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / WORKBOOK_NAME
    path.write_bytes(fill * 30_000)
    return path


def _discover(extracted: Path, label=None) -> Path:
    return discover_best_file(
        extracted_root=extracted,
        year=2026,
        source_type="BUDGET_LAW",
        parsers_config_path=PARSERS_YAML,
        label=label,
    )


def test_unlabelled_discovery_ignores_labelled_folder(tmp_path):
    _workbook(tmp_path / "budget_laws" / "2026_EDRAFT" / "annexes", b"e")

    with pytest.raises(FileNotFoundError):
        _discover(tmp_path)


def test_labelled_discovery_ignores_unlabelled_folder(tmp_path):
    _workbook(tmp_path / "budget_laws" / "2026" / "annexes", b"u")

    with pytest.raises(FileNotFoundError):
        _discover(tmp_path, "EDRAFT")


def test_labelled_discovery_ignores_other_label(tmp_path):
    _workbook(tmp_path / "budget_laws" / "2026_EDRAFT2" / "annexes", b"x")

    with pytest.raises(FileNotFoundError):
        _discover(tmp_path, "EDRAFT")


def test_each_version_gets_its_own_workbook_and_key(tmp_path):
    unlabelled = _workbook(tmp_path / "budget_laws" / "2026" / "annexes", b"u")
    labelled = _workbook(tmp_path / "budget_laws" / "2026_EDRAFT" / "annexes", b"e")

    assert _discover(tmp_path) == unlabelled.resolve()
    assert _discover(tmp_path, "EDRAFT") == labelled.resolve()
    # cached lookups stay separate too
    assert _discover(tmp_path) == unlabelled.resolve()
    assert _discover(tmp_path, "EDRAFT") == labelled.resolve()

    index = json.loads((tmp_path / "discovery_index.json").read_text("utf-8"))
    assert set(index) == {"2026/budget_law", "2026/budget_law/EDRAFT"}
    assert index["2026/budget_law"]["path"].startswith("budget_laws/2026/")
    assert index["2026/budget_law/EDRAFT"]["path"].startswith(
        "budget_laws/2026_EDRAFT/"
    )
    assert index["2026/budget_law/EDRAFT"]["key"] == "2026/budget_law/EDRAFT"
