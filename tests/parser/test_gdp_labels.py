"""GDP extraction for labelled budget-law versions (synthetic documents)."""

import json
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
