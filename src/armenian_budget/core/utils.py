"""Core utility functions for Armenian Budget Tools.

This module provides shared utilities used across the project.
"""

from __future__ import annotations

from pathlib import Path

from armenian_budget.core.enums import SourceType


def get_processed_paths(
    year: int, source_type: SourceType, processed_root: Path
) -> tuple[Path, Path]:
    """Get CSV and overall.json paths for a given year and source type.

    Constructs file paths following the standard naming convention:
    - CSV: {processed_root}/csv/{year}_{SOURCE_TYPE}.csv
    - JSON: {processed_root}/csv/{year}_{SOURCE_TYPE}_overall.json

    Args:
        year: The year of the budget data (e.g., 2023).
        source_type: The source type (e.g., BUDGET_LAW, SPENDING_Q1).
        processed_root: Path to the processed data root directory.

    Returns:
        A tuple of (csv_path, overall_path).

    Examples:
        >>> from pathlib import Path
        >>> from armenian_budget.core.enums import SourceType
        >>> csv_path, overall_path = get_processed_paths(
        ...     2023, SourceType.BUDGET_LAW, Path("data/processed")
        ... )
        >>> print(csv_path)
        data/processed/csv/2023_BUDGET_LAW.csv
        >>> print(overall_path)
        data/processed/csv/2023_BUDGET_LAW_overall.json
    """
    csv_dir = processed_root / "csv"
    csv_path = csv_dir / f"{year}_{source_type.value}.csv"
    overall_path = csv_dir / f"{year}_{source_type.value}_overall.json"
    return csv_path, overall_path
