"""Identical-data note: versions of a year whose CSVs are the same bytes."""

import json
from datetime import date
from pathlib import Path

import pandas as pd

from armenian_budget.core.enums import SourceType
from armenian_budget.interfaces.cli.main import main
from armenian_budget.validation.identical import find_identical_versions
from armenian_budget.validation.registry import run_validation

D1 = date(2025, 10, 1)
D0 = date(2025, 9, 1)


def _dataset(processed: Path, label: str | None, total: float = 1000.0) -> None:
    stem = "2026_BUDGET_LAW" + (f"_{label}" if label else "")
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


def _find(processed, label, published=None):
    return find_identical_versions(
        processed, 2026, SourceType.BUDGET_LAW, label, published or {}
    )


def _report(processed, label, published=None):
    return run_validation(
        2026, SourceType.BUDGET_LAW, processed, label=label, published=published
    )


def test_no_note_for_single_version(tmp_path):
    _dataset(tmp_path, None)

    assert _find(tmp_path, None) == []
    report = _report(tmp_path, None)
    assert report.identical_data == []
    assert "Identical data" not in report.to_markdown()
    assert "Identical data" not in report.to_console_summary()
    assert "identical_data" not in json.loads(report.to_json())


def test_no_note_when_versions_differ(tmp_path):
    _dataset(tmp_path, None, total=1.0)
    _dataset(tmp_path, "EDRAFT", total=2.0)

    assert _find(tmp_path, None) == []
    assert _find(tmp_path, "EDRAFT") == []


def test_group_lists_all_identical_versions(tmp_path):
    _dataset(tmp_path, "EDRAFT")
    _dataset(tmp_path, "PARLIAMENT")
    _dataset(tmp_path, "DRAFT2", total=2.0)
    published = {"EDRAFT": D1, "PARLIAMENT": D1, "DRAFT2": date(2025, 11, 27)}

    assert _find(tmp_path, "EDRAFT", published) == [("EDRAFT", D1), ("PARLIAMENT", D1)]
    assert _find(tmp_path, "PARLIAMENT", published) == [
        ("EDRAFT", D1),
        ("PARLIAMENT", D1),
    ]
    assert _find(tmp_path, "DRAFT2", published) == []


def test_other_years_and_source_types_are_not_compared(tmp_path):
    _dataset(tmp_path, "EDRAFT")
    for other in ["2025_BUDGET_LAW_EDRAFT.csv", "2026_MTEP_EDRAFT.csv"]:
        (tmp_path / other).write_bytes(
            (tmp_path / "2026_BUDGET_LAW_EDRAFT.csv").read_bytes()
        )

    assert _find(tmp_path, "EDRAFT") == []


def test_unregistered_version_is_not_compared(tmp_path):
    _dataset(tmp_path, None)
    _dataset(tmp_path, "EDRAFT")
    _dataset(tmp_path, "STRAY")

    assert _find(tmp_path, None, {"EDRAFT": D1}) == [("EDRAFT", D1), (None, None)]


def test_group_order(tmp_path):
    for label in ["PARLIAMENT", "EDRAFT", "X", "Y", "B", None]:
        _dataset(tmp_path, label)
    published = {
        "PARLIAMENT": D1,
        "EDRAFT": D1,
        "X": D0,
        "Y": None,
        "B": None,
        None: D1,
    }

    # oldest first, ties by label with the unlabelled version first, undated last
    assert _find(tmp_path, "EDRAFT", published) == [
        ("X", D0),
        (None, D1),
        ("EDRAFT", D1),
        ("PARLIAMENT", D1),
        ("B", None),
        ("Y", None),
    ]


def test_unlabelled_in_group(tmp_path):
    _dataset(tmp_path, None)
    _dataset(tmp_path, "DRAFT2")
    published = {"DRAFT2": date(2025, 11, 27)}

    report = _report(tmp_path, None, published)

    line = "**Identical data:** DRAFT2 (2025-11-27), (unlabelled)"
    assert line in report.to_markdown().splitlines()
    assert "Identical data: DRAFT2 (2025-11-27), (unlabelled)" in (
        report.to_console_summary()
    )
    assert json.loads(report.to_json())["identical_data"] == [
        {"label": "DRAFT2", "published": "2025-11-27"},
        {"label": None, "published": None},
    ]


