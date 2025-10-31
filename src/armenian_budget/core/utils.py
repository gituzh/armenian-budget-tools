"""Core utility functions for Armenian Budget Tools.

This module provides shared utilities used across the project:
- Filename parsing and source type detection
"""

from __future__ import annotations

from pathlib import Path

from armenian_budget.core.enums import SourceType


def detect_source_type(csv_path: Path) -> SourceType:
    """Detect source type from CSV filename.

    Parses filenames following the convention: {year}_{SOURCE_TYPE}.csv

    Args:
        csv_path: Path to CSV file (e.g., "2023_BUDGET_LAW.csv").

    Returns:
        SourceType enum value extracted from filename.

    Raises:
        ValueError: If filename doesn't match expected format or source type is invalid.

    Examples:
        >>> detect_source_type(Path("2023_BUDGET_LAW.csv"))
        SourceType.BUDGET_LAW
        >>> detect_source_type(Path("data/2024_SPENDING_Q1.csv"))
        SourceType.SPENDING_Q1
    """
    stem = csv_path.stem  # Get filename without extension
    parts = stem.split("_", 1)  # Split on first underscore only

    if len(parts) != 2:
        raise ValueError(
            f"Invalid CSV filename format: '{csv_path.name}'. "
            f"Expected format: {{year}}_{{SOURCE_TYPE}}.csv"
        )

    year_part, source_part = parts

    # Validate year part is numeric
    if not year_part.isdigit():
        raise ValueError(
            f"Invalid year in filename: '{year_part}'. "
            f"Expected numeric year in format: {{year}}_{{SOURCE_TYPE}}.csv"
        )

    # Try to convert source_part to SourceType
    try:
        return SourceType(source_part)
    except ValueError as exc:
        valid_types = ", ".join(t.value for t in SourceType)
        raise ValueError(
            f"Unknown source type: '{source_part}'. "
            f"Valid types: {valid_types}"
        ) from exc
