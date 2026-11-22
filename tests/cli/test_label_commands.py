"""CLI behaviour for labelled source versions."""

import io
import json
import logging
import zipfile
from pathlib import Path

import pandas as pd
import pytest

from armenian_budget.core.utils import list_processed_labels
from armenian_budget.interfaces.cli.main import _select_versions, main

PARSERS_YAML = Path(__file__).resolve().parents[2] / "config" / "parsers.yaml"
# A sources file that does not exist: only the unlabelled version is known
NO_CONFIG = Path(__file__).resolve().parent / "no-such-sources.yaml"
WORKBOOK_NAME = "ծրագրեր և միջոցառումներ.xlsx"
CLI_LOGGER = "armenian_budget.interfaces.cli.main"


@pytest.fixture
def warnings_log():
    """Warnings of the CLI module; main() resets root handlers, so not caplog."""
    messages: list[str] = []

    class _Collect(logging.Handler):
        def emit(self, record):
            if record.levelno >= logging.WARNING:
                messages.append(record.getMessage())

    handler = _Collect()
    logging.getLogger(CLI_LOGGER).addHandler(handler)
    yield messages
    logging.getLogger(CLI_LOGGER).removeHandler(handler)


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
    _sources(tmp_path)
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
    if "--config" not in extra:
        # the registry the tree fixture wrote next to the roots, if any
        config = extracted.parent / "sources.yaml"
        argv += ["--config", str(config if config.exists() else NO_CONFIG)]
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
    config = [] if "--config" in extra else ["--config", str(NO_CONFIG)]
    return main(
        [
            "validate",
            "--years",
            "2026",
            "--source-type",
            "BUDGET_LAW",
            "--processed-root",
            str(processed),
            *config,
            *extra,
        ]
    )


REGISTERED = """
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
  - name: "2025_budget_law_other"
    year: 2025
    source_type: "budget_law"
    label: "OTHERYEAR"
    url: "https://example.test/other.rar"
"""


def _sources(tmp_path, text=REGISTERED):
    config = tmp_path / "sources.yaml"
    config.write_text(text, encoding="utf-8")
    return config


def test_process_reports_registered_version_missing_on_disk(tmp_path, stub_parser):
    # A version that is in the config must never silently produce nothing
    extracted = tmp_path / "extracted"
    _workbook(extracted / "budget_laws" / "2026")
    processed = tmp_path / "processed"
    report = tmp_path / "report.json"

    exit_code = _process(
        extracted, processed, "--config", str(_sources(tmp_path)), report=report
    )

    assert exit_code == 0
    assert _names(processed) == UNLABELLED_PAIR
    plain, draft = json.loads(report.read_text("utf-8"))
    assert plain == {"year": 2026, "source": "BUDGET_LAW", "status": "OK", "reason": ""}
    assert (draft["status"], draft["label"]) == ("FAIL", "EDRAFT")
    assert draft["reason"].startswith("discovery:")


def _ignoring(folder: Path, label: str, year: int = 2026) -> str:
    return f"Ignoring {folder}: {label} is not registered for {year} in sources.yaml"


def test_unregistered_label_folder_is_ignored(tree, tmp_path, warnings_log):
    extracted, processed = tree
    plain_report = tmp_path / "plain_report.json"
    plain_exit = _process(extracted, tmp_path / "plain", report=plain_report)
    parliament = extracted / "budget_laws" / "2026_PARLIAMENT"
    _workbook(parliament)
    report = tmp_path / "report.json"

    exit_code = _process(extracted, processed, report=report)

    assert _names(processed) == sorted(UNLABELLED_PAIR + EDRAFT_PAIR)
    assert warnings_log.count(_ignoring(parliament.resolve(), "PARLIAMENT")) == 1
    # not a failure: no report entry for it, and the exit code is unchanged
    entries = json.loads(report.read_text("utf-8"))
    assert "PARLIAMENT" not in [e.get("label") for e in entries]
    assert entries == json.loads(plain_report.read_text("utf-8"))
    assert exit_code == plain_exit == 0


def test_unregistered_folder_warned_once_for_shared_category(tree, warnings_log):
    # four spending source types read the same folder: still one warning
    extracted, processed = tree
    stray = extracted / "spending_reports" / "2026_STRAY"
    _workbook(stray)

    main(
        [
            "process",
            "--years",
            "2026",
            "--extracted-root",
            str(extracted),
            "--processed-root",
            str(processed),
            "--parsers-config",
            str(PARSERS_YAML),
            "--config",
            str(extracted.parent / "sources.yaml"),
        ]
    )

    assert warnings_log.count(_ignoring(stray.resolve(), "STRAY")) == 1


