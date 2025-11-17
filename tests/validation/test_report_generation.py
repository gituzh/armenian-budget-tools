"""Pytest tests for validation report generation."""

import json
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from armenian_budget.core.enums import SourceType
from armenian_budget.validation.models import CheckResult, ValidationReport


@pytest.fixture
def mock_check_results():
    """Fixture for mock CheckResult objects."""
    return [
        CheckResult(
            check_id="required_fields",
            severity="error",
            passed=False,
            fail_count=2,
            messages=["Missing field 'program_id' in row 5", "Missing field 'amount' in row 10"],
        ),
        CheckResult(
            check_id="negative_totals",
            severity="warning",
            passed=False,
            fail_count=1,
            messages=["Negative total found for 'state_body_X': -100"],
        ),
        CheckResult(
            check_id="empty_identifiers",
            severity="error",
            passed=True,
            fail_count=0,
            messages=[],
        ),
        CheckResult(
            check_id="period_vs_annual",
            severity="error",
            passed=False,
            fail_count=3,
            messages=[
                "Period plan exceeds annual plan for 'program_Y' in row 15",
                "Period plan exceeds annual plan for 'program_Z' in row 20",
                "Period plan exceeds annual plan for 'program_A' in row 25",
            ],
        ),
    ]


@pytest.fixture
def mock_validation_report(mock_check_results):
    """Fixture for a mock ValidationReport instance."""
    return ValidationReport(
        results=mock_check_results,
        source_type=SourceType.SPENDING_Q1,
        csv_path=Path("data/processed/csv/2023_SPENDING_Q1.csv"),
        overall_path=Path("data/processed/csv/2023_SPENDING_Q1_overall.json"),
    )


@pytest.fixture
def mock_validation_report_all_passed():
    """Fixture for a ValidationReport where all checks passed."""
    return ValidationReport(
        results=[
            CheckResult(
                check_id="required_fields", severity="error", passed=True, fail_count=0
            ),
            CheckResult(
                check_id="negative_totals", severity="warning", passed=True, fail_count=0
            ),
        ],
        source_type=SourceType.BUDGET_LAW,
        csv_path=Path("data/processed/csv/2024_BUDGET_LAW.csv"),
        overall_path=Path("data/processed/csv/2024_BUDGET_LAW_overall.json"),
    )


def test_to_markdown_output(mock_validation_report):
    """Test the to_markdown method for correct content and structure."""
    markdown_output = mock_validation_report.to_markdown()

    # Check for header and metadata
    assert f"# Validation Report: {mock_validation_report.csv_path.name}" in markdown_output
    assert f"**Source Type:** {mock_validation_report.source_type.value}" in markdown_output
    assert f"**File:** {mock_validation_report.csv_path}" in markdown_output
    assert "Generated:" in markdown_output

    # Check summary section
    assert "## Summary" in markdown_output
    assert "- **Total Checks:** 4" in markdown_output
    assert "- **Passed:** 1 ✅" in markdown_output
    assert "- **Failed:** 3 ❌" in markdown_output
    assert "- **Errors:** 5" in markdown_output
    assert "- **Warnings:** 1" in markdown_output

    # Check passed checks section
    assert "## ✅ Passed Checks" in markdown_output
    assert "- **empty_identifiers**" in markdown_output

    # Check warnings section
    assert "## ⚠️ Warnings" in markdown_output
    assert "### ⚠️ negative_totals (1 failures)" in markdown_output
    assert "- Negative total found for 'state_body_X': -100" in markdown_output

    # Check errors section
    assert "## ❌ Errors" in markdown_output
    assert "### ❌ required_fields (2 failures)" in markdown_output
    assert "Missing field 'program_id' in row 5" in markdown_output
    assert "### ❌ period_vs_annual (3 failures)" in markdown_output
    assert "Period plan exceeds annual plan for 'program_Y' in row 15" in markdown_output

    # Check footer
    assert "For detailed information about validation checks" in markdown_output


