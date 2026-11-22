"""GDP extraction for labelled budget-law versions (synthetic documents)."""

import json
import logging
from pathlib import Path
from zipfile import ZipFile

import pytest

from armenian_budget.ingestion.gdp_indicators import (
    extract_gdp_snapshot,
    find_budget_law_explanatory_note_docx,
    gdp_snapshot_path,
    write_gdp_snapshot,
)
from armenian_budget.interfaces.cli.main import main

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _docx(path: Path, nominal_gdp: str) -> Path:
    """Write a DOCX holding one budget-message GDP table."""
    rows = [
        ["Հիմնական մակրոտնտեսական ցուցանիշներ", "2025", "2026"],
        ["Անվանական ՀՆԱ, մլրդ դրամ", "10,000.0", nominal_gdp],
        ["Տնտեսական աճ, %", "5.0", "5.4"],
    ]
    table = "".join(
        "<w:tr>"
        + "".join(f"<w:tc><w:p><w:r><w:t>{c}</w:t></w:r></w:p></w:tc>" for c in row)
        + "</w:tr>"
        for row in rows
    )
    xml = (
        f'<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="{W}">'
        f"<w:body><w:tbl>{table}</w:tbl></w:body></w:document>"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", xml)
    return path


CONFIG = """
sources:
  - name: "2026_budget_law_edraft"
    year: 2026
    source_type: "budget_law"
    label: "EDRAFT"
    files:
      - name: "2026_budget_law_edraft_attachments"
        url: "https://example.test/edraft.rar"
      - name: "2026_budget_law_edraft_explanatory_note"
        url: "https://example.test/ajax?file_id=1"
        filename: "draft.docx"
  - name: "2026_budget_law_parliament"
    year: 2026
    source_type: "budget_law"
    label: "PARLIAMENT"
    files:
      - name: "2026_budget_law_parliament_attachments"
        url: "https://example.test/parliament.rar"
  - name: "2026_budget_law"
    year: 2026
    source_type: "budget_law"
    files:
      - name: "2026_budget_law_attachments"
        url: "https://example.test/law.rar"
      - name: "2026_budget_law_explanatory_note"
        url: "https://example.test/final.docx"
"""


@pytest.fixture
def roots(tmp_path):
    config = tmp_path / "sources.yaml"
    config.write_text(CONFIG, encoding="utf-8")
    original = tmp_path / "original"
    extracted = tmp_path / "extracted"
    extracted.mkdir()
    _docx(original / "budget_laws" / "2026" / "final.docx", "11,933.7")
    _docx(original / "budget_laws" / "2026_EDRAFT" / "draft.docx", "11,900.0")
    return original, extracted, config


def _nominal_2026(snapshot):
    (value,) = [
        r["value"]
        for r in snapshot["tables"][0]["records"]
        if r["indicator"] == "Անվանական ՀՆԱ" and r["target_year"] == 2026
    ]
    return value


def test_gdp_snapshot_path_with_label(tmp_path):
    assert gdp_snapshot_path(tmp_path, 2026, "budget_law", "EDRAFT") == (
        tmp_path / "2026_BUDGET_LAW_EDRAFT_GDP.json"
    )
    assert gdp_snapshot_path(tmp_path, 2026, "budget_law") == (
        tmp_path / "2026_BUDGET_LAW_GDP.json"
    )


def test_note_lookup_is_per_label(roots):
    original, extracted, config = roots

    # the EDRAFT entry is listed first; the unlabelled lookup must not take it
    assert find_budget_law_explanatory_note_docx(original, extracted, config, 2026) == (
        original / "budget_laws" / "2026" / "final.docx"
    )
    assert find_budget_law_explanatory_note_docx(
        original, extracted, config, 2026, label="EDRAFT"
    ) == (original / "budget_laws" / "2026_EDRAFT" / "draft.docx")


def test_labelled_lookup_never_falls_back(roots):
    original, extracted, config = roots
    (original / "budget_laws" / "2026_EDRAFT" / "draft.docx").unlink()
    # a recognisable budget message elsewhere must not be picked up either
    _docx(original / "budget_laws" / "2026" / "բյուջետային ուղերձ.docx", "1.0")

    with pytest.raises(FileNotFoundError):
        find_budget_law_explanatory_note_docx(
            original, extracted, config, 2026, label="EDRAFT"
        )


def test_labelled_lookup_ignores_unregistered_docx_in_own_folder(roots):
    original, extracted, config = roots
    _docx(original / "budget_laws" / "2026_PARLIAMENT" / "ուղերձ.docx", "1.0")

    with pytest.raises(FileNotFoundError):
        find_budget_law_explanatory_note_docx(
            original, extracted, config, 2026, label="PARLIAMENT"
        )


def _snapshot(roots, label=None):
    original, extracted, config = roots
    return extract_gdp_snapshot(
        year=2026,
        source_type="BUDGET_LAW",
        original_root=original,
        extracted_root=extracted,
        sources_config=config,
        label=label,
    )


def test_labelled_snapshot_records_label(roots, tmp_path):
    snapshot = _snapshot(roots, "EDRAFT")

    assert snapshot["label"] == "EDRAFT"
    assert snapshot["source_file"] == "draft.docx"
    assert _nominal_2026(snapshot) == 11900.0
    path = write_gdp_snapshot(snapshot, tmp_path / "processed")
    assert path.name == "2026_BUDGET_LAW_EDRAFT_GDP.json"


def test_unlabelled_snapshot_has_no_label_key(roots, tmp_path):
    snapshot = _snapshot(roots)

    assert list(snapshot) == [
        "year",
        "source_type",
        "metric_set",
        "source_file",
        "tables",
    ]
    assert snapshot["source_file"] == "final.docx"
    assert _nominal_2026(snapshot) == 11933.7
    path = write_gdp_snapshot(snapshot, tmp_path / "processed")
    assert path.name == "2026_BUDGET_LAW_GDP.json"


def _gdp_extract(roots, processed, *extra):
    original, extracted, config = roots
    return main(
        [
            "gdp-extract",
            "--years",
            "2026",
            "--source-type",
            "BUDGET_LAW",
            "--config",
            str(config),
            "--original-root",
            str(original),
            "--extracted-root",
            str(extracted),
            "--processed-root",
            str(processed),
            *extra,
        ]
    )


def _names(processed):
    return sorted(p.name for p in processed.iterdir()) if processed.exists() else []


def test_gdp_extract_default_covers_labelled(roots, tmp_path):
    processed = tmp_path / "processed"

    # PARLIAMENT has no budget message: skipped, not a failure
    assert _gdp_extract(roots, processed) == 0

    assert _names(processed) == [
        "2026_BUDGET_LAW_EDRAFT_GDP.json",
        "2026_BUDGET_LAW_GDP.json",
    ]
    draft = json.loads(
        (processed / "2026_BUDGET_LAW_EDRAFT_GDP.json").read_text("utf-8")
    )
    final = json.loads((processed / "2026_BUDGET_LAW_GDP.json").read_text("utf-8"))
    assert (_nominal_2026(draft), _nominal_2026(final)) == (11900.0, 11933.7)


def test_gdp_extract_label(roots, tmp_path):
    processed = tmp_path / "processed"

    assert _gdp_extract(roots, processed, "--label", "edraft") == 0

    assert _names(processed) == ["2026_BUDGET_LAW_EDRAFT_GDP.json"]


def test_gdp_extract_unlabelled(roots, tmp_path):
    processed = tmp_path / "processed"

    assert _gdp_extract(roots, processed, "--unlabelled") == 0

    assert _names(processed) == ["2026_BUDGET_LAW_GDP.json"]


def test_gdp_extract_skips_version_without_note(roots, tmp_path):
    processed = tmp_path / "processed"

    assert _gdp_extract(roots, processed) == 0

    assert "2026_BUDGET_LAW_PARLIAMENT_GDP.json" not in _names(processed)


def test_gdp_extract_only_version_without_note_exits_1(roots, tmp_path):
    processed = tmp_path / "processed"

    # only a version without a budget message was asked for: nothing extracted
    assert _gdp_extract(roots, processed, "--label", "PARLIAMENT") == 1
    assert _names(processed) == []


def test_gdp_extract_skips_absent_unlabelled_version(tmp_path):
    config = tmp_path / "sources.yaml"
    config.write_text(
        CONFIG.replace("2026", "2027").split('  - name: "2027_budget_law_parliament"')[0],
        encoding="utf-8",
    )
    original = tmp_path / "original"
    extracted = tmp_path / "extracted"
    extracted.mkdir()
    _docx(original / "budget_laws" / "2027_EDRAFT" / "draft.docx", "12,000.0")
    processed = tmp_path / "processed"
    messages: list[str] = []

    class _Collect(logging.Handler):
        def emit(self, record):
            if record.levelno >= logging.INFO:
                messages.append(f"{record.levelname} {record.getMessage()}")

    handler = _Collect()
    cli_logger = logging.getLogger("armenian_budget.interfaces.cli.main")
    cli_logger.addHandler(handler)
    try:
        exit_code = main(
            [
                "gdp-extract",
                "--years",
                "2027",
                "--source-type",
                "BUDGET_LAW",
                "--config",
                str(config),
                "--original-root",
                str(original),
                "--extracted-root",
                str(extracted),
                "--processed-root",
                str(processed),
            ]
        )
    finally:
        cli_logger.removeHandler(handler)

    assert exit_code == 0
    assert _names(processed) == ["2027_BUDGET_LAW_EDRAFT_GDP.json"]
    skip = (
        "INFO 2027 BUDGET_LAW: unlabelled version skipped: "
        "not registered in sources.yaml and no data on disk"
    )
    assert messages.count(skip) == 1
    assert not [m for m in messages if m.startswith("WARNING")]


def test_gdp_extract_explicit_unlabelled_is_not_skipped(tmp_path, capsys):
    config = tmp_path / "sources.yaml"
    config.write_text(
        CONFIG.replace("2026", "2027").split('  - name: "2027_budget_law_parliament"')[0],
        encoding="utf-8",
    )
    original = tmp_path / "original"
    extracted = tmp_path / "extracted"
    extracted.mkdir()
    _docx(original / "budget_laws" / "2027_EDRAFT" / "draft.docx", "12,000.0")
    processed = tmp_path / "processed"

    exit_code = main(
        [
            "gdp-extract",
            "--years",
            "2027",
            "--source-type",
            "BUDGET_LAW",
            "--unlabelled",
            "--config",
            str(config),
            "--original-root",
            str(original),
            "--extracted-root",
            str(extracted),
            "--processed-root",
            str(processed),
        ]
    )

    err = capsys.readouterr().err
    assert exit_code == 1
    assert _names(processed) == []
    assert "unlabelled version skipped" not in err
    assert "2027 BUDGET_LAW: budget-law explanatory note DOCX not found" in err


def test_gdp_extract_label_not_registered(roots, tmp_path):
    original, _extracted, _config = roots
    _docx(original / "budget_laws" / "2026_NOPE" / "draft.docx", "1.0")
    processed = tmp_path / "processed"
    messages: list[str] = []

    class _Collect(logging.Handler):
        def emit(self, record):
            messages.append(record.getMessage())

    handler = _Collect()
    cli_logger = logging.getLogger("armenian_budget.interfaces.cli.main")
    cli_logger.addHandler(handler)
    try:
        exit_code = _gdp_extract(roots, processed, "--label", "NOPE")
    finally:
        cli_logger.removeHandler(handler)

    assert exit_code == 1
    assert _names(processed) == []
    assert any(
        "NOPE is not registered for 2026 BUDGET_LAW in sources.yaml" in m
        for m in messages
    )
    assert not any("no budget message" in m for m in messages)


def test_gdp_extract_invalid_config_warns_once_per_run(roots, tmp_path):
    original, extracted, _config = roots
    bad = tmp_path / "bad.yaml"
    bad.write_text("sources: [ : :\n", encoding="utf-8")
    messages: list[str] = []

    class _Collect(logging.Handler):
        def emit(self, record):
            if record.levelno >= logging.WARNING:
                messages.append(record.getMessage())

    handler = _Collect()
    cli_logger = logging.getLogger("armenian_budget.interfaces.cli.main")
    cli_logger.addHandler(handler)
    try:
        main(
            [
                "gdp-extract",
                "--years",
                "2026-2027",
                "--source-type",
                "BUDGET_LAW",
                "--config",
                str(bad),
                "--original-root",
                str(original),
                "--extracted-root",
                str(extracted),
                "--processed-root",
                str(tmp_path / "processed"),
            ]
        )
    finally:
        cli_logger.removeHandler(handler)

    config_warnings = [m for m in messages if str(bad) in m]
    assert len(config_warnings) == 1
    assert "labelled versions are not run" in config_warnings[0]


def test_gdp_extract_registered_note_missing_on_disk_fails(roots, tmp_path):
    original, _extracted, _config = roots
    (original / "budget_laws" / "2026_EDRAFT" / "draft.docx").unlink()
    processed = tmp_path / "processed"

    assert _gdp_extract(roots, processed) == 1

    assert _names(processed) == ["2026_BUDGET_LAW_GDP.json"]


def test_gdp_extract_label_leaves_spending_alone(roots, tmp_path):
    original, extracted, config = roots
    processed = tmp_path / "processed"

    exit_code = main(
        [
            "gdp-extract",
            "--years",
            "2026",
            "--label",
            "EDRAFT",
            "--config",
            str(config),
            "--original-root",
            str(original),
            "--extracted-root",
            str(extracted),
            "--processed-root",
            str(processed),
        ]
    )

    # no failure is counted for the annual spending report, which has no labels
    assert exit_code == 0
    assert _names(processed) == ["2026_BUDGET_LAW_EDRAFT_GDP.json"]


def test_gdp_extract_spending_does_not_need_a_valid_config(roots, tmp_path):
    # the annual spending report has no labels and never read sources.yaml
    original, extracted, config = roots
    config.write_text(CONFIG.replace('"EDRAFT"', '"bad-label"'), encoding="utf-8")

    exit_code = main(
        [
            "gdp-extract",
            "--years",
            "2026",
            "--source-type",
            "SPENDING_Q1234",
            "--config",
            str(config),
            "--original-root",
            str(original),
            "--extracted-root",
            str(extracted),
            "--processed-root",
            str(tmp_path / "processed"),
        ]
    )

    # 1: nothing extracted (no report on disk); 3 would be a config load error
    assert exit_code == 1


@pytest.mark.parametrize("place", ["original", "extracted"])
def test_gdp_extract_unlabelled_data_in_either_place_is_attempted(
    place, tmp_path, capsys
):
    config = tmp_path / "sources.yaml"
    config.write_text(
        CONFIG.replace("2026", "2027").split('  - name: "2027_budget_law_parliament"')[0],
        encoding="utf-8",
    )
    original = tmp_path / "original"
    extracted = tmp_path / "extracted"
    extracted.mkdir()
    _docx(original / "budget_laws" / "2027_EDRAFT" / "draft.docx", "12,000.0")
    other = original if place == "original" else extracted
    folder = other / "budget_laws" / "2027"
    folder.mkdir(parents=True)
    (folder / "anything.txt").write_text("x", encoding="utf-8")
    exit_code = main(
        [
            "gdp-extract",
            "--years",
            "2027",
            "--source-type",
            "BUDGET_LAW",
            "--config",
            str(config),
            "--original-root",
            str(original),
            "--extracted-root",
            str(extracted),
            "--processed-root",
            str(tmp_path / "processed"),
        ]
    )
    err = capsys.readouterr().err

    assert exit_code == 1
    assert "unlabelled version skipped" not in err
    assert "WARNING" in err and "2027 BUDGET_LAW:" in err
