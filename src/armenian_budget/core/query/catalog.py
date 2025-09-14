from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional
import json


DATA_PROCESSED_CSV = Path("data/processed/csv")


@dataclass
class DatasetEntry:
    year: int
    source_type: str
    path: Path
    row_count_approx: Optional[int]
    file_size_bytes: Optional[int]
    last_modified_iso: Optional[str]


def list_datasets(
    *, years: Optional[Iterable[int]] = None, source_types: Optional[Iterable[str]] = None
) -> List[DatasetEntry]:
    """List datasets by scanning data/processed/csv.

    Returns quick, approximate information; avoids loading the files.
    """
    years_set = set(int(y) for y in years) if years else None
    types_set = set(s.upper() for s in source_types) if source_types else None

    out: List[DatasetEntry] = []
    if not DATA_PROCESSED_CSV.exists():
        return out

    for f in DATA_PROCESSED_CSV.glob("*.csv"):
        name = f.name
        try:
            year_part, type_part_with_ext = name.split("_", 1)
            stype = type_part_with_ext[:-4]
            year = int(year_part)
        except Exception:
            continue

        if years_set and year not in years_set:
            continue
        if types_set and stype.upper() not in types_set:
            continue

        stat = f.stat()
        try:
            # cheap line count estimate without reading full file into memory
            with f.open("r", encoding="utf-8") as fh:
                rows = max(0, sum(1 for _ in fh) - 1)
        except Exception:
            rows = None

        out.append(
            DatasetEntry(
                year=year,
                source_type=stype.upper(),
                path=f,
                row_count_approx=rows,
                file_size_bytes=stat.st_size if stat else None,
                last_modified_iso=None,
            )
        )
    return out


def _schema_card_path(csv_path: Path) -> Path:
    return csv_path.with_suffix(".schema.json")


def get_dataset_schema(year: int, source_type: str) -> Dict:
    """Return schema card if present; otherwise minimal info.

    Looks for a sibling schema JSON next to the CSV.
    """
    csv_path = DATA_PROCESSED_CSV / f"{int(year)}_{str(source_type).upper()}.csv"
    schema_path = _schema_card_path(csv_path)
    if schema_path.exists():
        try:
            return json.loads(schema_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "year": int(year),
        "source_type": str(source_type).upper(),
        "file_path": str(csv_path),
        "schema_uri": str(schema_path),
        "columns": None,
        "dtypes": None,
        "roles": None,
        "shape": None,
        "sample_rows": None,
    }
