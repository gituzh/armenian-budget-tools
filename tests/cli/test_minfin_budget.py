from __future__ import annotations

import json

from armenian_budget.interfaces.cli import main as cli_main
from armenian_budget.sources import minfin_budget as budget


def test_extract_budget_year_pages_reads_landing_links():
    html = """
    <a href="/hy/page/byuje_2018">Պետական բյուջե 2018թ.</a>
    <a href="/hy/page/petakan_byuje_2026t">Պետական բյուջե 2026թ.</a>
    <a href="/hy/page/petakan_byuje_2025t">Պետական բյուջե 2025թ.</a>
    <a href="/hy/page/not_budget_2024">Other 2024</a>
    """

    assert budget.extract_budget_year_pages(html) == [
        {
            "year": 2018,
            "name": "Պետական բյուջե 2018թ.",
            "page_url": "https://minfin.am/hy/page/byuje_2018",
        },
        {
            "year": 2025,
            "name": "Պետական բյուջե 2025թ.",
            "page_url": "https://minfin.am/hy/page/petakan_byuje_2025t",
        },
        {
            "year": 2026,
            "name": "Պետական բյուջե 2026թ.",
            "page_url": "https://minfin.am/hy/page/petakan_byuje_2026t",
        },
    ]


def test_extract_budget_page_downloads_keeps_download_links():
    html = """
    <main>
      <a href="/website/images/website/law.pdf"> Budget law </a>
      <a href="/website/images/website/appendices.rar">Appendices</a>
      <a href="/hy/page/not-a-download">HTML page</a>
    </main>
    """

    assert budget.extract_budget_page_downloads(
        html,
        "https://minfin.am/hy/page/petakan_byuje_2025t",
    ) == [
        {
            "name": "Budget law",
            "file_name": "law.pdf",
            "file_format": "pdf",
            "download_url": "https://minfin.am/website/images/website/law.pdf",
            "source": "budget_page",
        },
        {
            "name": "Appendices",
            "file_name": "appendices.rar",
            "file_format": "rar",
            "download_url": "https://minfin.am/website/images/website/appendices.rar",
            "source": "budget_page",
        },
    ]


def test_extract_budget_page_downloads_uses_container_text_for_split_link():
    html = """
    <div class="app_block">
      <li>
        <strong>
          <a href="/website/images/website/law.docx">«Հայաստանի</a>
          <a href="/website/images/website/law.docx">
            Հանրապետության 2023 թվականի պետական բյուջեի մասին» ՀՀ օրենք
          </a>
        </strong>
      </li>
    </div>
    """

    assert budget.extract_budget_page_downloads(
        html,
        "https://minfin.am/hy/page/petakan_byuje_2023t",
    ) == [
        {
            "name": "«Հայաստանի Հանրապետության 2023 թվականի պետական բյուջեի մասին» ՀՀ օրենք",
            "file_name": "law.docx",
            "file_format": "docx",
            "download_url": "https://minfin.am/website/images/website/law.docx",
            "source": "budget_page",
        }
    ]


def test_extract_budget_page_downloads_does_not_split_sibling_letter():
    html = """
    <div class="app_block">
      <li>
        <strong>
          <a href="/website/images/website/explanation.docx">
            ՀՀ կառավարության 2025 թվականի բյուջետային ուղերձ-բացատրագի
          </a>ր
        </strong>
      </li>
    </div>
    """

    assert budget.extract_budget_page_downloads(
        html,
        "https://minfin.am/hy/page/petakan_byuje_2025t",
    ) == [
        {
            "name": "ՀՀ կառավարության 2025 թվականի բյուջետային ուղերձ-բացատրագիր",
            "file_name": "explanation.docx",
            "file_format": "docx",
            "download_url": "https://minfin.am/website/images/website/explanation.docx",
            "source": "budget_page",
        }
    ]


def test_extract_budget_page_downloads_marks_unlabeled_links_hidden():
    html = """
    <div class="app_block">
      <a href="/website/images/website/byujei_havelvac-2018.rar"></a>
    </div>
    """

    assert budget.extract_budget_page_downloads(
        html,
        "https://minfin.am/hy/page/byuje_2018",
    ) == [
        {
            "name": "byujei_havelvac-2018.rar",
            "file_name": "byujei_havelvac-2018.rar",
            "file_format": "rar",
            "download_url": "https://minfin.am/website/images/website/byujei_havelvac-2018.rar",
            "source": "budget_page",
            "hidden": True,
        }
    ]


def test_extract_budget_page_downloads_marks_css_hidden_links_hidden():
    html = """
    <div class="app_block">
      <a href="/website/images/website/hidden.pdf" style="display: none">Hidden</a>
    </div>
    """

    assert budget.extract_budget_page_downloads(
        html,
        "https://minfin.am/hy/page/petakan_byuje_2025t",
    ) == [
        {
            "name": "Hidden",
            "file_name": "hidden.pdf",
            "file_format": "pdf",
            "download_url": "https://minfin.am/website/images/website/hidden.pdf",
            "source": "budget_page",
            "hidden": True,
        }
    ]


def test_cli_minfin_budget_downloads_only(monkeypatch, capsys):
    def fake_list_minfin_budget(years):
        assert years == {2025}
        return [
            {
                "year": 2025,
                "source_type": "budget_law",
                "page_url": "https://minfin.am/hy/page/petakan_byuje_2025t",
                "downloads": [
                    {
                        "name": "Budget law",
                        "file_name": "law.pdf",
                        "file_format": "pdf",
                        "download_url": "https://example.test/law.pdf",
                        "source": "budget_page",
                    }
                ],
            }
        ]

    monkeypatch.setattr(budget, "list_minfin_budget", fake_list_minfin_budget)

    exit_code = cli_main.main(
        [
            "minfin-budget",
            "--years",
            "2025",
            "--downloads-only",
        ]
    )

    assert exit_code == 0
    assert json.loads(capsys.readouterr().out) == [
        {
            "year": 2025,
            "source_type": "budget_law",
            "page_url": "https://minfin.am/hy/page/petakan_byuje_2025t",
            "name": "Budget law",
            "file_name": "law.pdf",
            "file_format": "pdf",
            "download_url": "https://example.test/law.pdf",
            "source": "budget_page",
        }
    ]
