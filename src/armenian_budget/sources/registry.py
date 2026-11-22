from __future__ import annotations

import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, List, Optional, cast
import yaml

from armenian_budget.core.utils import validate_label


@dataclass(frozen=True)
class SourceDefinition:
    """Definition of a data source entry."""

    name: str
    year: int
    source_type: str  # "spending_q1", "spending_q12", "spending_q123", "spending_q1234"
    url: str
    file_format: Optional[str] = None  # Optional override: "zip", "rar", "xlsx", etc.
    filename: Optional[str] = None
    description: str = ""
    checksum: Optional[str] = None
    checksum_updated_at: Optional[str] = None
    label: str | None = None  # None: the unlabelled version
    published: datetime.date | None = None  # first seen on the site; display only


def _entry_label(item: dict) -> str | None:
    raw = item.get("label")
    if raw is None:
        return None
    try:
        return validate_label(str(raw))
    except ValueError as exc:
        raise ValueError(f"source {item.get('name')!r}: {exc}") from exc


def _entry_published(item: dict) -> datetime.date | None:
    raw: Any = item.get("published")
    if raw is None:
        return None
    if isinstance(raw, datetime.date) and not isinstance(raw, datetime.datetime):
        return raw
    try:
        return datetime.date.fromisoformat(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"source {item.get('name')!r}: invalid published date {raw!r} "
            "(expected YYYY-MM-DD)"
        ) from exc


class SourceRegistry:
    """Load and query source definitions from YAML."""

    def __init__(self, sources_file: Path) -> None:
        """Initialize the registry with a path to the sources YAML file."""
        self.sources_file = sources_file
        self._sources: List[SourceDefinition] = self._load_sources(sources_file)

    @staticmethod
    def _load_sources(sources_file: Path) -> List[SourceDefinition]:
        """Load and parse YAML into a list of SourceDefinition objects."""
        if not sources_file.exists():
            raise FileNotFoundError(f"Sources file not found: {sources_file}")
        with sources_file.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        entries = data.get("sources", []) or []
        sources: List[SourceDefinition] = []
        version_names: dict[tuple[int, str, str | None], str] = {}
        for item in entries:
            label = _entry_label(item)
            published = _entry_published(item)
            base = {
                "name": str(item.get("name", "")),
                "year": int(item.get("year")),
                "source_type": str(item.get("source_type", "")),
                "description": str(item.get("description", "")),
            }
            version = (base["year"], base["source_type"], label)
            first_name = version_names.setdefault(version, base["name"])
            if first_name != base["name"]:
                raise ValueError(
                    f"source {base['name']!r} repeats {version[0]} {version[1]} "
                    f"label {label!r} of source {first_name!r}"
                )
            files = item.get("files")
            if files is None:
                files = [item]
            for file_item in files:
                name = file_item.get("name") or base["name"]
                sources.append(
                    SourceDefinition(
                        name=str(name),
                        year=base["year"],
                        source_type=base["source_type"],
                        url=str(file_item.get("url", "")),
                        file_format=file_item.get("file_format", item.get("file_format")),
                        filename=file_item.get("filename"),
                        description=str(file_item.get("description", base["description"])),
                        checksum=file_item.get("checksum"),
                        checksum_updated_at=file_item.get("checksum_updated_at"),
                        label=label,
                        published=published,
                    )
                )
        return sources

    def all(self) -> List[SourceDefinition]:
        """Return all source definitions."""
        return list(self._sources)

    def for_years(self, years: Iterable[int]) -> List[SourceDefinition]:
        """Return sources that match any of the provided years."""
        years_set = set(int(y) for y in years)
        return [s for s in self._sources if s.year in years_set]

    def for_year(self, year: int) -> List[SourceDefinition]:
        """Return sources for a given year."""
        return [s for s in self._sources if s.year == int(year)]

    def published_by_label(
        self, year: int, source_type: str
    ) -> dict[str | None, datetime.date | None]:
        """Map each label of a year and source type to its published date.

        ``source_type`` is lower case as in YAML; key ``None`` is the
        unlabelled entry.
        """
        return {
            s.label: s.published
            for s in self._sources
            if s.year == int(year) and s.source_type == source_type
        }

    def filter(
        self,
        *,
        year: Optional[int] = None,
        source_types: Optional[Iterable[str]] = None,
    ) -> List[SourceDefinition]:
        """Filter sources by year and/or a set of source type names."""
        types_set: Optional[set[str]] = set(source_types) if source_types is not None else None
        result: List[SourceDefinition] = []
        for s in self._sources:
            if year is not None and s.year != int(year):
                continue
            if types_set is not None:
                allowed_types = cast(set[str], types_set)
                if s.source_type not in allowed_types:
                    continue
            result.append(s)
        return result
