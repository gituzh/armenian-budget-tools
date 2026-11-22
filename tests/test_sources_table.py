from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from armenian_budget.sources.registry import SourceRegistry

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "build_sources_table.py"
SCRIPT_SPEC = importlib.util.spec_from_file_location("build_sources_table", SCRIPT_PATH)
assert SCRIPT_SPEC is not None
assert SCRIPT_SPEC.loader is not None
build_sources_table = importlib.util.module_from_spec(SCRIPT_SPEC)
sys.modules[SCRIPT_SPEC.name] = build_sources_table
SCRIPT_SPEC.loader.exec_module(build_sources_table)

HEADER = [
    "| Year | Budget law | Budget-law drafts | Spending reports | MTEP |",
    "|---|---|---|---|---|",
]
START = "<!-- sources-table:start -->"
END = "<!-- sources-table:end -->"


def _entry(
    year: int,
    source_type: str,
    label: str | None = None,
    published: str | None = None,
) -> str:
    name = f"{year}_{source_type}" + (f"_{label.lower()}" if label else "")
    lines = [
        f'  - name: "{name}"',
        f"    year: {year}",
        f'    source_type: "{source_type}"',
        f'    url: "https://example.test/{name}.rar"',
    ]
    if label:
        lines.append(f'    label: "{label}"')
    if published:
        lines.append(f"    published: {published}")
    return "\n".join(lines)


