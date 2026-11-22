import zipfile
from pathlib import Path

from armenian_budget.core.utils import list_version_dirs
from armenian_budget.interfaces.cli.main import main
from armenian_budget.sources.downloader import _category_and_subdir


def test_subdir_unlabelled_unchanged():
    root = Path("original")

    assert _category_and_subdir(root, 2026, "budget_law") == (
        root / "budget_laws" / "2026",
        None,
    )
    assert _category_and_subdir(root, 2026, "spending_q1") == (
        root / "spending_reports" / "2026" / "Q1",
        "Q1",
    )
    assert _category_and_subdir(root, 2026, "mtep") == (root / "mtep" / "2026", None)


def test_subdir_labelled():
    root = Path("original")

    assert _category_and_subdir(root, 2026, "budget_law", "EDRAFT") == (
        root / "budget_laws" / "2026_EDRAFT",
        None,
    )
    assert _category_and_subdir(root, 2026, "spending_q1", "X") == (
        root / "spending_reports" / "2026_X" / "Q1",
        "Q1",
    )
    assert _category_and_subdir(root, 2026, "mtep", "X") == (
        root / "mtep" / "2026_X",
        None,
    )
    assert _category_and_subdir(root, 2026, "unknown", "X") == (
        root / "other" / "2026_X",
        None,
    )


def test_list_version_dirs(tmp_path):
    for name in ["2026", "2026_EDRAFT", "2026_DRAFT2", "2026_old-copy", "2025_EDRAFT"]:
        (tmp_path / name).mkdir()
    (tmp_path / "2026_FILE").write_text("not a folder")

    assert list_version_dirs(tmp_path, 2026) == [None, "DRAFT2", "EDRAFT"]
    assert list_version_dirs(tmp_path, 2025) == ["EDRAFT"]
    assert list_version_dirs(tmp_path, 2024) == []
    assert list_version_dirs(tmp_path / "missing", 2026) == []


def _zip(path: Path, member: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr(member, "x")


def test_extract_covers_labelled_folders(tmp_path):
    original = tmp_path / "original"
    extracted = tmp_path / "extracted"
    laws = original / "budget_laws"
    _zip(laws / "2026" / "a.zip", "a.txt")
    _zip(laws / "2026_EDRAFT" / "b.zip", "b.txt")
    _zip(laws / "2026_old-copy" / "c.zip", "c.txt")
    _zip(laws / "2025_EDRAFT" / "d.zip", "d.txt")

    exit_code = main(
        [
            "extract",
            "--original-root",
            str(original),
            "--extracted-root",
            str(extracted),
        ]
    )

    assert exit_code == 0
    out = extracted / "budget_laws"
    assert (out / "2026" / "a" / "a.txt").exists()
    assert (out / "2026_EDRAFT" / "b" / "b.txt").exists()
    # a year that only has a labelled folder is still found
    assert (out / "2025_EDRAFT" / "d" / "d.txt").exists()
    assert not (out / "2026_old-copy").exists()


def test_extract_with_years_covers_labelled_folders(tmp_path):
    original = tmp_path / "original"
    extracted = tmp_path / "extracted"
    laws = original / "budget_laws"
    _zip(laws / "2026" / "a.zip", "a.txt")
    _zip(laws / "2026_EDRAFT" / "b.zip", "b.txt")
    _zip(laws / "2025_EDRAFT" / "d.zip", "d.txt")

    exit_code = main(
        [
            "extract",
            "--years",
            "2026",
            "--original-root",
            str(original),
            "--extracted-root",
            str(extracted),
        ]
    )

    assert exit_code == 0
    out = extracted / "budget_laws"
    assert (out / "2026" / "a" / "a.txt").exists()
    assert (out / "2026_EDRAFT" / "b" / "b.txt").exists()
    assert not (out / "2025_EDRAFT").exists()
