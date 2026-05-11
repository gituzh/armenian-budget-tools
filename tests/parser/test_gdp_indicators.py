from pathlib import Path

import pytest

from armenian_budget.ingestion.gdp_indicators import (
    _nominal_gdp_records,
    extract_gdp_snapshot,
    find_spending_gdp_docx,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
EXTRACTED_ROOT = REPO_ROOT / "data" / "extracted"


def _has_annual_gdp_reports() -> bool:
    return all(
        (EXTRACTED_ROOT / "spending_reports" / str(year) / "Q1234").exists()
        for year in (2024, 2025)
    )


pytestmark = pytest.mark.skipif(
    not _has_annual_gdp_reports(),
    reason="2024-2025 annual spending report fixtures are not available",
)


def test_find_spending_gdp_docx_for_current_report_layouts():
    assert find_spending_gdp_docx(EXTRACTED_ROOT, 2024).name.startswith(
        "12.Մակրոտնտեսական և հարկաբյուջետային ցուցանիշներ"
    )
    assert find_spending_gdp_docx(EXTRACTED_ROOT, 2025).name.startswith(
        "12.Մակրոտնտեսական և հարկաբյուջետային ցուց"
    )


def test_extract_gdp_snapshot_from_2025_spending_docx():
    snapshot = extract_gdp_snapshot(
        year=2025,
        source_type="SPENDING_Q1234",
        original_root=REPO_ROOT / "data" / "original",
        extracted_root=EXTRACTED_ROOT,
        sources_config=REPO_ROOT / "config" / "sources.yaml",
    )
    records = snapshot["tables"][0]["records"]
    nominal_gdp = [
        record
        for record in records
        if record["indicator"] == "Անվանական ՀՆԱ"
        and record["target_year"] == 2025
        and record["status"] == "փաստ"
    ]

    assert snapshot["source_type"] == "SPENDING_Q1234"
    assert len(records) == 60
    assert len(nominal_gdp) == 1
    assert nominal_gdp[0]["unit"] == "մլրդ դրամ"
    assert nominal_gdp[0]["value"] == 11317.5


def test_nominal_gdp_report_skips_spending_budget_plan_value():
    snapshot = {
        "source_type": "SPENDING_Q1234",
        "tables": [
            {
                "records": [
                    {
                        "target_year": 2025,
                        "status": "պետական բյուջե",
                        "indicator": "Անվանական ՀՆԱ",
                        "value": 10891.5,
                    },
                    {
                        "target_year": 2025,
                        "status": "կանխ.",
                        "indicator": "Անվանական ՀՆԱ",
                        "value": 10900.0,
                    },
                    {
                        "target_year": 2025,
                        "status": "փաստ",
                        "indicator": "Անվանական ՀՆԱ",
                        "value": 11317.5,
                    },
                ]
            }
        ],
    }

    records = _nominal_gdp_records(snapshot)

    assert [record["status"] for record in records] == ["փաստ"]
