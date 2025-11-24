"""Unit tests for run_validation() and get_processed_paths()."""

from __future__ import annotations

import json
from pathlib import Path
import pandas as pd
import pytest
from armenian_budget.core.enums import SourceType
from armenian_budget.core.utils import get_processed_paths
from armenian_budget.validation import run_validation
from armenian_budget.validation.models import ValidationReport


class TestGetProcessedPaths:
    """Tests for get_processed_paths() utility function."""

    def test_get_processed_paths_basic(self):
        """Test that get_processed_paths() constructs correct paths."""
        processed_root = Path("data/processed")
        csv_path, overall_path = get_processed_paths(2023, SourceType.BUDGET_LAW, processed_root)

        assert csv_path == Path("data/processed/2023_BUDGET_LAW.csv")
        assert overall_path == Path("data/processed/2023_BUDGET_LAW_overall.json")

    @pytest.mark.parametrize(
        "year,source_type,expected_csv,expected_json",
        [
            (
                2019,
                SourceType.SPENDING_Q1,
                "2019_SPENDING_Q1.csv",
                "2019_SPENDING_Q1_overall.json",
            ),
            (
                2023,
                SourceType.BUDGET_LAW,
                "2023_BUDGET_LAW.csv",
                "2023_BUDGET_LAW_overall.json",
            ),
            (
                2025,
                SourceType.SPENDING_Q123,
                "2025_SPENDING_Q123.csv",
                "2025_SPENDING_Q123_overall.json",
            ),
        ],
    )
    def test_get_processed_paths_parametrized(self, year, source_type, expected_csv, expected_json):
        """Test path construction for different years and source types."""
        processed_root = Path("/tmp/test")
        csv_path, overall_path = get_processed_paths(year, source_type, processed_root)

        assert csv_path.name == expected_csv
        assert overall_path.name == expected_json
        assert csv_path.parent == Path("/tmp/test")
        assert overall_path.parent == Path("/tmp/test")