def test_markdown_note_sits_in_header_block(tmp_path):
    _dataset(tmp_path, "EDRAFT")
    _dataset(tmp_path, "PARLIAMENT")

    published = {"EDRAFT": D1, "PARLIAMENT": None}
    lines = _report(tmp_path, "EDRAFT", published).to_markdown().splitlines()

    note = lines.index("**Identical data:** EDRAFT (2025-10-01), PARLIAMENT")
    assert lines[note - 1].startswith("**Generated:**")
    assert note < lines.index("## Summary")


def test_note_does_not_affect_status(tmp_path):
    _dataset(tmp_path, None)
    alone = _report(tmp_path, None)
    _dataset(tmp_path, "DRAFT2")
    with_note = _report(tmp_path, None, {"DRAFT2": None})

    assert with_note.identical_data
    assert with_note.results == alone.results
    assert with_note.get_error_count() == alone.get_error_count()
    assert with_note.get_warning_count() == alone.get_warning_count()
    assert with_note.has_errors() == alone.has_errors()


def _validate(processed, config, *extra):
    return main(
        [
            "validate",
            "--years",
            "2026",
            "--source-type",
            "BUDGET_LAW",
            "--processed-root",
            str(processed),
            "--config",
            str(config),
            "--report",
            "--report-json",
            *extra,
        ]
    )


def _config(tmp_path: Path) -> Path:
    config = tmp_path / "sources.yaml"
    config.write_text(
        """
sources:
  - name: "edraft"
    year: 2026
    source_type: "budget_law"
    label: "EDRAFT"
    published: 2025-10-01
    url: "https://example.test/edraft.rar"
  - name: "parliament"
    year: 2026
    source_type: "budget_law"
    label: "PARLIAMENT"
    published: 2025-09-01
    url: "https://example.test/parliament.rar"
""",
        encoding="utf-8",
    )
    return config


def test_note_ignores_label_selection(tmp_path):
    processed = tmp_path / "processed"
    processed.mkdir()
    _dataset(processed, "EDRAFT")
    _dataset(processed, "PARLIAMENT")

    exit_code = _validate(processed, _config(tmp_path), "--label", "EDRAFT")

    assert not (processed / "2026_BUDGET_LAW_PARLIAMENT_validation.md").exists()
    markdown = (processed / "2026_BUDGET_LAW_EDRAFT_validation.md").read_text("utf-8")
    assert (
        "**Identical data:** PARLIAMENT (2025-09-01), EDRAFT (2025-10-01)"
        in markdown.splitlines()
    )
    report = json.loads(
        (processed / "2026_BUDGET_LAW_EDRAFT_validation.json").read_text("utf-8")
    )
    assert report["identical_data"] == [
        {"label": "PARLIAMENT", "published": "2025-09-01"},
        {"label": "EDRAFT", "published": "2025-10-01"},
    ]
    # the note is information: the exit code is the one without the other version
    (processed / "2026_BUDGET_LAW_PARLIAMENT.csv").unlink()
    assert _validate(processed, _config(tmp_path), "--label", "EDRAFT") == exit_code


def test_validate_without_config_file(tmp_path):
    # no registry: only the unlabelled version is known, so no other version is named
    processed = tmp_path / "processed"
    processed.mkdir()
    _dataset(processed, None)
    _dataset(processed, "PARLIAMENT")

    exit_code = _validate(processed, tmp_path / "missing.yaml")

    assert exit_code == 0
    markdown = (processed / "2026_BUDGET_LAW_validation.md").read_text("utf-8")
    assert "Identical data" not in markdown
    assert not (processed / "2026_BUDGET_LAW_PARLIAMENT_validation.md").exists()


def test_validate_with_invalid_config_still_validates(tmp_path):
    # the config is only read for dates and registered labels: warn, do not stop
    processed = tmp_path / "processed"
    processed.mkdir()
    _dataset(processed, None)
    expected = _validate(processed, tmp_path / "missing.yaml")
    config = tmp_path / "sources.yaml"
    config.write_text(
        'sources:\n  - name: "x"\n    year: 2026\n    source_type: "budget_law"\n'
        '    label: "bad-label"\n    url: "https://example.test/x.rar"\n',
        encoding="utf-8",
    )

    assert _validate(processed, config) == expected
    assert (processed / "2026_BUDGET_LAW_validation.md").exists()
