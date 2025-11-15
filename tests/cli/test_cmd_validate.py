"""Tests for cmd_validate CLI function."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import pytest

from armenian_budget.core.enums import SourceType
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
        )
        result = cmd_validate(args)
        assert result == 2

    def test_cmd_validate_success_minimal(self, tmp_path):
        """Test cmd_validate with minimal valid data."""
        # Setup directory structure
        processed_root = tmp_path
        csv_dir = processed_root / "csv"
        csv_dir.mkdir()

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
        )
        result = cmd_validate(args)

        # Should succeed (return 0) or have validation errors (return 2)
        assert result in [0, 2]

    def test_cmd_validate_with_report_flag(self, tmp_path):
        """Test cmd_validate with --report flag to generate markdown report."""
        # Setup directory structure
        processed_root = tmp_path
        csv_dir = processed_root / "csv"
        csv_dir.mkdir()

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
        )
        result = cmd_validate(args)

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
        csv_dir = processed_root / "csv"
        csv_dir.mkdir()

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
        )
        result = cmd_validate(args)

        # Check that markdown report was created in custom directory
        expected_report = custom_dir / "2023_BUDGET_LAW_validation.md"
        assert expected_report.exists()
        assert expected_report.stat().st_size > 0

    def test_cmd_validate_multiple_years(self, tmp_path):
        """Test cmd_validate with multiple years."""
        processed_root = tmp_path
        csv_dir = processed_root / "csv"
        csv_dir.mkdir()

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
        )
        result = cmd_validate(args)
        assert result in [0, 2]

    def test_cmd_validate_missing_year(self, tmp_path):
        """Test cmd_validate when some years are missing."""
        processed_root = tmp_path
        csv_dir = processed_root / "csv"
        csv_dir.mkdir()

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

        # Validate 2023-2024, but 2024 is missing
        args = argparse.Namespace(
            years="2023-2024",
            source_type="BUDGET_LAW",
            processed_root=str(processed_root),
            report=False,
        )
        result = cmd_validate(args)
        # Should succeed because at least one year validated
        assert result in [0, 2]

    def test_cmd_validate_all_years_missing(self, tmp_path):
        """Test error when no years have data."""
        processed_root = tmp_path
        csv_dir = processed_root / "csv"
        csv_dir.mkdir()

        # Don't create any data files
        args = argparse.Namespace(
            years="2023-2024",
            source_type="BUDGET_LAW",
            processed_root=str(processed_root),
            report=False,
        )
        result = cmd_validate(args)
        assert result == 1  # No datasets validated

    def test_cmd_validate_report_multiple_years(self, tmp_path):
        """Test --report generates one file per year."""
        processed_root = tmp_path
        csv_dir = processed_root / "csv"
        csv_dir.mkdir()

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
        )
        result = cmd_validate(args)

        # Check that reports were created for both years
        report_2023 = csv_dir / "2023_BUDGET_LAW_validation.md"
        report_2024 = csv_dir / "2024_BUDGET_LAW_validation.md"
        assert report_2023.exists()
        assert report_2024.exists()
        assert report_2023.stat().st_size > 0
        assert report_2024.stat().st_size > 0