class TestRunValidation:
    """Tests for run_validation() function."""

    def test_run_validation_missing_processed_root(self, tmp_path):
        """Test that FileNotFoundError is raised if processed_root doesn't exist."""
        non_existent = tmp_path / "nonexistent"

        with pytest.raises(FileNotFoundError, match="Processed data root not found"):
            run_validation(2023, SourceType.BUDGET_LAW, non_existent)

    def test_run_validation_missing_csv(self, tmp_path):
        """Test that FileNotFoundError is raised if CSV file doesn't exist."""
        processed_root = tmp_path
        (processed_root).mkdir(parents=True, exist_ok=True)

        with pytest.raises(FileNotFoundError, match="CSV file not found"):
            run_validation(2023, SourceType.BUDGET_LAW, processed_root)

    def test_run_validation_missing_overall_json(self, tmp_path):
        """Test that FileNotFoundError is raised if overall.json doesn't exist."""
        processed_root = tmp_path
        csv_dir = processed_root
        csv_dir.mkdir(parents=True, exist_ok=True)

        # Create CSV but not overall.json
        csv_path = csv_dir / "2023_BUDGET_LAW.csv"
        pd.DataFrame({"state_body": ["Test"]}).to_csv(csv_path, index=False)

        with pytest.raises(FileNotFoundError, match="Overall JSON file not found"):
            run_validation(2023, SourceType.BUDGET_LAW, processed_root)

    def test_run_validation_invalid_csv(self, tmp_path):
        """Test that ValueError is raised if CSV is malformed."""
        processed_root = tmp_path
        csv_dir = processed_root
        csv_dir.mkdir(parents=True, exist_ok=True)

        # Create malformed CSV
        csv_path = csv_dir / "2023_BUDGET_LAW.csv"
        csv_path.write_text("invalid,csv\n,data,extra,columns\n1,2,3,4,5,6,7,8")

        # Create valid overall.json
        overall_path = csv_dir / "2023_BUDGET_LAW_overall.json"
        overall_path.write_text('{"total": 100}')

        # Malformed CSV should raise ValueError
        with pytest.raises(ValueError, match="Failed to read CSV file"):
            run_validation(2023, SourceType.BUDGET_LAW, processed_root)

    def test_run_validation_invalid_json(self, tmp_path):
        """Test that ValueError is raised if overall.json is malformed."""
        processed_root = tmp_path
        csv_dir = processed_root
        csv_dir.mkdir(parents=True, exist_ok=True)

        # Create valid CSV
        csv_path = csv_dir / "2023_BUDGET_LAW.csv"
        pd.DataFrame({"state_body": ["Test"]}).to_csv(csv_path, index=False)

        # Create malformed JSON
        overall_path = csv_dir / "2023_BUDGET_LAW_overall.json"
        overall_path.write_text("{invalid json")

        with pytest.raises(ValueError, match="Failed to read overall JSON file"):
            run_validation(2023, SourceType.BUDGET_LAW, processed_root)

    def test_run_validation_success_minimal(self, tmp_path):
        """Test successful validation with minimal valid data."""
        processed_root = tmp_path
        csv_dir = processed_root
        csv_dir.mkdir(parents=True, exist_ok=True)

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
        report = run_validation(2023, SourceType.BUDGET_LAW, processed_root)

        # Verify report structure
        assert isinstance(report, ValidationReport)
        assert report.source_type == SourceType.BUDGET_LAW
        assert report.csv_path == csv_path
        assert report.overall_path == overall_path
        assert len(report.results) > 0

    @pytest.mark.parametrize(
        "source_type",
        [
            SourceType.BUDGET_LAW,
            SourceType.SPENDING_Q1,
            SourceType.SPENDING_Q12,
            SourceType.SPENDING_Q123,
            SourceType.SPENDING_Q1234,
        ],
    )
    def test_run_validation_different_source_types(self, source_type, tmp_path):
        """Test that run_validation handles different source types correctly."""
        processed_root = tmp_path
        csv_dir = processed_root
        csv_dir.mkdir(parents=True, exist_ok=True)

        # Create minimal CSV with columns appropriate for source type
        csv_path = csv_dir / f"2023_{source_type.value}.csv"

        # Base columns (common to all types)
        df_data = {
            "state_body": ["Overall", "State Body 1"],
            "state_body_code": ["", "001"],
            "program": ["", ""],
            "program_code": ["", ""],
            "subprogram": ["", ""],
            "subprogram_code": ["", ""],
        }

        # Add source-specific columns
        if source_type == SourceType.BUDGET_LAW:
            df_data["subprogram_total"] = [1000.0, 1000.0]
        else:  # SPENDING types
            df_data.update(
                {
                    "subprogram_annual_plan": [1000.0, 1000.0],
                    "subprogram_rev_annual_plan": [1000.0, 1000.0],
                    "subprogram_actual": [800.0, 800.0],
                    "subprogram_actual_vs_annual_plan": [80.0, 80.0],
                    "subprogram_actual_vs_rev_annual_plan": [80.0, 80.0],
                }
            )

        pd.DataFrame(df_data).to_csv(csv_path, index=False)

        # Create overall.json
        overall_path = csv_dir / f"2023_{source_type.value}_overall.json"
        overall_data = {"overall_total": 1000.0}
        with open(overall_path, "w", encoding="utf-8") as f:
            json.dump(overall_data, f)

        # Run validation
        report = run_validation(2023, source_type, processed_root)

        # Verify report
        assert isinstance(report, ValidationReport)
        assert report.source_type == source_type
        assert len(report.results) > 0


class TestRunValidationIntegration:
    """Integration tests using real data if available."""

    def test_run_validation_with_real_data_if_exists(self):
        """Integration test using real processed data if available."""
        # Try to use real data
        processed_root = Path(__file__).parent.parent.parent / "data/processed"

        if not processed_root.exists():
            pytest.skip("No processed data available for integration test")

        # Try 2023 BUDGET_LAW as it's commonly available
        csv_path = processed_root / "2023_BUDGET_LAW.csv"
        if not csv_path.exists():
            pytest.skip("2023 BUDGET_LAW data not available")

        # Run validation
        report = run_validation(2023, SourceType.BUDGET_LAW, processed_root)

        # Verify report structure
        assert isinstance(report, ValidationReport)
        assert report.csv_path.exists()
        assert report.overall_path.exists()
        assert len(report.results) > 0

        # Should have results from multiple checks
        check_ids = {result.check_id for result in report.results}
        assert len(check_ids) > 0
