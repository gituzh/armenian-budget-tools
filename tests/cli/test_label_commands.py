"""CLI behaviour for labelled source versions."""

import json
from pathlib import Path

import pandas as pd
import pytest

from armenian_budget.core.utils import list_processed_labels
from armenian_budget.interfaces.cli.main import _select_versions, main

PARSERS_YAML = Path(__file__).resolve().parents[2] / "config" / "parsers.yaml"
WORKBOOK_NAME = "ծրագրեր և միջոցառումներ.xlsx"


def test_select_versions():
    assert _select_versions([None, "A", "B"], None, False) == [None, "A", "B"]
    assert _select_versions(["A"], None, False) == [None, "A"]
    assert _select_versions([], None, False) == [None]
    assert _select_versions([None, "A", "B"], "B", False) == ["B"]
    assert _select_versions([None], "X", False) == ["X"]
    assert _select_versions([None, "A"], None, True) == [None]


def test_list_processed_labels(tmp_path):
    for name in [
        "2026_BUDGET_LAW.csv",
        "2026_BUDGET_LAW_EDRAFT.csv",
        "2026_BUDGET_LAW_DRAFT2.csv",
        "2026_BUDGET_LAW_GDP.json",
        "2026_BUDGET_LAW_EDRAFT_validation.md",
        "2026_BUDGET_LAW_old-copy.csv",
        "2026_SPENDING_Q12.csv",
        "2025_BUDGET_LAW_OTHER.csv",
    ]:
        (tmp_path / name).write_text("x")

    assert list_processed_labels(tmp_path, 2026, "BUDGET_LAW") == [
        None,
        "DRAFT2",
        "EDRAFT",
    ]
    assert list_processed_labels(tmp_path, 2026, "SPENDING_Q1") == []
    assert list_processed_labels(tmp_path, 2026, "SPENDING_Q12") == [None]
    assert list_processed_labels(tmp_path, 2025, "BUDGET_LAW") == ["OTHER"]
    assert list_processed_labels(tmp_path / "missing", 2026, "BUDGET_LAW") == []


# --- process ---------------------------------------------------------------


@pytest.fixture
def stub_parser(monkeypatch):
    """Replace the 2025+ parser; the row records which workbook was parsed."""
    import armenian_budget.ingestion.parsers as parsers_pkg

    def fake_parser(path, source_type=None, year=None):
        df = pd.DataFrame({"source_folder": [Path(path).parent.name]})
        return df, {"overall_total": 1.0}, None, None

    monkeypatch.setattr(parsers_pkg, "flatten_budget_excel_2025", fake_parser)


def _workbook(folder: Path) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / WORKBOOK_NAME
    path.write_bytes(folder.name.encode() * 10_000)
    return path


@pytest.fixture
def tree(tmp_path, stub_parser):
    extracted = tmp_path / "extracted"
    _workbook(extracted / "budget_laws" / "2026")
    _workbook(extracted / "budget_laws" / "2026_EDRAFT")
    processed = tmp_path / "processed"
    return extracted, processed


def _process(extracted, processed, *extra, report=None):
    argv = [
        "process",
        "--years",
        "2026",
        "--source-type",
        "BUDGET_LAW",
        "--extracted-root",
        str(extracted),
        "--processed-root",
        str(processed),
        "--parsers-config",
        str(PARSERS_YAML),
    ]
    if report is not None:
        argv += ["--report-json", str(report)]
    return main(argv + list(extra))


def _names(processed):
    return sorted(p.name for p in processed.iterdir())


UNLABELLED_PAIR = ["2026_BUDGET_LAW.csv", "2026_BUDGET_LAW_overall.json"]
EDRAFT_PAIR = ["2026_BUDGET_LAW_EDRAFT.csv", "2026_BUDGET_LAW_EDRAFT_overall.json"]


def test_process_default_runs_all_versions(tree, tmp_path):
    extracted, processed = tree
    report = tmp_path / "report.json"

    assert _process(extracted, processed, report=report) == 0

    assert _names(processed) == sorted(UNLABELLED_PAIR + EDRAFT_PAIR)
    # each version was parsed from its own folder
    plain = pd.read_csv(processed / "2026_BUDGET_LAW.csv", encoding="utf-8-sig")
    draft = pd.read_csv(processed / "2026_BUDGET_LAW_EDRAFT.csv", encoding="utf-8-sig")
    assert plain["source_folder"].astype(str).tolist() == ["2026"]
    assert draft["source_folder"].tolist() == ["2026_EDRAFT"]
    entries = json.loads(report.read_text("utf-8"))
    assert entries == [
        {"year": 2026, "source": "BUDGET_LAW", "status": "OK", "reason": ""},
        {
            "year": 2026,
            "source": "BUDGET_LAW",
            "status": "OK",
            "reason": "",
            "label": "EDRAFT",
        },
    ]


def test_unlabelled_report_entry_shape_unchanged(tree, tmp_path):
    extracted, processed = tree
    report = tmp_path / "report.json"

    _process(extracted, processed, "--unlabelled", report=report)

    (entry,) = json.loads(report.read_text("utf-8"))
    assert list(entry) == ["year", "source", "status", "reason"]


