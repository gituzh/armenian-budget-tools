"""Find versions of a dataset whose processed CSVs hold identical data.

This is information for the validation report, not a check: it never passes,
fails or changes counts.
"""

from __future__ import annotations

import datetime
import hashlib
from collections.abc import Mapping
from pathlib import Path

from armenian_budget.core.enums import SourceType
from armenian_budget.core.utils import get_processed_paths, list_processed_labels

Version = tuple[str | None, datetime.date | None]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_identical_versions(
    processed_root: Path,
    year: int,
    source_type: SourceType,
    label: str | None,
    published: Mapping[str | None, datetime.date | None],
) -> list[Version]:
    """List the versions whose CSV is byte-identical to ``label``'s CSV.

    Every version of the year and source type found in ``processed_root`` is
    compared, whatever a command run selected. The result includes ``label``
    itself and is empty when no other version matches.

    Order: by ``published`` date, oldest first; ties by label with the
    unlabelled version (None) first; versions without a date come last.
    """
    own_csv, _ = get_processed_paths(year, source_type, processed_root, label)
    if not own_csv.is_file():
        return []
    own_checksum = _sha256(own_csv)
    group: list[Version] = []
    for other in list_processed_labels(processed_root, year, source_type.value):
        csv_path, _ = get_processed_paths(year, source_type, processed_root, other)
        if other == label or _sha256(csv_path) == own_checksum:
            group.append((other, published.get(other)))
    if len(group) < 2:
        return []
    return sorted(
        group,
        key=lambda version: (
            version[1] is None,
            version[1] or datetime.date.min,
            version[0] is not None,
            version[0] or "",
        ),
    )


def format_identical_versions(versions: list[Version]) -> str:
    """Render a group as ``EDRAFT (2025-10-01), PARLIAMENT, (unlabelled)``."""
    parts = []
    for label, published in versions:
        name = label or "(unlabelled)"
        parts.append(f"{name} ({published.isoformat()})" if published else name)
    return ", ".join(parts)
