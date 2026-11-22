"""Core utility functions for Armenian Budget Tools.

This module provides shared utilities used across the project.
"""

from __future__ import annotations

import re
from pathlib import Path

from armenian_budget.core.enums import SourceType

LABEL_RE = re.compile(r"^[A-Z0-9]+$")
# GDP would collide with {year}_{SOURCE_TYPE}_GDP.json
RESERVED_LABELS = frozenset({"GDP"})


def validate_label(label: str) -> str:
    """Return a valid source label unchanged, or raise ValueError."""
    if not LABEL_RE.match(label):
        raise ValueError(f"invalid label {label!r}: must match {LABEL_RE.pattern}")
    if label in RESERVED_LABELS:
        raise ValueError(f"label {label!r} is reserved")
    return label


def year_dir_name(year: int, label: str | None = None) -> str:
    """Year folder of a version: "2026", or "2026_EDRAFT" when labelled."""
    return f"{year}_{label}" if label else str(year)


def list_version_dirs(category_root: Path, year: int) -> list[str | None]:
    """Labels of the version folders of a year under a category root.

    Looks for ``<year>`` and ``<year>_<LABEL>`` folders: None first when
    ``<year>`` exists, then labels sorted. Other names are ignored.
    """
    if not category_root.is_dir():
        return []
    versions: list[str | None] = []
    if (category_root / str(year)).is_dir():
        versions.append(None)
    prefix = f"{year}_"
    versions.extend(
        sorted(
            p.name[len(prefix) :]
            for p in category_root.iterdir()
            if p.is_dir()
            and p.name.startswith(prefix)
            and LABEL_RE.match(p.name[len(prefix) :])
        )
    )
    return versions


def dataset_stem(year: int, source_type_name: str, label: str | None = None) -> str:
    """File-name stem of a dataset: {year}_{SOURCE_TYPE}[_{LABEL}]."""
    stem = f"{year}_{source_type_name}"
    return f"{stem}_{label}" if label else stem


def get_processed_paths(
    year: int,
    source_type: SourceType,
    processed_root: Path,
    label: str | None = None,
) -> tuple[Path, Path]:
    """Get CSV and overall.json paths for a given year and source type.

    Constructs file paths following the standard naming convention:
    - CSV: {processed_root}/{year}_{SOURCE_TYPE}[_{LABEL}].csv
    - JSON: {processed_root}/{year}_{SOURCE_TYPE}[_{LABEL}]_overall.json

    Args:
        year: The year of the budget data (e.g., 2023).
        source_type: The source type (e.g., BUDGET_LAW, SPENDING_Q1).
        processed_root: Path to the processed data root directory.
        label: Source label of the version; None for the unlabelled one.

    Returns:
        A tuple of (csv_path, overall_path).

    Examples:
        >>> from pathlib import Path
        >>> from armenian_budget.core.enums import SourceType
        >>> csv_path, overall_path = get_processed_paths(
        ...     2023, SourceType.BUDGET_LAW, Path("data/processed")
        ... )
        >>> print(csv_path)
        data/processed/2023_BUDGET_LAW.csv
        >>> print(overall_path)
        data/processed/2023_BUDGET_LAW_overall.json
    """
    stem = dataset_stem(year, source_type.value, label)
    return processed_root / f"{stem}.csv", processed_root / f"{stem}_overall.json"
