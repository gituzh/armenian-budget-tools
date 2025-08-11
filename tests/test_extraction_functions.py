"""Tests for the budget extraction functions themselves."""

import pytest
import tempfile
import pandas as pd
import os
from armenian_budget.ingestion.parsers import (
    flatten_budget_excel_2019_2024,
    flatten_budget_excel_2025,
    SourceType,
    RowType,
    _detect_row_type_2019_2024,
    _detect_row_type_2025,
    _extract_subprogram_code,
    _parse_fraction,
    # alias helpers for legacy names used in tests
    is_numeric as _is_numeric,
    normalize_str as _normalize_str,
)


class TestUtilityFunctions:
    """Test utility functions used by the extraction functions."""

    def test_is_numeric(self):
        """Test the _is_numeric function."""
        assert _is_numeric("123") is True
        assert _is_numeric("123.45") is True
        assert _is_numeric("-123.45") is True
        assert _is_numeric("0") is True
        assert _is_numeric("") is False
        assert _is_numeric("abc") is False
        assert _is_numeric("123abc") is False

    def test_normalize_str(self):
        """Test the _normalize_str function."""
        assert _normalize_str("  Hello World  ") == "helloworld"
        assert _normalize_str("UPPERCASE") == "uppercase"
        assert _normalize_str("Mixed Case") == "mixedcase"
        assert _normalize_str("") == ""

    def test_parse_fraction(self):
        """Test the _parse_fraction function."""
        assert _parse_fraction("50") == 0.5
        assert _parse_fraction("50%") == 0.5
        assert _parse_fraction("100") == 1.0
        assert _parse_fraction("0") == 0.0
        assert _parse_fraction("-") == 0.0
        assert _parse_fraction("abc") == 0.0
        assert abs(_parse_fraction("33.33") - 0.3333) < 0.0001

    def test_extract_subprogram_code(self):
        """Test the _extract_subprogram_code function."""
        assert _extract_subprogram_code("123") == 123
        assert _extract_subprogram_code("123.0") == 123
        assert _extract_subprogram_code("1154-11001") == 11001
        assert _extract_subprogram_code("  456  ") == 456


class TestRowTypeDetection:
    """Test row type detection functions."""

    def test_detect_row_type_2019_2024_grand_total(self):
        """Test detection of grand total rows."""
        row = ["", "", "ԸՆԴԱՄԵՆԸ", "1000000"]
        assert _detect_row_type_2019_2024(row) == RowType.GRAND_TOTAL

        row = ["", "", "ընդամենը", "1000000"]  # lowercase
        assert _detect_row_type_2019_2024(row) == RowType.GRAND_TOTAL

    def test_detect_row_type_2019_2024_state_body_header(self):
        """Test detection of state body header rows."""
        row = ["", "", "Some State Body", "500000"]
        assert _detect_row_type_2019_2024(row) == RowType.STATE_BODY_HEADER

    def test_detect_row_type_2019_2024_program_header(self):
        """Test detection of program header rows."""
        row = ["1001", "", "Program Name", "100000"]
        assert _detect_row_type_2019_2024(row) == RowType.PROGRAM_HEADER

    def test_detect_row_type_2019_2024_subprogram_header(self):
        """Test detection of subprogram header rows."""
        row = ["", "1001", "Subprogram Name", "50000"]
        assert _detect_row_type_2019_2024(row) == RowType.SUBPROGRAM_HEADER

        row = ["", "1154-11001", "Compound Code Subprogram", "50000"]
        assert _detect_row_type_2019_2024(row) == RowType.SUBPROGRAM_HEADER

    def test_detect_row_type_2019_2024_detail_line(self):
        """Test detection of detail line rows."""
        row = ["", "", "Some description", ""]
        assert _detect_row_type_2019_2024(row) == RowType.DETAIL_LINE

    def test_detect_row_type_2019_2024_empty(self):
        """Test detection of empty rows."""
        row = ["", "", "", ""]
        assert _detect_row_type_2019_2024(row) == RowType.EMPTY

        row = ["   ", "  ", "", "   "]
        assert _detect_row_type_2019_2024(row) == RowType.EMPTY

    def test_detect_row_type_2025_grand_total(self):
        """Test detection of 2025 grand total rows."""
        row = ["ԸՆԴԱՄԵՆԸ", "", "", "", "", "", "1000000"]
        assert _detect_row_type_2025(row) == RowType.GRAND_TOTAL

    def test_detect_row_type_2025_state_body_header(self):
        """Test detection of 2025 state body header rows."""
        row = ["State Body Name", "", "", "", "", "", "500000"]
        assert _detect_row_type_2025(row) == RowType.STATE_BODY_HEADER

    def test_detect_row_type_2025_program_header(self):
        """Test detection of 2025 program header rows."""
        row = ["", "1001", "", "Program Name", "Goal", "", "100000"]
        assert _detect_row_type_2025(row) == RowType.PROGRAM_HEADER

    def test_detect_row_type_2025_subprogram_header(self):
        """Test detection of 2025 subprogram header rows."""
        row = ["", "", "1154-11001", "Subprogram", "Description", "Type", "50000"]
        assert _detect_row_type_2025(row) == RowType.SUBPROGRAM_HEADER


