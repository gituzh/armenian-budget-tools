from pathlib import Path

import pytest

from armenian_budget.ingestion.macro_indicators import (
    extract_macro_indicator_history,
    extract_macro_indicators_from_docx,
    find_macro_indicator_docx,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
EXTRACTED_ROOT = REPO_ROOT / "data" / "extracted"


def _has_annual_macro_reports() -> bool:
    return all(
        (EXTRACTED_ROOT / "spending_reports" / str(year) / "Q1234").exists()
        for year in (2024, 2025)
    )


pytestmark = pytest.mark.skipif(
    not _has_annual_macro_reports(),
    reason="2024-2025 annual spending report fixtures are not available",
)


def test_find_macro_indicator_docx_for_current_report_layouts():
    assert find_macro_indicator_docx(EXTRACTED_ROOT, 2024).name.startswith(
        "12.Մակրոտնտեսական և հարկաբյուջետային ցուցանիշներ"
    )
    assert find_macro_indicator_docx(EXTRACTED_ROOT, 2025).name.startswith(
        "12.Մակրոտնտեսական և հարկաբյուջետային ցուց"
    )


def test_extract_macro_indicators_from_2025_docx():
    docx_path = find_macro_indicator_docx(EXTRACTED_ROOT, 2025)
    records = extract_macro_indicators_from_docx(docx_path, 2025)

    nominal_gdp = [
        record
        for record in records
        if record.indicator == "Անվանական ՀՆԱ"
        and record.target_year == 2025
        and record.scenario == "actual"
    ]

    assert len(records) == 60
    assert len(nominal_gdp) == 1
    assert nominal_gdp[0].unit == "մլրդ դրամ"
    assert nominal_gdp[0].value == 11317.5


def test_extract_macro_indicator_history_keeps_report_snapshot_context():
    records, warnings = extract_macro_indicator_history(EXTRACTED_ROOT, [2024, 2025])

    report_2024_value = next(
        record.value
        for record in records
        if record.report_year == 2024
        and record.target_year == 2023
        and record.indicator == "Անվանական ՀՆԱ"
        and record.scenario == "history"
    )
    report_2025_value = next(
        record.value
        for record in records
        if record.report_year == 2025
        and record.target_year == 2023
        and record.indicator == "Անվանական ՀՆԱ"
        and record.scenario == "history"
    )

    assert warnings == []
    assert report_2024_value == 9453.2
    assert report_2025_value == 9492.5