def test_process_reads_only_its_own_categories(tree, warnings_log):
    # the run reads budget laws only: it never looks in the spending folder
    extracted, processed = tree
    _workbook(extracted / "spending_reports" / "2026_STRAY")

    _process(extracted, processed)

    assert not [m for m in warnings_log if m.startswith("Ignoring")]


def test_process_ignores_invalid_config(tree, tmp_path):
    # process never read sources.yaml before labels; a broken one must not stop it
    extracted, processed = tree
    config = _sources(tmp_path, REGISTERED.replace('"EDRAFT"', '"bad-label"'))

    assert _process(extracted, processed, "--config", str(config)) == 0

    assert _names(processed) == UNLABELLED_PAIR


def test_invalid_registry_runs_unlabelled_only(tree, tmp_path, warnings_log):
    extracted, processed = tree
    config = _sources(tmp_path, REGISTERED.replace('"EDRAFT"', '"bad-label"'))

    assert _process(extracted, processed, "--config", str(config)) == 0

    assert _names(processed) == UNLABELLED_PAIR
    assert [m for m in warnings_log if "labelled versions are not run" in m]
    extra = ["--config", str(config), "--label", "EDRAFT"]
    assert _process(extracted, processed, *extra) == 1


def test_missing_registry_runs_unlabelled_only(tree, warnings_log):
    extracted, processed = tree

    assert _process(extracted, processed, "--config", str(NO_CONFIG)) == 0

    assert _names(processed) == UNLABELLED_PAIR
    assert [m for m in warnings_log if "labelled versions are not run" in m]
    extra = ["--config", str(NO_CONFIG), "--label", "EDRAFT"]
    assert _process(extracted, processed, *extra) == 1


def test_input_needs_no_registry(tree, tmp_path, warnings_log):
    _extracted, processed = tree
    workbook = _workbook(tmp_path / "elsewhere")

    exit_code = _process_input(workbook, processed, "--config", "/nonexistent.yaml")

    assert exit_code == 0
    assert _names(processed) == UNLABELLED_PAIR
    assert not [m for m in warnings_log if "sources config" in m.lower()]


def test_input_ignores_registered_labels(tree, tmp_path):
    _extracted, processed = tree
    workbook = _workbook(tmp_path / "elsewhere")
    registry = tmp_path / "sources.yaml"  # written by the tree fixture: EDRAFT, 2026
    assert "EDRAFT" in registry.read_text(encoding="utf-8")

    assert _process_input(workbook, processed, "--config", str(registry)) == 0

    assert _names(processed) == UNLABELLED_PAIR


def test_input_does_not_read_invalid_registry(tree, tmp_path, warnings_log):
    _extracted, processed = tree
    workbook = _workbook(tmp_path / "elsewhere")
    bad = tmp_path / "bad.yaml"
    bad.write_text("sources: [ : :\n", encoding="utf-8")

    assert _process_input(workbook, processed, "--config", str(bad)) == 0

    assert _names(processed) == UNLABELLED_PAIR
    assert not [m for m in warnings_log if "sources config" in m.lower()]


def test_validate_reports_registered_version_missing(tmp_path, monkeypatch):
    import armenian_budget.interfaces.cli.main as cli

    processed = tmp_path / "processed"
    _dataset(processed, "2026_BUDGET_LAW")
    without_config = _validate(processed)
    entries = []
    monkeypatch.setattr(
        cli, "_log_validation_summary", lambda results: entries.extend(results)
    )

    exit_code = _validate(processed, "--config", str(_sources(tmp_path)))

    assert exit_code == without_config
    assert [(e["status"] == "MISSING", e.get("label")) for e in entries] == [
        (False, None),
        (True, "EDRAFT"),
    ]


def test_validate_ignores_invalid_config(tmp_path):
    processed = tmp_path / "processed"
    _dataset(processed, "2026_BUDGET_LAW")
    config = _sources(tmp_path, REGISTERED.replace('"EDRAFT"', '"bad-label"'))

    assert _validate(processed, "--config", str(config)) == _validate(processed)


def test_validate_default_covers_labelled(tmp_path):
    _dataset(tmp_path, "2026_BUDGET_LAW")
    _dataset(tmp_path, "2026_BUDGET_LAW_EDRAFT", total=2000.0)
    config = _sources(tmp_path)

    _validate(tmp_path, "--config", str(config), "--report", "--report-json")

    for stem in ["2026_BUDGET_LAW", "2026_BUDGET_LAW_EDRAFT"]:
        markdown = (tmp_path / f"{stem}_validation.md").read_text("utf-8")
        assert f"# Validation Report: {stem}.csv" in markdown
        report = json.loads((tmp_path / f"{stem}_validation.json").read_text("utf-8"))
        assert report["metadata"]["csv_path"] == f"{stem}.csv"
        assert report["metadata"]["overall_path"] == f"{stem}_overall.json"


