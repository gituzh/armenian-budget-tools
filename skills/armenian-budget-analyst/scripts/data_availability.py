#!/usr/bin/env python3
"""Render a year-by-source availability matrix for processed datasets."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path


DEFAULT_COLUMN_ORDER = [
    "BUDGET_LAW",
    "BUDGET_LAW_GDP",
    "SPENDING_Q1",
    "SPENDING_Q12",
    "SPENDING_Q123",
    "SPENDING_Q1234",
    "SPENDING_Q1234_GDP",
    "MTEP",
]
PRIMARY_DATASET_RE = re.compile(r"^(?P<year>\d{4})_(?P<source_type>.+)\.csv$")
GDP_DATASET_RE = re.compile(
    r"^(?P<year>\d{4})_(?P<source_type>BUDGET_LAW|SPENDING_Q1234)_GDP\.json$"
)


def bundled_data_root_candidates() -> list[Path]:
    """Return bundled processed-data roots in preference order."""
    skill_root = Path(__file__).resolve().parents[1]
    repo_root = Path(__file__).resolve().parents[3]
    return [
        (skill_root / "assets" / "data" / "processed").resolve(),
        (repo_root / "data" / "processed").resolve(),
    ]


def resolve_data_root(cli_value: str | None) -> Path:
    """Resolve the active processed-data root."""
    if cli_value:
        data_root = Path(cli_value).expanduser()
    elif os.environ.get("ARMENIAN_BUDGET_DATA_PATH"):
        data_root = Path(os.environ["ARMENIAN_BUDGET_DATA_PATH"]).expanduser()
    else:
        for candidate in bundled_data_root_candidates():
            if candidate.exists() and candidate.is_dir():
                data_root = candidate
                break
        else:
            data_root = bundled_data_root_candidates()[-1]

    data_root = data_root.resolve()
    if not data_root.exists() or not data_root.is_dir():
        raise FileNotFoundError(
            f"Resolved data root does not exist or is not a directory: {data_root}. "
            "Pass --data-root or set ARMENIAN_BUDGET_DATA_PATH."
        )
    return data_root


def iter_processed_datasets(data_root: Path) -> list[tuple[int, str, str]]:
    """Collect processed dataset artifacts from the data root."""
    datasets: list[tuple[int, str, str]] = []
    for path in sorted(data_root.iterdir()):
        if not path.is_file():
            continue

        if path.suffix.lower() == ".csv":
            match = PRIMARY_DATASET_RE.match(path.name)
            if not match:
                continue

            source_type = match.group("source_type")
            if source_type.endswith("_overall") or source_type.endswith("_validation"):
                continue

            datasets.append((int(match.group("year")), source_type, path.name))
        elif path.suffix.lower() == ".json":
            match = GDP_DATASET_RE.match(path.name)
            if match:
                datasets.append(
                    (
                        int(match.group("year")),
                        f"{match.group('source_type')}_GDP",
                        path.name,
                    )
                )
    return datasets


def build_matrix(data_root: Path) -> tuple[list[str], list[dict[str, str | int]]]:
    """Build the availability matrix."""
    datasets = iter_processed_datasets(data_root)
    unknown_columns = sorted(
        {
            source_type
            for _, source_type, _ in datasets
            if source_type not in DEFAULT_COLUMN_ORDER
        }
    )
    columns = DEFAULT_COLUMN_ORDER + unknown_columns

    years = sorted({year for year, _, _ in datasets})
    rows: list[dict[str, str | int]] = []
    for year in years:
        row: dict[str, str | int] = {"year": year}
        for column in columns:
            row[column] = "-"
        for dataset_year, source_type, basename in datasets:
            if dataset_year == year:
                row[source_type] = basename
        rows.append(row)

    return columns, rows


def render_markdown(
    data_root: Path, columns: list[str], rows: list[dict[str, str | int]]
) -> str:
    """Render the matrix as Markdown."""
    header = ["Year"] + columns
    lines = [
        f"Data root: `{data_root}`",
        "",
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for row in rows:
        values = [str(row["year"])] + [str(row[column]) for column in columns]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def build_payload(
    data_root: Path, columns: list[str], rows: list[dict[str, str | int]]
) -> dict[str, object]:
    """Build the JSON payload."""
    return {
        "data_root": str(data_root),
        "columns": columns,
        "rows": rows,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a year-by-source availability matrix for processed datasets."
    )
    parser.add_argument("--data-root", help="Override the processed data root.")
    parser.add_argument(
        "--format",
        choices=("markdown", "json", "both"),
        default="markdown",
        help="Output format.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        data_root = resolve_data_root(args.data_root)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    columns, rows = build_matrix(data_root)
    markdown_output = render_markdown(data_root, columns, rows)
    json_output = json.dumps(build_payload(data_root, columns, rows), indent=2)

    if args.format == "markdown":
        print(markdown_output)
    elif args.format == "json":
        print(json_output)
    else:
        print(markdown_output)
        print()
        print(json_output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
