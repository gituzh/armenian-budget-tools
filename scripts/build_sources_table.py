"""Build the README sources table from config/sources.yaml."""

from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

from armenian_budget.sources.registry import SourceDefinition, SourceRegistry

START_MARKER = "<!-- sources-table:start -->"
END_MARKER = "<!-- sources-table:end -->"
HEADER = (
    "| Year | Budget law | Budget-law drafts | Spending reports | MTEP |\n"
    "|---|---|---|---|---|"
)
QUARTERS = {
    "spending_q1": "Q1",
    "spending_q12": "Q12",
    "spending_q123": "Q123",
    "spending_q1234": "Q1234",
}
SOURCE_TYPES = {"budget_law", "mtep", *QUARTERS}
PRESENT = "yes"
ABSENT = "–"
REBUILD_COMMAND = "python scripts/build_sources_table.py"


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def registered_labels(
    sources: list[SourceDefinition], source_type: str
) -> list[str | None]:
    """Labels of one year's source type: by published date, undated last."""
    published: dict[str | None, datetime.date | None] = {}
    for source in sources:
        if source.source_type == source_type:
            published.setdefault(source.label, source.published)
    return sorted(
        published,
        key=lambda label: (
            published[label] is None,
            published[label] or datetime.date.min,
        ),
    )


def backticked(labels: list[str]) -> str:
    return ", ".join(f"`{label}`" for label in labels)


def version_cell(versions: list[str | None], name: str) -> str:
    """One source type's versions: ``Q1``, ``Q1 (`X`)`` or ``Q1 (`X` only)``.

    ``name`` stands for the unlabelled version; "only" marks its absence.
    """
    labels = [label for label in versions if label is not None]
    if not labels:
        return name if versions else ""
    if None in versions:
        return f"{name} ({backticked(labels)})"
    if name == PRESENT:
        return f"{backticked(labels)} only"
    return f"{name} ({backticked(labels)} only)"


def year_row(year: int, sources: list[SourceDefinition]) -> str:
    budget_law = registered_labels(sources, "budget_law")
    drafts = [label for label in budget_law if label is not None]
    quarters = [
        version_cell(registered_labels(sources, source_type), quarter)
        for source_type, quarter in QUARTERS.items()
    ]
    cells = [
        str(year),
        PRESENT if None in budget_law else ABSENT,
        backticked(drafts) or ABSENT,
        ", ".join(cell for cell in quarters if cell) or ABSENT,
        version_cell(registered_labels(sources, "mtep"), PRESENT) or ABSENT,
    ]
    return "| " + " | ".join(cells) + " |"


def build_sources_table(registry: SourceRegistry) -> str:
    """Return the Markdown sources table, one row per registered year."""
    by_year: dict[int, list[SourceDefinition]] = {}
    for source in registry.all():
        if source.source_type not in SOURCE_TYPES:
            raise ValueError(
                f"source {source.name!r}: no table column for source type "
                f"{source.source_type!r}"
            )
        by_year.setdefault(source.year, []).append(source)
    rows = [year_row(year, by_year[year]) for year in sorted(by_year)]
    return "\n".join([HEADER, *rows])


def replace_table_block(readme: str, table: str) -> str:
    """Return ``readme`` with the text between the markers replaced by ``table``."""
    if readme.count(START_MARKER) != 1 or readme.count(END_MARKER) != 1:
        raise ValueError(
            f"expected exactly one {START_MARKER} and one {END_MARKER} marker"
        )
    before, _, rest = readme.partition(START_MARKER)
    if END_MARKER in before:
        raise ValueError(f"{END_MARKER} comes before {START_MARKER}")
    _, _, after = rest.partition(END_MARKER)
    return f"{before}{START_MARKER}\n{table}\n{END_MARKER}{after}"


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if the README table is out of date; write nothing.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None, *, repo_root: Path | None = None) -> int:
    args = parse_args(argv)
    repo_root = repo_root or repo_root_from_script()
    readme_path = repo_root / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    registry = SourceRegistry(repo_root / "config" / "sources.yaml")
    try:
        updated = replace_table_block(readme, build_sources_table(registry))
    except ValueError as exc:
        print(f"error: {readme_path.name}: {exc}", file=sys.stderr)
        return 2

    if updated == readme:
        print(f"{readme_path.name} sources table is up to date")
        return 0
    if args.check:
        print(
            f"{readme_path.name} sources table is out of date; run: {REBUILD_COMMAND}",
            file=sys.stderr,
        )
        return 1
    readme_path.write_text(updated, encoding="utf-8")
    print(f"Updated the sources table in {readme_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