def test_validate_label_runs_one(tmp_path):
    _dataset(tmp_path, "2026_BUDGET_LAW")
    _dataset(tmp_path, "2026_BUDGET_LAW_EDRAFT")
    config = _sources(tmp_path)

    _validate(tmp_path, "--config", str(config), "--label", "edraft", "--report")

    assert (tmp_path / "2026_BUDGET_LAW_EDRAFT_validation.md").exists()
    assert not (tmp_path / "2026_BUDGET_LAW_validation.md").exists()


def test_validate_ignores_unregistered_csv(tmp_path):
    _dataset(tmp_path, "2026_BUDGET_LAW")
    _dataset(tmp_path, "2026_BUDGET_LAW_EDRAFT")
    _dataset(tmp_path, "2026_BUDGET_LAW_STRAYCOPY")  # same bytes, not registered
    config = _sources(tmp_path)

    exit_code = _validate(
        tmp_path, "--config", str(config), "--report", "--report-json"
    )

    assert exit_code == 0
    assert not list(tmp_path.glob("*STRAYCOPY_validation*"))
    for suffix in ("md", "json"):
        report = (tmp_path / f"2026_BUDGET_LAW_validation.{suffix}").read_text("utf-8")
        assert "EDRAFT" in report
        assert "STRAYCOPY" not in report


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
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zf:
            zf.writestr("inside.txt", "x")
        yield buffer.getvalue()


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


def test_download_extract_stays_in_own_category(tmp_path, monkeypatch):
    # A budget-law draft must not create spending or MTEP version folders
    from armenian_budget.sources import downloader

    monkeypatch.setattr(downloader.httpx, "Client", _FakeClient)
    config = tmp_path / "sources.yaml"
    config.write_text(
        """
sources:
  - name: "2026_budget_law_edraft"
    year: 2026
    source_type: "budget_law"
    label: "EDRAFT"
    url: "https://example.test/edraft.zip"
""",
        encoding="utf-8",
    )
    original = tmp_path / "original"
    extracted = tmp_path / "extracted"

    exit_code = _download(
        config, original, "--extract", "--extracted-root", str(extracted)
    )

    assert exit_code == 0
    assert (extracted / "budget_laws/2026_EDRAFT/edraft/inside.txt").exists()
    assert sorted(p.name for p in extracted.iterdir()) == ["budget_laws"]
    assert sorted(p.name for p in original.iterdir()) == ["budget_laws"]


def _original_zips(original: Path, *folders: tuple[str, str]) -> None:
    for folder, name in folders:
        target = original / "budget_laws" / folder
        target.mkdir(parents=True)
        with zipfile.ZipFile(target / f"{name}.zip", "w") as zf:
            zf.writestr(f"{name}.txt", "x")


def test_extract_label_selects_one(tmp_path):
    original = tmp_path / "original"
    extracted = tmp_path / "extracted"
    _original_zips(original, ("2026", "a"), ("2026_EDRAFT", "b"), ("2026_NOPE", "c"))
    config = _sources(tmp_path)
    base = ["extract", "--years", "2026", "--source-type", "BUDGET_LAW"]
    roots = [
        "--original-root",
        str(original),
        "--extracted-root",
        str(extracted),
        "--config",
        str(config),
    ]

    assert main(base + roots + ["--label", "EDRAFT"]) == 0
    out = extracted / "budget_laws"
    assert (out / "2026_EDRAFT" / "b" / "b.txt").exists()
    assert not (out / "2026").exists()

    # a label that is not registered extracts nothing, even with a folder
    assert main(base + roots + ["--label", "NOPE"]) == 1
    assert not (out / "2026_NOPE").exists()

    assert main(base + roots + ["--unlabelled"]) == 0
    assert (out / "2026" / "a" / "a.txt").exists()


def test_extract_default_skips_unregistered_folder(tmp_path, warnings_log):
    original = tmp_path / "original"
    extracted = tmp_path / "extracted"
    _original_zips(original, ("2026", "a"), ("2026_EDRAFT", "b"), ("2026_NOPE", "c"))
    argv = [
        "extract",
        "--years",
        "2026",
        "--original-root",
        str(original),
        "--extracted-root",
        str(extracted),
        "--config",
        str(_sources(tmp_path)),
    ]

    assert main(argv) == 0

    out = extracted / "budget_laws"
    assert sorted(p.name for p in out.iterdir()) == ["2026", "2026_EDRAFT"]
    nope = (original / "budget_laws" / "2026_NOPE").resolve()
    assert warnings_log.count(_ignoring(nope, "NOPE")) == 1


