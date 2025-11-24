"""Unit tests for the validation registry and runner."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from armenian_budget.core.enums import SourceType
from armenian_budget.validation import run_validation
from armenian_budget.validation.models import CheckResult, ValidationReport
from armenian_budget.validation.registry import ALL_CHECKS


@pytest.fixture
def mock_processed_data(tmp_path: Path) -> Path:
    """Create a temporary directory with minimal valid processed data."""
    processed_root = tmp_path
    csv_dir = processed_root / "csv"
    csv_dir.mkdir(parents=True)

    csv_path = csv_dir / "2023_BUDGET_LAW.csv"
    pd.DataFrame({"state_body": ["Test"]}).to_csv(csv_path, index=False)

    overall_path = csv_dir / "2023_BUDGET_LAW_overall.json"
    overall_path.write_text('{"overall_total": 1000.0}')

    return processed_root


def test_run_validation_filters_checks_by_source_type(mock_processed_data: Path):  # pylint: disable=redefined-outer-name
    """
    Test that run_validation() correctly filters checks based on source_type.
    `ALL_CHECKS` is a list of INSTANCES, so we patch it with mock INSTANCES.
    """
    mock_instances = []
    # `original_instance` is an item from the real ALL_CHECKS list
    for original_instance in ALL_CHECKS:
        # Create a mock instance that has the same interface as the original
        mock_instance = MagicMock(spec=original_instance)
        mock_instance.validate.return_value = []

        # Configure the mock's applicability to match the real one
        applies = original_instance.applies_to_source_type(SourceType.BUDGET_LAW)
        mock_instance.applies_to_source_type.return_value = applies

        mock_instances.append(mock_instance)

    # Patch ALL_CHECKS with our list of mock instances
    with patch("armenian_budget.validation.registry.ALL_CHECKS", mock_instances):
        run_validation(2023, SourceType.BUDGET_LAW, mock_processed_data)

    # Verify that 'validate' was called only for the applicable mock instances
    for mock_instance in mock_instances:
        if mock_instance.applies_to_source_type.return_value:
            mock_instance.validate.assert_called_once()
        else:
            mock_instance.validate.assert_not_called()


def test_run_validation_aggregates_results(mock_processed_data: Path):  # pylint: disable=redefined-outer-name
    """
    Test that run_validation() correctly aggregates results into a ValidationReport.
    """
    # Define results
    result1_pass = CheckResult(check_id="check1", passed=True, fail_count=0, severity="warning")
    result2_error = CheckResult(
        check_id="check2",
        passed=False,
        fail_count=1,
        severity="error",
        messages=["An error occurred"],
    )
    result3_warning = CheckResult(
        check_id="check3",
        passed=False,
        fail_count=2,
        severity="warning",
        messages=["A warning occurred"],
    )

    # Create mock instances and configure them directly
    mock_instance_1 = MagicMock()
    mock_instance_1.applies_to_source_type.return_value = True
    mock_instance_1.validate.return_value = [result1_pass]

    mock_instance_2 = MagicMock()
    mock_instance_2.applies_to_source_type.return_value = True
    mock_instance_2.validate.return_value = [result2_error]

    mock_instance_3 = MagicMock()
    mock_instance_3.applies_to_source_type.return_value = True
    mock_instance_3.validate.return_value = [result3_warning]

    mock_instance_skipped = MagicMock()
    mock_instance_skipped.applies_to_source_type.return_value = False

    mock_instances = [mock_instance_1, mock_instance_2, mock_instance_3, mock_instance_skipped]

    with patch("armenian_budget.validation.registry.ALL_CHECKS", mock_instances):
        report = run_validation(2023, SourceType.BUDGET_LAW, mock_processed_data)

    # Assertions
    assert isinstance(report, ValidationReport)
    assert len(report.results) == 3
    assert report.get_error_count() == 1
    assert report.get_warning_count() == 2

    passed_count = sum(1 for r in report.results if r.passed)
    assert passed_count == 1

    check_ids_in_report = {res.check_id for res in report.results}
    assert {"check1", "check2", "check3"} == check_ids_in_report

    # Ensure the validate method on the skipped mock was not called
    mock_instance_skipped.validate.assert_not_called()
