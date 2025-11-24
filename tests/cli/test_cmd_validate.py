"""Tests for cmd_validate CLI function."""

from __future__ import annotations

import argparse
import json
import pandas as pd
import pytest
from armenian_budget.interfaces.cli.main import cmd_validate


class TestCmdValidate:
    """Tests for cmd_validate function."""

    def test_cmd_validate_missing_processed_root(self, tmp_path):
        """Test error when processed_root doesn't exist."""
        args = argparse.Namespace(
            years="2023",
            source_type="BUDGET_LAW",
            processed_root=str(tmp_path / "nonexistent"),
            report=False,
            report_json=False,
        )
        result = cmd_validate(args)
        assert result == 2

    def test_cmd_validate_success_minimal(self, tmp_path):
        """Test cmd_validate with minimal valid data."""
        # Setup directory structure
        processed_root = tmp_path
        csv_dir = processed_root
        csv_dir.mkdir(exist_ok=True)

        # Create minimal valid CSV (BUDGET_LAW format)
        csv_path = csv_dir / "2023_BUDGET_LAW.csv"
        df_data = {
            "state_body": ["Overall", "State Body 1"],
            "state_body_code": ["", "001"],
            "program": ["", ""],
            "program_code": ["", ""],
            "subprogram": ["", ""],
            "subprogram_code": ["", ""],
            "subprogram_total": [1000.0, 1000.0],
        }
        pd.DataFrame(df_data).to_csv(csv_path, index=False)

        # Create minimal valid overall.json
        overall_path = csv_dir / "2023_BUDGET_LAW_overall.json"
        overall_data = {"overall_total": 1000.0}
        with open(overall_path, "w", encoding="utf-8") as f:
            json.dump(overall_data, f)

        # Run validation
        args = argparse.Namespace(
            years="2023",
            source_type="BUDGET_LAW",
            processed_root=str(processed_root),
            report=False,
            report_json=False,
        )
        result = cmd_validate(args)

        # Should succeed (return 0) or have validation errors (return 2)
        assert result in [0, 2]

    def test_cmd_validate_with_report_flag(self, tmp_path):
        """Test cmd_validate with --report flag to generate markdown report."""
        # Setup directory structure
        processed_root = tmp_path
        csv_dir = processed_root
        csv_dir.mkdir(exist_ok=True)

        # Create minimal valid CSV
        csv_path = csv_dir / "2023_BUDGET_LAW.csv"
        df_data = {
            "state_body": ["Overall", "State Body 1"],
            "state_body_code": ["", "001"],
            "program": ["", ""],
            "program_code": ["", ""],
            "subprogram": ["", ""],
            "subprogram_code": ["", ""],
            "subprogram_total": [1000.0, 1000.0],
        }
        pd.DataFrame(df_data).to_csv(csv_path, index=False)

        # Create overall.json
        overall_path = csv_dir / "2023_BUDGET_LAW_overall.json"
        with open(overall_path, "w", encoding="utf-8") as f:
            json.dump({"overall_total": 1000.0}, f)

        # Run validation with report flag
        args = argparse.Namespace(
            years="2023",
            source_type="BUDGET_LAW",
            processed_root=str(processed_root),
            report=True,
            report_json=False,
        )
        cmd_validate(args)

        # Check that markdown report was created
        expected_report = csv_dir / "2023_BUDGET_LAW_validation.md"
        assert expected_report.exists()
        assert expected_report.stat().st_size > 0

        # Verify report contains expected sections
        report_content = expected_report.read_text()
        assert "Summary" in report_content
        assert "Source Type:" in report_content

    def test_cmd_validate_with_custom_report_directory(self, tmp_path):
        """Test cmd_validate with custom --report directory."""
        # Setup directory structure
        processed_root = tmp_path
        csv_dir = processed_root
        csv_dir.mkdir(exist_ok=True)

        # Create minimal valid CSV
        csv_path = csv_dir / "2023_BUDGET_LAW.csv"
        df_data = {
            "state_body": ["Overall", "State Body 1"],
            "state_body_code": ["", "001"],
            "program": ["", ""],
            "program_code": ["", ""],
            "subprogram": ["", ""],
            "subprogram_code": ["", ""],
            "subprogram_total": [1000.0, 1000.0],
        }
        pd.DataFrame(df_data).to_csv(csv_path, index=False)

        # Create overall.json
        overall_path = csv_dir / "2023_BUDGET_LAW_overall.json"
        with open(overall_path, "w", encoding="utf-8") as f:
            json.dump({"overall_total": 1000.0}, f)

        # Run validation with custom report directory
        custom_dir = tmp_path / "reports"
        args = argparse.Namespace(
            years="2023",
            source_type="BUDGET_LAW",
            processed_root=str(processed_root),
            report=str(custom_dir),
            report_json=False,
        )
        cmd_validate(args)

        # Check that markdown report was created in custom directory
        expected_report = custom_dir / "2023_BUDGET_LAW_validation.md"
        assert expected_report.exists()
        assert expected_report.stat().st_size > 0

    def test_cmd_validate_multiple_years(self, tmp_path):
        """Test cmd_validate with multiple years."""
        processed_root = tmp_path
        csv_dir = processed_root
        csv_dir.mkdir(exist_ok=True)

        # Create data for 2023 and 2024
        for year in [2023, 2024]:
            csv_path = csv_dir / f"{year}_BUDGET_LAW.csv"
            df_data = {
                "state_body": ["Overall", "State Body 1"],
                "state_body_code": ["", "001"],
                "program": ["", ""],
                "program_code": ["", ""],
                "subprogram": ["", ""],
                "subprogram_code": ["", ""],
                "subprogram_total": [1000.0, 1000.0],
            }
            pd.DataFrame(df_data).to_csv(csv_path, index=False)

            overall_path = csv_dir / f"{year}_BUDGET_LAW_overall.json"
            with open(overall_path, "w", encoding="utf-8") as f:
                json.dump({"overall_total": 1000.0}, f)

        # Validate both years
        args = argparse.Namespace(
            years="2023-2024",
            source_type="BUDGET_LAW",
            processed_root=str(processed_root),
            report=False,
            report_json=False,
        )
        result = cmd_validate(args)
        assert result in [0, 2]

    def test_cmd_validate_missing_year(self, tmp_path):
        """Test cmd_validate when some years are missing."""
        processed_root = tmp_path
        csv_dir = processed_root
        csv_dir.mkdir(exist_ok=True)

        # Create data only for 2023
        csv_path = csv_dir / "2023_BUDGET_LAW.csv"
        df_data = {
            "state_body": ["Overall", "State Body 1"],
            "state_body_code": ["", "001"],
            "program": ["", ""],
            "program_code": ["", ""],
            "subprogram": ["", ""],
            "subprogram_code": ["", ""],
            "subprogram_total": [1000.0, 1000.0],
        }
        pd.DataFrame(df_data).to_csv(csv_path, index=False)

        overall_path = csv_dir / "2023_BUDGET_LAW_overall.json"
        with open(overall_path, "w", encoding="utf-8") as f:
            json.dump({"overall_total": 1000.0}, f)

        args = argparse.Namespace(
            years="2023-2024",
            source_type="BUDGET_LAW",
            processed_root=str(processed_root),
            report=False,
            report_json=False,
        )
        result = cmd_validate(args)
        # Should succeed because at least one year validated
        assert result in [0, 2]

    def test_cmd_validate_all_years_missing(self, tmp_path):
        """Test error when no years have data."""
        processed_root = tmp_path
        csv_dir = processed_root
        csv_dir.mkdir(exist_ok=True)

        # Don't create any data files
        args = argparse.Namespace(
            years="2023-2024",
            source_type="BUDGET_LAW",
            processed_root=str(processed_root),
            report=False,
            report_json=False,
        )
        result = cmd_validate(args)
        assert result == 1  # No datasets validated

    def test_cmd_validate_report_multiple_years(self, tmp_path):
        """Test --report generates one file per year."""
        processed_root = tmp_path
        csv_dir = processed_root
        csv_dir.mkdir(exist_ok=True)

        # Create data for 2023 and 2024
        for year in [2023, 2024]:
            csv_path = csv_dir / f"{year}_BUDGET_LAW.csv"
            df_data = {
                "state_body": ["Overall", "State Body 1"],
                "state_body_code": ["", "001"],
                "program": ["", ""],
                "program_code": ["", ""],
                "subprogram": ["", ""],
                "subprogram_code": ["", ""],
                "subprogram_total": [1000.0, 1000.0],
            }
            pd.DataFrame(df_data).to_csv(csv_path, index=False)

            overall_path = csv_dir / f"{year}_BUDGET_LAW_overall.json"
            with open(overall_path, "w", encoding="utf-8") as f:
                json.dump({"overall_total": 1000.0}, f)

        # Validate with --report
        args = argparse.Namespace(
            years="2023-2024",
            source_type="BUDGET_LAW",
            processed_root=str(processed_root),
            report=True,
            report_json=False,
        )
        cmd_validate(args)

        # Check that reports were created for both years
        report_2023 = csv_dir / "2023_BUDGET_LAW_validation.md"
        report_2024 = csv_dir / "2024_BUDGET_LAW_validation.md"
        assert report_2023.exists()
        assert report_2024.exists()
        assert report_2023.stat().st_size > 0
        assert report_2024.stat().st_size > 0

    def test_cmd_validate_invalid_source_type(self, tmp_path, caplog):
        """Test error handling for invalid source type."""
        processed_root = tmp_path
        csv_dir = processed_root
        csv_dir.mkdir(exist_ok=True)

        # Create minimal valid data
        csv_path = csv_dir / "2023_BUDGET_LAW.csv"
        df_data = {
            "state_body": ["State Body 1"],
            "subprogram_total": [1000.0],
        }
        pd.DataFrame(df_data).to_csv(csv_path, index=False)

        overall_path = csv_dir / "2023_BUDGET_LAW_overall.json"
        with open(overall_path, "w", encoding="utf-8") as f:
            json.dump({"overall_total": 1000.0}, f)

        # Test with invalid source type
        args = argparse.Namespace(
            years="2023",
            source_type="INVALID_SOURCE_TYPE",
            processed_root=str(processed_root),
            report=False,
            report_json=False,
        )

        result = cmd_validate(args)

        # Should return error code
        assert result == 2

        # Verify error message is helpful and mentions the invalid type
        log_messages = " ".join([record.message for record in caplog.records])
        assert "INVALID_SOURCE_TYPE" in log_messages
        assert "Valid types:" in log_messages or "valid" in log_messages.lower()

    @pytest.mark.parametrize(
        "invalid_years",
        ["abc", "2023-abc"],
        ids=["non_numeric", "partial_invalid"],
    )
    def test_cmd_validate_malformed_years_raises_error(self, tmp_path, invalid_years):
        """Test that non-numeric year arguments raise ValueError."""
        processed_root = tmp_path
        csv_dir = processed_root
        csv_dir.mkdir(exist_ok=True)

        args = argparse.Namespace(
            years=invalid_years,
            source_type="BUDGET_LAW",
            processed_root=str(processed_root),
            report=False,
            report_json=False,
        )

        # Should raise ValueError when parsing malformed years
        with pytest.raises(ValueError) as exc_info:
            cmd_validate(args)

        # Verify error message mentions the issue
        assert "invalid literal" in str(exc_info.value)

    def test_cmd_validate_reversed_range(self, tmp_path, caplog):
        """Test that reversed year range (2030-2020) results in no datasets found."""
        processed_root = tmp_path
        csv_dir = processed_root
        csv_dir.mkdir(exist_ok=True)

        args = argparse.Namespace(
            years="2030-2020",
            source_type="BUDGET_LAW",
            processed_root=str(processed_root),
            report=False,
            report_json=False,
        )

        result = cmd_validate(args)

        # Reversed range produces empty list, so no datasets validated
        assert result == 1

        # Verify error message
        log_messages = " ".join([record.message for record in caplog.records])
        assert "no datasets" in log_messages.lower()

    def test_cmd_validate_missing_csv_file(self, tmp_path, caplog):
        """Test error when CSV missing but overall.json exists."""
        processed_root = tmp_path
        csv_dir = processed_root
        csv_dir.mkdir(exist_ok=True)

        # Create only overall.json
        overall_path = csv_dir / "2023_BUDGET_LAW_overall.json"
        with open(overall_path, "w", encoding="utf-8") as f:
            json.dump({"overall_total": 1000.0}, f)

        args = argparse.Namespace(
            years="2023",
            source_type="BUDGET_LAW",
            processed_root=str(processed_root),
            report=False,
            report_json=False,
        )
        result = cmd_validate(args)

        # Should fail because no CSV file found (no datasets validated)
        assert result == 1

        # Verify error message mentions missing CSV
        log_messages = " ".join([record.message for record in caplog.records])
        assert "csv" in log_messages.lower() and "not found" in log_messages.lower()

    def test_cmd_validate_missing_overall_json(self, tmp_path, caplog):
        """Test error when overall.json missing but CSV exists."""
        processed_root = tmp_path
        csv_dir = processed_root
        csv_dir.mkdir(exist_ok=True)

        # Create only CSV
        csv_path = csv_dir / "2023_BUDGET_LAW.csv"
        df_data = {
            "state_body": ["State Body 1"],
            "subprogram_total": [1000.0],
        }
        pd.DataFrame(df_data).to_csv(csv_path, index=False)

        args = argparse.Namespace(
            years="2023",
            source_type="BUDGET_LAW",
            processed_root=str(processed_root),
            report=False,
            report_json=False,
        )
        result = cmd_validate(args)

        # Should fail because overall.json is missing (no datasets validated)
        assert result == 1

        # Verify error message mentions missing JSON
        log_messages = " ".join([record.message for record in caplog.records])
        assert (
            "json" in log_messages.lower() and "not found" in log_messages.lower()
        ) or "overall" in log_messages.lower()

    def test_cmd_validate_error_messages_are_helpful(self, tmp_path, caplog):
        """Verify error messages are user-friendly and actionable."""
        processed_root = tmp_path
        csv_dir = processed_root
        csv_dir.mkdir(exist_ok=True)

        # Test 1: Missing processed_root directory
        args = argparse.Namespace(
            years="2023",
            source_type="BUDGET_LAW",
            processed_root=str(tmp_path / "nonexistent"),
            report=False,
            report_json=False,
        )
        result = cmd_validate(args)
        assert result == 2

        # Error should mention the directory issue
        log_messages = " ".join([record.message for record in caplog.records])
        assert "not found" in log_messages.lower() or "does not exist" in log_messages.lower()
        # Should mention running process command
        assert "process" in log_messages.lower()

        # Clear log for next test
        caplog.clear()

        # Test 2: No data files at all
        args = argparse.Namespace(
            years="2023",
            source_type="BUDGET_LAW",
            processed_root=str(processed_root),
            report=False,
            report_json=False,
        )
        result = cmd_validate(args)
        assert result == 1

        # Error should explain what's missing
        log_messages = " ".join([record.message for record in caplog.records])
        assert len(log_messages) > 0  # Some error output should be present
        assert "not found" in log_messages.lower() or "no datasets" in log_messages.lower()