def test_extract_no_empty_unlabelled_folder(tmp_path):
    # 2027 has only a labelled version: no empty extracted/budget_laws/2027
    original = tmp_path / "original"
    extracted = tmp_path / "extracted"
    _original_zips(original, ("2027_DRAFT", "d"))
    config = _sources(
        tmp_path,
        REGISTERED.replace("2026", "2027").replace("EDRAFT", "DRAFT").replace(
            "edraft", "draft"
        ),
    )

    exit_code = main(
        [
            "extract",
            "--original-root",
            str(original),
            "--extracted-root",
            str(extracted),
            "--config",
            str(config),
        ]
    )

    assert exit_code == 0
    out = extracted / "budget_laws"
    assert (out / "2027_DRAFT" / "d" / "d.txt").exists()
    assert not (out / "2027").exists()


def test_extract_year_without_original_folder_creates_nothing(tmp_path):
    original = tmp_path / "original"
    extracted = tmp_path / "extracted"
    _original_zips(original, ("2026", "a"))
    argv = [
        "extract",
        "--years",
        "2025",
        "--original-root",
        str(original),
        "--extracted-root",
        str(extracted),
        "--config",
        str(_sources(tmp_path)),
    ]

    assert main(argv) == 0

    assert not any(p.name.startswith("2025") for p in extracted.rglob("*"))


def test_extract_registered_label_without_original_folder_fails(tmp_path):
    original = tmp_path / "original"
    extracted = tmp_path / "extracted"
    _original_zips(original, ("2026", "a"))
    argv = [
        "extract",
        "--years",
        "2026",
        "--label",
        "EDRAFT",
        "--original-root",
        str(original),
        "--extracted-root",
        str(extracted),
        "--config",
        str(_sources(tmp_path)),
    ]

    assert main(argv) == 1

    assert not (extracted / "budget_laws" / "2026_EDRAFT").exists()


def test_discover_covers_labelled_versions(tmp_path):
    extracted = tmp_path / "extracted"
    _workbook(extracted / "budget_laws" / "2026")
    _workbook(extracted / "budget_laws" / "2026_EDRAFT")
    _workbook(extracted / "budget_laws" / "2026_NOPE")
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
        "--config",
        str(_sources(tmp_path)),
    ]

    assert main(argv) == 0
    index = json.loads((extracted / "discovery_index.json").read_text("utf-8"))
    assert set(index) == {"2026/budget_law", "2026/budget_law/EDRAFT"}

    assert main(argv + ["--label", "NOPE"]) == 1


def test_discover_warns_for_unregistered_folder(tmp_path, warnings_log):
    extracted = tmp_path / "extracted"
    _workbook(extracted / "budget_laws" / "2026")
    nope = _workbook(extracted / "budget_laws" / "2026_NOPE").parent

    main(
        [
            "discover",
            "--years",
            "2026",
            "--source-type",
            "BUDGET_LAW",
            "--extracted-root",
            str(extracted),
            "--parsers-config",
            str(PARSERS_YAML),
            "--config",
            str(_sources(tmp_path)),
        ]
    )

    assert warnings_log.count(_ignoring(nope.resolve(), "NOPE")) == 1


@pytest.mark.parametrize(
    "command", ["download", "extract", "discover", "process", "validate", "gdp-extract"]
)
def test_label_not_registered_fails_everywhere(command, tmp_path, stub_parser):
    # a folder or CSV with the label exists, but sources.yaml has no entry
    config = _sources(tmp_path)
    original = tmp_path / "original"
    extracted = tmp_path / "extracted"
    processed = tmp_path / "processed"
    _original_zips(original, ("2026_NOPE", "c"))
    _workbook(extracted / "budget_laws" / "2026_NOPE")
    _dataset(processed, "2026_BUDGET_LAW_NOPE")
    argv = {
        "download": ["--original-root", str(original)],
        "extract": [
            "--original-root",
            str(original),
            "--extracted-root",
            str(extracted),
        ],
        "discover": [
            "--extracted-root",
            str(extracted),
            "--parsers-config",
            str(PARSERS_YAML),
        ],
        "process": [
            "--extracted-root",
            str(extracted),
            "--processed-root",
            str(processed),
            "--parsers-config",
            str(PARSERS_YAML),
        ],
        "validate": ["--processed-root", str(processed)],
        "gdp-extract": [
            "--original-root",
            str(original),
            "--extracted-root",
            str(extracted),
            "--processed-root",
            str(processed),
        ],
    }[command]

    exit_code = main(
        [command, "--years", "2026", "--label", "NOPE", "--config", str(config)] + argv
    )

    assert exit_code != 0
