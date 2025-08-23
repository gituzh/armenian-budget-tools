from __future__ import annotations

from pathlib import Path
from typing import Optional

import polars as pl

from .catalog import DATA_PROCESSED_CSV


def resolve_csv(year: int, source_type: str) -> Path:
    path = DATA_PROCESSED_CSV / f"{int(year)}_{str(source_type).upper()}.csv"
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    return path


def scan_dataset(year: int, source_type: str, *, has_header: bool = True) -> pl.LazyFrame:
    """Return a LazyFrame scanning the dataset without materializing."""
    csv_path = resolve_csv(year, source_type)
    return pl.scan_csv(str(csv_path), has_header=has_header)


