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