def _write_sources(path: Path, *entries: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("sources:\n" + "\n".join(entries) + "\n", encoding="utf-8")
    return path


def _rows(tmp_path: Path, *entries: str) -> list[str]:
    registry = SourceRegistry(_write_sources(tmp_path / "sources.yaml", *entries))
    lines = build_sources_table.build_sources_table(registry).split("\n")
    assert lines[:2] == HEADER
    return lines[2:]


def _repo(tmp_path: Path, readme: str, *entries: str) -> Path:
    _write_sources(tmp_path / "config" / "sources.yaml", *entries)
    (tmp_path / "README.md").write_text(readme, encoding="utf-8")
    return tmp_path


def test_readme_table_matches_sources_yaml() -> None:
    registry = SourceRegistry(REPO_ROOT / "config" / "sources.yaml")
    table = build_sources_table.build_sources_table(registry)
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert build_sources_table.replace_table_block(readme, table) == readme, (
        "README.md sources table is out of date; "
        "run: python scripts/build_sources_table.py"
    )


def test_one_row_per_year_in_year_order(tmp_path: Path) -> None:
    rows = _rows(
        tmp_path,
        _entry(2020, "budget_law"),
        _entry(2019, "budget_law"),
        _entry(2019, "spending_q1"),
    )

    assert rows == [
        "| 2019 | yes | – | Q1 | – |",
        "| 2020 | yes | – | – | – |",
    ]


def test_drafts_ordered_by_published_date_not_label_name(tmp_path: Path) -> None:
    rows = _rows(
        tmp_path,
        _entry(2026, "budget_law"),
        _entry(2026, "budget_law", "AAA", "2025-12-01"),
        _entry(2026, "budget_law", "ZZZ", "2025-10-01"),
        _entry(2026, "budget_law", "MMM", "2025-11-27"),
    )

    assert rows == ["| 2026 | yes | `ZZZ`, `MMM`, `AAA` | – | – |"]


def test_undated_drafts_come_last_in_registry_order(tmp_path: Path) -> None:
    rows = _rows(
        tmp_path,
        _entry(2020, "budget_law", "ZZZ"),
        _entry(2020, "budget_law", "AAA"),
        _entry(2020, "budget_law", "MMM", "2019-10-04"),
    )

    assert rows == ["| 2020 | – | `MMM`, `ZZZ`, `AAA` | – | – |"]


def test_drafts_with_equal_dates_keep_registry_order(tmp_path: Path) -> None:
    rows = _rows(
        tmp_path,
        _entry(2026, "budget_law", "ZZZ", "2025-10-01"),
        _entry(2026, "budget_law", "AAA", "2025-10-01"),
    )

    assert rows == ["| 2026 | – | `ZZZ`, `AAA` | – | – |"]


def test_year_with_only_a_labelled_budget_law(tmp_path: Path) -> None:
    rows = _rows(tmp_path, _entry(2027, "budget_law", "DRAFT", "2026-10-01"))

    assert rows == ["| 2027 | – | `DRAFT` | – | – |"]


def test_quarters_in_fixed_order_and_mtep(tmp_path: Path) -> None:
    rows = _rows(
        tmp_path,
        _entry(2024, "spending_q1234"),
        _entry(2024, "mtep"),
        _entry(2024, "spending_q12"),
        _entry(2024, "spending_q1"),
        _entry(2024, "spending_q123"),
    )

    assert rows == ["| 2024 | – | – | Q1, Q12, Q123, Q1234 | yes |"]


def test_multi_file_entry_counts_once(tmp_path: Path) -> None:
    entry = """\
  - name: "2026_budget_law_edraft"
    year: 2026
    source_type: "budget_law"
    label: "EDRAFT"
    files:
      - name: "a"
        url: "https://example.test/a.rar"
      - name: "b"
        url: "https://example.test/b.docx"\
"""

    assert _rows(tmp_path, entry) == ["| 2026 | – | `EDRAFT` | – | – |"]


def test_labelled_spending_and_mtep_versions_are_shown(tmp_path: Path) -> None:
    rows = _rows(
        tmp_path,
        _entry(2025, "spending_q1"),
        _entry(2025, "spending_q1", "X"),
        _entry(2025, "spending_q12", "Y"),
        _entry(2025, "mtep"),
        _entry(2025, "mtep", "X"),
        _entry(2026, "mtep", "X"),
    )

    assert rows == [
        "| 2025 | – | – | Q1 (`X`), Q12 (`Y` only) | yes (`X`) |",
        "| 2026 | – | – | – | `X` only |",
    ]


def test_unknown_source_type_is_an_error(tmp_path: Path) -> None:
    registry = SourceRegistry(
        _write_sources(tmp_path / "sources.yaml", _entry(2025, "audit_report"))
    )

    with pytest.raises(ValueError, match="audit_report"):
        build_sources_table.build_sources_table(registry)


def test_replace_table_block_changes_only_the_block() -> None:
    readme = f"# Title\n\nbefore\n{START}\nold\nrows\n{END}\nafter\n"

    result = build_sources_table.replace_table_block(readme, "| new |")

    assert result == f"# Title\n\nbefore\n{START}\n| new |\n{END}\nafter\n"


@pytest.mark.parametrize(
    "readme",
    [
        "no markers\n",
        f"{START}\nonly start\n",
        f"only end\n{END}\n",
        f"{END}\nwrong order\n{START}\n",
        f"{START}\n{END}\n{START}\n{END}\n",
    ],
)
def test_replace_table_block_requires_one_marker_pair(readme: str) -> None:
    with pytest.raises(ValueError, match="sources-table"):
        build_sources_table.replace_table_block(readme, "| new |")


def test_main_rewrites_only_the_block(tmp_path: Path) -> None:
    repo = _repo(
        tmp_path,
        f"intro\n{START}\nstale\n{END}\noutro\n",
        _entry(2027, "budget_law", "DRAFT"),
    )

    assert build_sources_table.main([], repo_root=repo) == 0

    table = "\n".join([*HEADER, "| 2027 | – | `DRAFT` | – | – |"])
    assert (repo / "README.md").read_text(encoding="utf-8") == (
        f"intro\n{START}\n{table}\n{END}\noutro\n"
    )


def test_check_passes_when_readme_is_in_sync(tmp_path: Path) -> None:
    repo = _repo(tmp_path, f"{START}\n{END}\n", _entry(2027, "budget_law", "DRAFT"))
    assert build_sources_table.main([], repo_root=repo) == 0

    assert build_sources_table.main(["--check"], repo_root=repo) == 0


def test_check_fails_without_writing_when_readme_differs(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    stale = f"intro\n{START}\nstale\n{END}\noutro\n"
    repo = _repo(tmp_path, stale, _entry(2027, "budget_law", "DRAFT"))

    assert build_sources_table.main(["--check"], repo_root=repo) == 1

    assert (repo / "README.md").read_text(encoding="utf-8") == stale
    message = capsys.readouterr().err
    assert message.count("\n") == 1
    assert "python scripts/build_sources_table.py" in message


@pytest.mark.parametrize("argv", [[], ["--check"]])
def test_main_fails_without_writing_when_markers_are_missing(
    tmp_path: Path, argv: list[str]
) -> None:
    repo = _repo(tmp_path, "no markers\n", _entry(2027, "budget_law", "DRAFT"))

    assert build_sources_table.main(argv, repo_root=repo) == 2

    assert (repo / "README.md").read_text(encoding="utf-8") == "no markers\n"