class TestExtractionFunctionInputValidation:
    """Test input validation for extraction functions."""

    def test_invalid_file_path(self):
        """Test handling of invalid file paths."""
        with pytest.raises(FileNotFoundError):
            flatten_budget_excel_2019_2024("nonexistent_file.xlsx")

        with pytest.raises(FileNotFoundError):
            flatten_budget_excel_2025("nonexistent_file.xlsx")

    def test_invalid_source_type(self):
        """Test handling of invalid source types."""
        # Create a temporary valid Excel file
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
            df.to_excel(tmp.name, index=False, header=False)
            tmp_path = tmp.name

        try:
            # This should work with valid source type
            with pytest.raises(SystemExit):  # Expected to fail due to invalid data format
                flatten_budget_excel_2019_2024(tmp_path, SourceType.BUDGET_LAW)

            # Test with invalid source type would require creating an invalid enum value
            # which isn't easily testable

        finally:
            os.unlink(tmp_path)


class TestMockDataExtraction:
    """Test extraction functions with mock data."""

    def create_mock_budget_excel_2019_2024(self, source_type=SourceType.BUDGET_LAW):
        """Create a mock Excel file for 2019-2024 format testing."""
        if source_type == SourceType.BUDGET_LAW:
            data = [
                ["", "", "ԸՆԴԱՄԵՆԸ", 1000000],  # Grand total
                ["", "", "State Body 1", 600000],  # State body
                [1001, "", "Program 1", 300000],  # Program
                ["", "", "Program Name", ""],  # Program name detail
                ["", "", "ծրագրինպատակը", ""],  # Program goal label
                ["", "", "Program Goal", ""],  # Program goal detail
                ["", "", "վերջնականարդյունքինկարագրությունը", ""],  # Result label
                ["", "", "Result Description", ""],  # Result detail
                ["", "", "Ծրագրի միջոցառումներ", ""],  # Subprogram marker
                ["", 1001001, "Subprogram 1", 150000],  # Subprogram
                ["", "", "Subprogram Name", ""],  # Subprogram name detail
                ["", "", "միջոցառմաննկարագրությունը", ""],  # Subprogram desc label
                ["", "", "Subprogram Description", ""],  # Subprogram desc detail
                ["", "", "միջոցառմանտեսակը", ""],  # Subprogram type label
                ["", "", "Subprogram Type", ""],  # Subprogram type detail
                ["", 1001002, "Subprogram 2", 150000],  # Another subprogram
                ["", "", "Subprogram Name 2", ""],
                ["", "", "միջոցառմաննկարագրությունը", ""],
                ["", "", "Subprogram Description 2", ""],
                ["", "", "միջոցառմանտեսակը", ""],
                ["", "", "Subprogram Type 2", ""],
                [1002, "", "Program 2", 300000],  # Another program
                ["", "", "Program Name 2", ""],
                ["", "", "ծրագրինպատակը", ""],
                ["", "", "Program Goal 2", ""],
                ["", "", "վերջնականարդյունքինկարագրությունը", ""],
                ["", "", "Result Description 2", ""],
                ["", "", "Ծրագրի միջոցառումներ", ""],  # Subprogram marker
                ["", 1002001, "Subprogram 3", 300000],
                ["", "", "Subprogram Name 3", ""],
                ["", "", "միջոցառմաննկարագրությունը", ""],
                ["", "", "Subprogram Description 3", ""],
                ["", "", "միջոցառմանտեսակը", ""],
                ["", "", "Subprogram Type 3", ""],
                ["", "", "State Body 2", 400000],  # Another state body
                [2001, "", "Program 3", 400000],
                ["", "", "Program Name 3", ""],
                ["", "", "ծրագրինպատակը", ""],
                ["", "", "Program Goal 3", ""],
                ["", "", "վերջնականարդյունքինկարագրությունը", ""],
                ["", "", "Result Description 3", ""],
                ["", "", "Ծրագրի միջոցառումներ", ""],  # Subprogram marker
                ["", 2001001, "Subprogram 4", 400000],
                ["", "", "Subprogram Name 4", ""],
                ["", "", "միջոցառմաննկարագրությունը", ""],
                ["", "", "Subprogram Description 4", ""],
                ["", "", "միջոցառմանտեսակը", ""],
                ["", "", "Subprogram Type 4", ""],
            ]
        else:
            # For spending reports, add more columns
            data = [
                ["", "", "ԸՆԴԱՄԵՆԸ", 1000000, 1100000, 800000, 850000, 750000, 0.68, 0.88],
                ["", "", "State Body 1", 600000, 650000, 480000, 510000, 450000, 0.69, 0.88],
                [1001, "", "Program 1", 300000, 325000, 240000, 255000, 225000, 0.69, 0.88],
                ["", "", "Program Name", "", "", "", "", "", "", ""],
                ["", "", "ծրագրինպատակը", "", "", "", "", "", "", ""],
                ["", "", "Program Goal", "", "", "", "", "", "", ""],
                ["", "", "վերջնականարդյունքինկարագրությունը", "", "", "", "", "", "", ""],
                ["", "", "Result Description", "", "", "", "", "", "", ""],
                ["", "", "Ծրագրի միջոցառումներ", "", "", "", "", "", "", ""],  # Subprogram marker
                ["", 1001001, "Subprogram 1", 150000, 162500, 120000, 127500, 112500, 0.69, 0.88],
                ["", "", "Subprogram Name", "", "", "", "", "", "", ""],
                ["", "", "միջոցառմաննկարագրությունը", "", "", "", "", "", "", ""],
                ["", "", "Subprogram Description", "", "", "", "", "", "", ""],
                ["", "", "միջոցառմանտեսակը", "", "", "", "", "", "", ""],
                ["", "", "Subprogram Type", "", "", "", "", "", "", ""],
            ]

        # Create DataFrame and save to temporary file
        df = pd.DataFrame(data)

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            df.to_excel(tmp.name, index=False, header=False)
            return tmp.name

    def test_budget_law_extraction_basic(self):
        """Test basic budget law extraction functionality."""
        tmp_file = self.create_mock_budget_excel_2019_2024(SourceType.BUDGET_LAW)

        try:
            df, overall, rowtype_stats, statetrans_stats = flatten_budget_excel_2019_2024(
                tmp_file, SourceType.BUDGET_LAW
            )

            # Basic assertions
            assert isinstance(df, pd.DataFrame)
            assert len(df) > 0
            assert "state_body" in df.columns
            assert "program_code" in df.columns
            assert "subprogram_code" in df.columns
            assert "subprogram_total" in df.columns

            # Check overall values
            assert isinstance(overall, dict)
            assert "overall_total" in overall
            assert overall["overall_total"] == 1000000

            # Check statistics
            assert isinstance(rowtype_stats, dict)
            assert isinstance(statetrans_stats, dict)
            assert rowtype_stats[RowType.GRAND_TOTAL] >= 1

        finally:
            os.unlink(tmp_file)

    def test_spending_extraction_basic(self):
        """Test basic spending report extraction functionality."""
        tmp_file = self.create_mock_budget_excel_2019_2024(SourceType.SPENDING_Q1)

        try:
            df, overall, rowtype_stats, statetrans_stats = flatten_budget_excel_2019_2024(
                tmp_file, SourceType.SPENDING_Q1
            )

            # Basic assertions
            assert isinstance(df, pd.DataFrame)
            assert len(df) > 0

            # Check spending-specific columns
            assert "subprogram_annual_plan" in df.columns
            assert "subprogram_actual" in df.columns
            assert "subprogram_actual_vs_rev_annual_plan" in df.columns

            # Check overall values structure for spending
            assert isinstance(overall, dict)
            assert "overall_actual" in overall

        finally:
            os.unlink(tmp_file)


class TestErrorHandling:
    """Test error handling in extraction functions."""

    def test_empty_excel_file(self):
        """Test handling of empty Excel files."""
        # Create empty Excel file
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            df = pd.DataFrame()
            df.to_excel(tmp.name, index=False, header=False)
            tmp_path = tmp.name

        try:
            with pytest.raises(SystemExit):
                flatten_budget_excel_2019_2024(tmp_path, SourceType.BUDGET_LAW)
        finally:
            os.unlink(tmp_path)

    def test_malformed_excel_data(self):
        """Test handling of malformed Excel data."""
        # Create Excel with invalid structure
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            df = pd.DataFrame(
                {"A": ["random", "data", "without"], "B": ["proper", "budget", "structure"]}
            )
            df.to_excel(tmp.name, index=False, header=False)
            tmp_path = tmp.name

        try:
            with pytest.raises(SystemExit):
                flatten_budget_excel_2019_2024(tmp_path, SourceType.BUDGET_LAW)
        finally:
            os.unlink(tmp_path)