def test_to_markdown_all_passed(mock_validation_report_all_passed):
    """Test to_markdown when all checks pass."""
    markdown_output = mock_validation_report_all_passed.to_markdown()

    assert "## ✅ All Checks Passed" in markdown_output
    assert "No validation issues found." in markdown_output
    assert "## ✅ Passed Checks" in markdown_output
    assert "- **negative_totals**" in markdown_output
    assert "## ⚠️ Warnings" not in markdown_output
    assert "## ❌ Errors" not in markdown_output


def test_to_json_output(mock_validation_report):
    """Test the to_json method for correct content and structure."""
    json_output = mock_validation_report.to_json()
    report_data = json.loads(json_output)

    # Check metadata
    assert report_data["metadata"]["source_type"] == mock_validation_report.source_type.value
    assert report_data["metadata"]["csv_path"] == str(mock_validation_report.csv_path)
    assert report_data["metadata"]["overall_path"] == str(mock_validation_report.overall_path)
    assert "generated_at" in report_data["metadata"]
    assert datetime.fromisoformat(report_data["metadata"]["generated_at"])

    # Check summary
    assert report_data["summary"]["total_checks"] == 4
    assert report_data["summary"]["passed_checks"] == 1
    assert report_data["summary"]["failed_checks"] == 3
    assert report_data["summary"]["errors"] == 5
    assert report_data["summary"]["warnings"] == 1

    # Check passed checks
    assert len(report_data["passed_checks"]) == 1
    assert report_data["passed_checks"][0]["check_id"] == "empty_identifiers"

    # Check warning checks
    assert len(report_data["warning_checks"]) == 1
    assert report_data["warning_checks"][0]["check_id"] == "negative_totals"
    assert report_data["warning_checks"][0]["fail_count"] == 1
    assert report_data["warning_checks"][0]["messages"] == [
        "Negative total found for 'state_body_X': -100"
    ]

    # Check error checks
    assert len(report_data["error_checks"]) == 2
    assert report_data["error_checks"][0]["check_id"] == "period_vs_annual"
    assert report_data["error_checks"][0]["fail_count"] == 3
    assert report_data["error_checks"][1]["check_id"] == "required_fields"
    assert report_data["error_checks"][1]["fail_count"] == 2


def test_to_json_all_passed(mock_validation_report_all_passed):
    """Test to_json when all checks pass."""
    json_output = mock_validation_report_all_passed.to_json()
    report_data = json.loads(json_output)

    assert report_data["summary"]["passed_checks"] == 2
    assert report_data["summary"]["failed_checks"] == 0
    assert report_data["summary"]["errors"] == 0
    assert report_data["summary"]["warnings"] == 0
    assert len(report_data["passed_checks"]) == 2
    assert len(report_data["warning_checks"]) == 0
    assert len(report_data["error_checks"]) == 0


def test_to_console_summary_output(mock_validation_report):
    """Test the to_console_summary method for correct content and structure."""
    console_output = mock_validation_report.to_console_summary()

    # Check summary section
    assert "Validation Summary:" in console_output
    assert "Source: SPENDING_Q1 (2023_SPENDING_Q1.csv)" in console_output
    assert "Checks: 4 total, 1 passed, 3 failed" in console_output
    assert "Errors: 5" in console_output
    assert "Warnings: 1" in console_output

    # Check failed checks list
    assert "Failed Checks:" in console_output
    assert "❌ required_fields (error): 2 failures" in console_output
    assert "   - Missing field 'program_id' in row 5" in console_output
    assert "⚠️ negative_totals (warning): 1 failures" in console_output
    assert "   - Negative total found for 'state_body_X': -100" in console_output
    assert "❌ period_vs_annual (error): 3 failures" in console_output
    assert "   - Period plan exceeds annual plan for 'program_Y' in row 15" in console_output


def test_to_console_summary_all_passed(mock_validation_report_all_passed):
    """Test to_console_summary when all checks pass."""
    console_output = mock_validation_report_all_passed.to_console_summary()

    assert "Validation Summary:" in console_output
    assert "✅ All validation checks passed!" in console_output
    assert "Failed Checks:" not in console_output