def test_process_label_runs_one(tree):
    extracted, processed = tree

    assert _process(extracted, processed, "--label", "EDRAFT") == 0

    assert _names(processed) == EDRAFT_PAIR


def test_process_unlabelled_runs_one(tree):
    extracted, processed = tree

    assert _process(extracted, processed, "--unlabelled") == 0

    assert _names(processed) == UNLABELLED_PAIR


def test_process_label_lowercase(tree):
    extracted, processed = tree

    assert _process(extracted, processed, "--label", "edraft") == 0

    assert _names(processed) == EDRAFT_PAIR


def test_process_missing_label_fails(tree, tmp_path):
    extracted, processed = tree
    report = tmp_path / "report.json"

    assert _process(extracted, processed, "--label", "NOPE", report=report) == 1

    (entry,) = json.loads(report.read_text("utf-8"))
    assert entry["status"] == "FAIL"
    assert entry["label"] == "NOPE"
    assert _names(processed) == []


def _process_input(workbook, processed, *extra):
    return main(
        [
            "process",
            "--years",
            "2026",
            "--source-type",
            "BUDGET_LAW",
            "--input",
            str(workbook),
            "--processed-root",
            str(processed),
            *extra,
        ]
    )


def test_process_input_writes_unlabelled_only(tree, tmp_path, monkeypatch):
    _extracted, processed = tree
    # labelled folders exist under the default ./data/extracted too
    monkeypatch.chdir(tmp_path)
    _workbook(tmp_path / "data" / "extracted" / "budget_laws" / "2026_EDRAFT")
    workbook = _workbook(tmp_path / "elsewhere")

    assert _process_input(workbook, processed) == 0

    assert _names(processed) == UNLABELLED_PAIR


def test_process_input_with_label(tree, tmp_path):
    _extracted, processed = tree
    workbook = _workbook(tmp_path / "elsewhere")

    assert _process_input(workbook, processed, "--label", "EDRAFT") == 0

    assert _names(processed) == EDRAFT_PAIR


@pytest.mark.parametrize(
    "command", ["download", "extract", "discover", "process", "validate"]
)
def test_label_and_unlabelled_conflict(command):
    with pytest.raises(SystemExit) as exc:
        main([command, "--years", "2026", "--label", "EDRAFT", "--unlabelled"])

    assert exc.value.code == 2


@pytest.mark.parametrize("label", ["E-DRAFT", "GDP", "e_draft"])
def test_invalid_label_is_rejected(label):
    with pytest.raises(SystemExit) as exc:
        main(["process", "--years", "2026", "--label", label])

    assert exc.value.code == 2


# --- validate --------------------------------------------------------------


def _dataset(processed: Path, stem: str, total: float = 1000.0) -> None:
    processed.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        {
            "state_body": ["State Body 1"],
            "state_body_total": [total],
            "program_code": [1],
            "program_name": ["Program"],
            "program_goal": ["Goal"],
            "program_result_desc": ["Result"],
            "program_total": [total],
            "subprogram_code": [11001],
            "subprogram_name": ["Subprogram"],
            "subprogram_desc": ["Description"],
            "subprogram_type": ["Type"],
            "subprogram_total": [total],
        }
    ).to_csv(processed / f"{stem}.csv", index=False, encoding="utf-8-sig")
    (processed / f"{stem}_overall.json").write_text(
        json.dumps({"overall_total": total}), encoding="utf-8"
    )


def _validate(processed, *extra):
    return main(
        [
            "validate",
            "--years",
            "2026",
            "--source-type",
            "BUDGET_LAW",
            "--processed-root",
            str(processed),
            *extra,
        ]
    )


def test_validate_default_covers_labelled(tmp_path):
    _dataset(tmp_path, "2026_BUDGET_LAW")
    _dataset(tmp_path, "2026_BUDGET_LAW_EDRAFT", total=2000.0)

    _validate(tmp_path, "--report", "--report-json")

    for stem in ["2026_BUDGET_LAW", "2026_BUDGET_LAW_EDRAFT"]:
        markdown = (tmp_path / f"{stem}_validation.md").read_text("utf-8")
        assert f"# Validation Report: {stem}.csv" in markdown
        report = json.loads((tmp_path / f"{stem}_validation.json").read_text("utf-8"))
        assert report["metadata"]["csv_path"] == f"{stem}.csv"
        assert report["metadata"]["overall_path"] == f"{stem}_overall.json"


def test_validate_label_runs_one(tmp_path):
    _dataset(tmp_path, "2026_BUDGET_LAW")
    _dataset(tmp_path, "2026_BUDGET_LAW_EDRAFT")

    _validate(tmp_path, "--label", "edraft", "--report")

    assert (tmp_path / "2026_BUDGET_LAW_EDRAFT_validation.md").exists()
    assert not (tmp_path / "2026_BUDGET_LAW_validation.md").exists()


