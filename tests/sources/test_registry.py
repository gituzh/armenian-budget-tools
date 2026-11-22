from datetime import date

import pytest

from armenian_budget.sources.registry import SourceRegistry


def test_registry_expands_multi_file_sources(tmp_path):
    config = tmp_path / "sources.yaml"
    config.write_text(
        """
sources:
  - name: "2026_budget_law"
    year: 2026
    source_type: "budget_law"
    description: "2026 State Budget Law"
    files:
      - name: "2026_budget_law_pdf"
        url: "https://example.test/law.pdf"
        file_format: "pdf"
        filename: "law.pdf"
        checksum: "abc"
      - name: "2026_budget_law_appendices"
        url: "https://example.test/appendices.rar"
        file_format: "rar"
        description: "2026 State Budget Law appendices"
""",
        encoding="utf-8",
    )

    sources = SourceRegistry(config).all()

    assert [source.name for source in sources] == [
        "2026_budget_law_pdf",
        "2026_budget_law_appendices",
    ]
    assert [source.url for source in sources] == [
        "https://example.test/law.pdf",
        "https://example.test/appendices.rar",
    ]
    assert sources[0].year == 2026
    assert sources[0].source_type == "budget_law"
    assert sources[0].file_format == "pdf"
    assert sources[0].filename == "law.pdf"
    assert sources[0].checksum == "abc"
    assert sources[1].description == "2026 State Budget Law appendices"


def test_registry_keeps_single_file_source_shape(tmp_path):
    config = tmp_path / "sources.yaml"
    config.write_text(
        """
sources:
  - name: "2025_spending_q1"
    year: 2025
    source_type: "spending_q1"
    url: "https://example.test/report.rar"
    file_format: "rar"
    description: "2025 Q1 Spending Report"
""",
        encoding="utf-8",
    )

    source = SourceRegistry(config).all()[0]

    assert source.name == "2025_spending_q1"
    assert source.url == "https://example.test/report.rar"
    assert source.file_format == "rar"


def _write_config(tmp_path, body):
    config = tmp_path / "sources.yaml"
    config.write_text("sources:\n" + body, encoding="utf-8")
    return config


def _entry(name, label_line="", published_line="", year=2026):
    return f"""
  - name: "{name}"
    year: {year}
    source_type: "budget_law"
{label_line}{published_line}    files:
      - name: "{name}_attachments"
        url: "https://example.test/{name}.rar"
      - name: "{name}_explanatory_note"
        url: "https://example.test/{name}.docx"
"""


def test_registry_reads_label_and_published(tmp_path):
    config = _write_config(
        tmp_path,
        _entry("a", '    label: "EDRAFT"\n', "    published: 2025-10-01\n"),
    )

    sources = SourceRegistry(config).all()

    assert len(sources) == 2
    assert [source.label for source in sources] == ["EDRAFT", "EDRAFT"]
    assert [source.published for source in sources] == [date(2025, 10, 1)] * 2


def test_registry_reads_quoted_published(tmp_path):
    config = _write_config(
        tmp_path,
        _entry("a", '    label: "EDRAFT"\n', '    published: "2025-10-01"\n'),
    )

    assert SourceRegistry(config).all()[0].published == date(2025, 10, 1)


def test_registry_defaults_are_unlabelled(tmp_path):
    source = SourceRegistry(_write_config(tmp_path, _entry("a"))).all()[0]

    assert source.label is None
    assert source.published is None


@pytest.mark.parametrize("label", ["edraft", "GDP", "E_DRAFT"])
def test_registry_rejects_bad_label(tmp_path, label):
    config = _write_config(tmp_path, _entry("bad_one", f"    label: {label}\n"))

    with pytest.raises(ValueError, match="bad_one"):
        SourceRegistry(config)


def test_registry_converts_non_string_label(tmp_path):
    config = _write_config(tmp_path, _entry("a", "    label: 2\n"))

    assert SourceRegistry(config).all()[0].label == "2"


@pytest.mark.parametrize("published", ['"October 2025"', "20251001", '"2025-13-01"'])
def test_registry_rejects_bad_published(tmp_path, published):
    config = _write_config(
        tmp_path, _entry("bad_one", "", f"    published: {published}\n")
    )

    with pytest.raises(ValueError, match="bad_one"):
        SourceRegistry(config)


@pytest.mark.parametrize("label_line", ['    label: "EDRAFT"\n', ""])
def test_registry_rejects_duplicate_version(tmp_path, label_line):
    config = _write_config(
        tmp_path, _entry("first", label_line) + _entry("second", label_line)
    )

    with pytest.raises(ValueError, match="second"):
        SourceRegistry(config)


def test_registry_allows_same_label_in_other_year_or_type(tmp_path):
    config = _write_config(
        tmp_path,
        _entry("a", '    label: "EDRAFT"\n')
        + _entry("b", '    label: "EDRAFT"\n', year=2025)
        + _entry("c", '    label: "PARLIAMENT"\n'),
    )

    assert len(SourceRegistry(config).all()) == 6


def test_published_by_label(tmp_path):
    config = _write_config(
        tmp_path,
        _entry("law", "", "    published: 2025-12-10\n")
        + _entry("edraft", '    label: "EDRAFT"\n', "    published: 2025-10-01\n")
        + _entry("parl", '    label: "PARLIAMENT"\n')
        + _entry("other_year", '    label: "DRAFT"\n', year=2027),
    )

    assert SourceRegistry(config).published_by_label(2026, "budget_law") == {
        None: date(2025, 12, 10),
        "EDRAFT": date(2025, 10, 1),
        "PARLIAMENT": None,
    }
