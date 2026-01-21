"""Pytest tests for CLI report generation.

This module verifies the functionality of the `armenian-budget validate` CLI command,
ensuring it correctly generates validation reports in Markdown and JSON formats
at specified or default locations.
"""

import json
import subprocess
import sys


def run_cli_command(args: list[str]) -> subprocess.CompletedProcess:
    """Helper function to run CLI commands."""
    return subprocess.run(
        [sys.executable, "-m", "armenian_budget.interfaces.cli.main"] + args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def test_cli_validate_report_generation(tmp_path):
    """Test that `validate` command with --report and --report-json flags generates reports."""
    processed_root = tmp_path / "processed"
    csv_dir = processed_root
    csv_dir.mkdir(parents=True)

    # Create dummy CSV and overall.json files
    csv_path = csv_dir / "2023_SPENDING_Q1.csv"
    overall_path = csv_dir / "2023_SPENDING_Q1_overall.json"
    csv_path.write_text("col1,col2\nval1,val2")
    overall_path.write_text('{"total": 1000}')

    # Test --report with default location
    result = run_cli_command(
        [
            "validate",
            "--years",
            "2023",
            "--source-type",
            "SPENDING_Q1",
            "--processed-root",
            str(processed_root),
            "--report",
        ]
    )
    assert result.returncode == 2
    md_report_path = csv_dir / "2023_SPENDING_Q1_validation.md"
    assert md_report_path.exists()
    md_content = md_report_path.read_text()
    assert "# Validation Report: 2023_SPENDING_Q1.csv" in md_content
    assert "## ❌ Errors" in md_content

    # Test --report with custom directory
    custom_report_dir = tmp_path / "custom_reports"
    result = run_cli_command(
        [
            "validate",
            "--years",
            "2023",
            "--source-type",
            "SPENDING_Q1",
            "--processed-root",
            str(processed_root),
            "--report",
            str(custom_report_dir),
        ]
    )
    assert result.returncode == 2
    custom_md_report_path = custom_report_dir / "2023_SPENDING_Q1_validation.md"
    assert custom_md_report_path.exists()
    custom_md_content = custom_md_report_path.read_text()
    assert "# Validation Report: 2023_SPENDING_Q1.csv" in custom_md_content

    # Test --report-json with default location
    result = run_cli_command(
        [
            "validate",
            "--years",
            "2023",
            "--source-type",
            "SPENDING_Q1",
            "--processed-root",
            str(processed_root),
            "--report-json",
        ]
    )
    assert result.returncode == 2
    json_report_path = csv_dir / "2023_SPENDING_Q1_validation.json"
    assert json_report_path.exists()
    json_content = json.loads(json_report_path.read_text())
    assert json_content["metadata"]["source_type"] == "SPENDING_Q1"
    assert json_content["summary"]["with_errors"] > 0

    # Test --report-json with custom directory
    custom_json_report_dir = tmp_path / "custom_json_reports"
    result = run_cli_command(
        [
            "validate",
            "--years",
            "2023",
            "--source-type",
            "SPENDING_Q1",
            "--processed-root",
            str(processed_root),
            "--report-json",
            str(custom_json_report_dir),
        ]
    )
    assert result.returncode == 2
    custom_json_report_path = custom_json_report_dir / "2023_SPENDING_Q1_validation.json"
    assert custom_json_report_path.exists()
    custom_json_content = json.loads(custom_json_report_path.read_text())
    assert custom_json_content["metadata"]["source_type"] == "SPENDING_Q1"
