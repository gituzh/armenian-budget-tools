from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, cast
import yaml


@dataclass(frozen=True)
class SourceDefinition:
    """Definition of a data source entry."""

    name: str
    year: int
    source_type: str  # "spending_q1", "spending_q12", "spending_q123", "spending_q1234"
    url: str
    file_format: Optional[str] = None  # Optional override: "zip", "rar", "xlsx", etc.
    description: str = ""
    checksum: Optional[str] = None
    checksum_updated_at: Optional[str] = None


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
        for item in entries:
            sources.append(
                SourceDefinition(
                    name=str(item.get("name", "")),
                    year=int(item.get("year")),
                    source_type=str(item.get("source_type", "")),
                    url=str(item.get("url", "")),
                    file_format=str(item.get("file_format", "")),
                    description=str(item.get("description", "")),
                    checksum=item.get("checksum"),
                    checksum_updated_at=item.get("checksum_updated_at"),
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
