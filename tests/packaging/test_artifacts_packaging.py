from __future__ import annotations

import importlib.util
import json
import sys
import tomllib
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_ARTIFACTS_PATH = REPO_ROOT / "scripts" / "build_artifacts.py"
BUILD_ARTIFACTS_SPEC = importlib.util.spec_from_file_location(
    "build_artifacts", BUILD_ARTIFACTS_PATH
)
assert BUILD_ARTIFACTS_SPEC is not None
assert BUILD_ARTIFACTS_SPEC.loader is not None
build_artifacts = importlib.util.module_from_spec(BUILD_ARTIFACTS_SPEC)
sys.modules[BUILD_ARTIFACTS_SPEC.name] = build_artifacts
BUILD_ARTIFACTS_SPEC.loader.exec_module(build_artifacts)


def test_data_skill_exists() -> None:
    skill_root = REPO_ROOT / "skills" / "armenian-budget-data"

    assert skill_root.is_dir()
    assert not skill_root.is_symlink()
    assert (skill_root / "SKILL.md").is_file()
    assert (skill_root / "agents" / "openai.yaml").is_file()
    assert (skill_root / "scripts" / "data_availability.py").is_file()


def test_project_version_is_readable_for_skill_artifacts() -> None:
    project = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert project["project"]["version"]


def test_processed_artifact_allowlist_includes_gdp_snapshots(tmp_path: Path) -> None:
    data_root = tmp_path / "processed"
    data_root.mkdir()
    included_files = [
        "2024_BUDGET_LAW.csv",
        "2024_BUDGET_LAW_overall.json",
        "2024_BUDGET_LAW_GDP.json",
        "2024_BUDGET_LAW_validation.json",
        "2024_BUDGET_LAW_validation.md",
    ]
    excluded_files = [
        ".DS_Store",
        "2024_BUDGET_LAW_notes.txt",
        "2024_BUDGET_LAW_GDP.md",
    ]
    for name in included_files + excluded_files:
        (data_root / name).write_text("", encoding="utf-8")

    artifacts = build_artifacts.iter_processed_artifacts(data_root)

    assert [path.name for path in artifacts] == sorted(included_files)


def test_data_version_counts_gdp_snapshots(tmp_path: Path, monkeypatch) -> None:
    repo_root = tmp_path
    data_root = repo_root / "data" / "processed"
    data_root.mkdir(parents=True)
    (data_root / "2024_BUDGET_LAW.csv").write_text("", encoding="utf-8")
    (data_root / "2024_BUDGET_LAW_GDP.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(build_artifacts, "git_metadata", lambda _repo_root: {})

    data_version = build_artifacts.build_data_version(repo_root, "0.1.0")

    assert data_version["file_count"] == 2
    assert data_version["primary_csv_count"] == 1
    assert {
        file_info["path"] for file_info in data_version["files"]
    } == {
        "data/processed/2024_BUDGET_LAW.csv",
        "data/processed/2024_BUDGET_LAW_GDP.json",
    }


def test_skill_version_paths_exist_in_archive(
    tmp_path: Path, monkeypatch
) -> None:
    repo_root = tmp_path
    skill_root = repo_root / "skills" / "armenian-budget-data"
    data_root = repo_root / "data" / "processed"
    build_dir = tmp_path / "build"
    skill_root.mkdir(parents=True)
    data_root.mkdir(parents=True)
    (skill_root / "SKILL.md").write_text(
        "\n".join(
            [
                "# Test skill",
                "2. Resolve the active parsed-data root:",
                "   - use `ARMENIAN_BUDGET_DATA_PATH` if set",
                "   - otherwise use bundled `assets/data` when this skill is packaged with data",
                "   - otherwise use repo `data/processed`",
                "   - if neither exists, fail clearly",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (data_root / "2024_BUDGET_LAW.csv").write_text("x\n", encoding="utf-8")
    monkeypatch.setattr(build_artifacts, "git_metadata", lambda _repo_root: {})

    context = build_artifacts.build_context(
        repo_root, build_dir, tmp_path / "dist", "0.1.0"
    )
    artifact = build_artifacts.build_skill(context)

    assert artifact.path.name == "armenian-budget-data-skill-0.1.0.zip"

    with zipfile.ZipFile(artifact.path) as archive:
        names = set(archive.namelist())
        skill_text = archive.read("SKILL.md").decode("utf-8")
        version = json.loads(archive.read("assets/DATA_VERSION.json"))

    assert (build_dir / "armenian-budget-data" / "assets" / "data").is_dir()
    assert (
        build_dir / "armenian-budget-data" / "assets" / "DATA_VERSION.json"
    ).is_file()
    assert "- otherwise use bundled `assets/data`\n" in skill_text
    assert "otherwise use repo `data/processed`" not in skill_text
    assert version["data_root"] == "assets/data"
    assert [file_info["path"] for file_info in version["files"]] == [
        "assets/data/2024_BUDGET_LAW.csv"
    ]
    assert all(file_info["path"] in names for file_info in version["files"])
    assert "assets/DATA_VERSION.json" in names


def test_data_archive_uses_flat_data_directory(tmp_path: Path, monkeypatch) -> None:
    repo_root = tmp_path
    data_root = repo_root / "data" / "processed"
    data_root.mkdir(parents=True)
    (data_root / "2024_BUDGET_LAW.csv").write_text("x\n", encoding="utf-8")
    monkeypatch.setattr(build_artifacts, "git_metadata", lambda _repo_root: {})

    context = build_artifacts.build_context(
        repo_root, tmp_path / "build", tmp_path / "dist", "0.1.0"
    )
    artifact = build_artifacts.build_data_archive(context)

    assert artifact.path.name == "armenian-budget-data-0.1.0.zip"

    with zipfile.ZipFile(artifact.path) as archive:
        names = set(archive.namelist())
        version = json.loads(archive.read("DATA_VERSION.json"))

    assert (tmp_path / "build" / "data-archive" / "data").is_dir()
    assert (tmp_path / "build" / "data-archive" / "DATA_VERSION.json").is_file()
    assert version["data_root"] == "data"
    assert [file_info["path"] for file_info in version["files"]] == [
        "data/2024_BUDGET_LAW.csv"
    ]
    assert "DATA_VERSION.json" in names
    assert "data/2024_BUDGET_LAW.csv" in names