def test_validate_unlabelled_runs_one(tmp_path):
    _dataset(tmp_path, "2026_BUDGET_LAW")
    _dataset(tmp_path, "2026_BUDGET_LAW_EDRAFT")

    _validate(tmp_path, "--unlabelled", "--report")

    assert (tmp_path / "2026_BUDGET_LAW_validation.md").exists()
    assert not (tmp_path / "2026_BUDGET_LAW_EDRAFT_validation.md").exists()


def test_validate_missing_label(tmp_path, monkeypatch):
    import armenian_budget.interfaces.cli.main as cli

    _dataset(tmp_path, "2026_BUDGET_LAW")
    entries = []
    monkeypatch.setattr(
        cli, "_log_validation_summary", lambda results: entries.extend(results)
    )

    assert _validate(tmp_path, "--label", "NOPE") == 1

    (entry,) = entries
    assert entry["status"] == "MISSING"
    assert entry["label"] == "NOPE"


def test_validate_unlabelled_summary_entry_shape_unchanged(tmp_path, monkeypatch):
    import armenian_budget.interfaces.cli.main as cli

    _dataset(tmp_path, "2026_BUDGET_LAW")
    entries = []
    monkeypatch.setattr(
        cli, "_log_validation_summary", lambda results: entries.extend(results)
    )

    _validate(tmp_path)

    (entry,) = entries
    assert list(entry) == ["year", "source_type", "status", "errors", "warnings"]


# --- download / extract / discover -----------------------------------------


class _FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def raise_for_status(self):
        return None

    def iter_bytes(self, chunk_size=None):
        yield b"archive-bytes"


class _FakeClient:
    def __init__(self, *args, **kwargs):
        pass

    def stream(self, method, url):
        return _FakeResponse()

    def close(self):
        pass


@pytest.fixture
def download_config(tmp_path, monkeypatch):
    from armenian_budget.sources import downloader

    monkeypatch.setattr(downloader.httpx, "Client", _FakeClient)
    config = tmp_path / "config" / "sources.yaml"
    config.parent.mkdir()
    config.write_text(
        """
sources:
  - name: "2026_budget_law"
    year: 2026
    source_type: "budget_law"
    url: "https://example.test/law.rar"
  - name: "2026_budget_law_edraft"
    year: 2026
    source_type: "budget_law"
    label: "EDRAFT"
    url: "https://example.test/edraft.rar"
""",
        encoding="utf-8",
    )
    return config


def _download(config, original, *extra):
    return main(
        [
            "download",
            "--years",
            "2026",
            "--config",
            str(config),
            "--original-root",
            str(original),
            *extra,
        ]
    )


def _files(root):
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*.rar"))


def test_download_uses_label_folder(download_config, tmp_path):
    original = tmp_path / "original"

    assert _download(download_config, original) == 0

    assert _files(original) == [
        "budget_laws/2026/law.rar",
        "budget_laws/2026_EDRAFT/edraft.rar",
    ]


def test_download_label_selects_one(download_config, tmp_path):
    original = tmp_path / "original"

    assert _download(download_config, original, "--label", "EDRAFT") == 0

    assert _files(original) == ["budget_laws/2026_EDRAFT/edraft.rar"]


def test_download_unlabelled_selects_one(download_config, tmp_path):
    original = tmp_path / "original"

    assert _download(download_config, original, "--unlabelled") == 0

    assert _files(original) == ["budget_laws/2026/law.rar"]


def test_extract_label_selects_one(tmp_path):
    import zipfile

    original = tmp_path / "original"
    extracted = tmp_path / "extracted"
    for folder, name in [("2026", "a"), ("2026_EDRAFT", "b")]:
        target = original / "budget_laws" / folder
        target.mkdir(parents=True)
        with zipfile.ZipFile(target / f"{name}.zip", "w") as zf:
            zf.writestr(f"{name}.txt", "x")
    base = ["extract", "--years", "2026", "--source-type", "BUDGET_LAW"]
    roots = ["--original-root", str(original), "--extracted-root", str(extracted)]

    assert main(base + roots + ["--label", "EDRAFT"]) == 0
    out = extracted / "budget_laws"
    assert (out / "2026_EDRAFT" / "b" / "b.txt").exists()
    assert not (out / "2026").exists()

    # a label with no folder creates nothing
    assert main(base + roots + ["--label", "NOPE"]) == 0
    assert not (out / "2026_NOPE").exists()

    assert main(base + roots + ["--unlabelled"]) == 0
    assert (out / "2026" / "a" / "a.txt").exists()


def test_discover_covers_labelled_versions(tmp_path):
    extracted = tmp_path / "extracted"
    _workbook(extracted / "budget_laws" / "2026")
    _workbook(extracted / "budget_laws" / "2026_EDRAFT")
    argv = [
        "discover",
        "--years",
        "2026",
        "--source-type",
        "BUDGET_LAW",
        "--extracted-root",
        str(extracted),
        "--parsers-config",
        str(PARSERS_YAML),
    ]

    assert main(argv) == 0
    index = json.loads((extracted / "discovery_index.json").read_text("utf-8"))
    assert set(index) == {"2026/budget_law", "2026/budget_law/EDRAFT"}

    assert main(argv + ["--label", "NOPE"]) == 1
