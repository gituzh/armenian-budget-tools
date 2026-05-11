import argparse
from pathlib import Path

from armenian_budget.ingestion import macro_indicators
from armenian_budget.interfaces.cli.main import cmd_gdp_report


def test_gdp_report_defaults_to_reports_root(monkeypatch, tmp_path):
    captured: dict[str, Path] = {}

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        macro_indicators,
        "load_gdp_snapshots",
        lambda *_args, **_kwargs: [{"year": 2025, "source_type": "BUDGET_LAW"}],
    )
    monkeypatch.setattr(
        macro_indicators,
        "write_gdp_html_report",
        lambda _snapshots, output_path: captured.setdefault("output_path", output_path),
    )

    result = cmd_gdp_report(
        argparse.Namespace(
            years=None,
            source_type=None,
            processed_root=None,
            output=None,
        )
    )

    assert result == 0
    assert captured["output_path"] == tmp_path / "data/reports/gdp_report.html"


def test_filtered_gdp_report_defaults_to_partial_reports_path(monkeypatch, tmp_path):
    captured: dict[str, Path] = {}

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        macro_indicators,
        "load_gdp_snapshots",
        lambda *_args, **_kwargs: [{"year": 2025, "source_type": "BUDGET_LAW"}],
    )
    monkeypatch.setattr(
        macro_indicators,
        "write_gdp_html_report",
        lambda _snapshots, output_path: captured.setdefault("output_path", output_path),
    )

    result = cmd_gdp_report(
        argparse.Namespace(
            years="2025",
            source_type=None,
            processed_root=None,
            output=None,
        )
    )

    assert result == 0
    assert captured["output_path"] == tmp_path / "data/reports/gdp_report_partial.html"


def test_gdp_report_table_rows_and_controls_drive_selection():
    html = macro_indicators._render_gdp_html(
        [
            {
                "year": 2025,
                "source_type": "BUDGET_LAW",
                "source_file": "source.docx",
                "tables": [
                    {
                        "records": [
                            {
                                "indicator": "Անվանական ՀՆԱ",
                                "target_year": 2025,
                                "status": "ծրագիր",
                                "value": 10891.5,
                            }
                        ]
                    }
                ],
            }
        ]
    )

    assert 'document.addEventListener("click"' in html
    assert 'closest("tr[data-series-id]")' in html
    assert 'id="gdp-prev"' in html
    assert 'id="gdp-next"' in html
    assert "series-active" in html
    assert "series-muted" in html
    assert "scrollIntoView" not in html
    assert 'group.addEventListener("click"' not in html


def test_gdp_report_rows_order_prior_spending_after_current_budget():
    snapshots = [
        _gdp_snapshot(2022, "SPENDING_Q1234"),
        _gdp_snapshot(2023, "BUDGET_LAW"),
        _gdp_snapshot(2022, "BUDGET_LAW"),
    ]

    html = macro_indicators._render_gdp_html(snapshots)

    budget_2022 = html.index(">2022 BUDGET_LAW<")
    budget_2023 = html.index(">2023 BUDGET_LAW<")
    spending_2022 = html.index(">2022 SPENDING_Q1234<")
    assert budget_2022 < budget_2023 < spending_2022


def _gdp_snapshot(year: int, source_type: str) -> dict:
    return {
        "year": year,
        "source_type": source_type,
        "source_file": f"{year}_{source_type}.docx",
        "tables": [
            {
                "records": [
                    {
                        "indicator": "Անվանական ՀՆԱ",
                        "target_year": year,
                        "status": "փաստ",
                        "value": 1.0,
                    }
                ]
            }
        ],
    }
