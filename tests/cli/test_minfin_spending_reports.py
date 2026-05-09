from __future__ import annotations

import json

import pytest

from armenian_budget.interfaces.cli import main as cli_main
from armenian_budget.sources import minfin_spending_reports as reports


def test_extract_year_ids_reads_minfin_select_options():
    html = """
    <select id="yearSelect">
      <option value="2024" data-id="41">2024</option>
      <option value="2025" data-id="42">2025</option>
      <option value="" data-id="">ignored</option>
    </select>
    """

    assert reports.extract_year_ids(html) == [(2024, 41), (2025, 42)]


def test_extract_detail_page_downloads_keeps_download_links_once():
    html = """
    <section class="docs">
      <a href="/website/images/files/report.xlsx"> Report workbook </a>
      <a href="/website/images/files/report.xlsx">Duplicate</a>
      <a href="/hy/page/not-a-download">HTML page</a>
      <a href="https://minfin.am/website/images/files/archive.rar">Archive</a>
    </section>
    """

    downloads = reports.extract_detail_page_downloads(
        html,
        "https://minfin.am/hy/page/details",
    )

    assert downloads == [
        {
            "name": "Report workbook",
            "file_name": "report.xlsx",
            "file_format": "xlsx",
            "download_url": "https://minfin.am/website/images/files/report.xlsx",
            "source": "detail_page",
        },
        {
            "name": "Archive",
            "file_name": "archive.rar",
            "file_format": "rar",
            "download_url": "https://minfin.am/website/images/files/archive.rar",
            "source": "detail_page",
        },
    ]


def test_cli_minfin_spending_reports_downloads_only(monkeypatch, capsys):
    def fake_list_minfin_spending_reports(years):
        assert years == {2025}
        return [
            {
                "year": 2025,
                "quarter": "Q1",
                "downloads": [
                    {
                        "name": "Report",
                        "file_name": "report.xlsx",
                        "file_format": "xlsx",
                        "download_url": "https://example.test/report.xlsx",
                        "source": "period_file",
                    }
                ],
            },
            {
                "year": 2025,
                "quarter": "Q12",
                "downloads": [],
            },
        ]

    monkeypatch.setattr(
        reports,
        "list_minfin_spending_reports",
        fake_list_minfin_spending_reports,
    )

    exit_code = cli_main.main(
        [
            "minfin-spending-reports",
            "--years",
            "2025",
            "--quarter",
            "Q1",
            "--downloads-only",
        ]
    )

    assert exit_code == 0
    assert json.loads(capsys.readouterr().out) == [
        {
            "year": 2025,
            "quarter": "Q1",
            "name": "Report",
            "file_name": "report.xlsx",
            "file_format": "xlsx",
            "download_url": "https://example.test/report.xlsx",
            "source": "period_file",
        }
    ]


def test_cli_minfin_spending_reports_rejects_archives_only():
    parser = cli_main.build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(["minfin-spending-reports", "--archives-only"])
