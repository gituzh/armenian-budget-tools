#!/usr/bin/env python3
"""Build release artifacts for Armenian Budget Tools."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


SKILL_NAME = "armenian-budget-data"
SKILL_ARCHIVE_NAME = "armenian-budget-data-skill"
DATA_ARCHIVE_NAME = "armenian-budget-data"
PRIMARY_DATASET_RE = re.compile(r"^\d{4}_[A-Z0-9_]+\.csv$")
PROCESSED_ARTIFACT_RE = re.compile(
    r"^(?:"
    r"\d{4}_[A-Z0-9_]+\.csv|"
    r"\d{4}_[A-Z0-9_]+_GDP\.json|"
    r"\d{4}_[A-Z0-9_]+_overall\.json|"
    r"\d{4}_[A-Z0-9_]+_validation\.(?:json|md)"
    r")$"
)
VERSION_RE = re.compile(r'^version\s*=\s*"(?P<version>[^"]+)"', re.MULTILINE)
EXCLUDE_NAMES = {".DS_Store"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo"}
EXCLUDE_DIRS = {"__pycache__"}
SKILL_DIR = Path("skills") / SKILL_NAME
BUNDLED_DATA_DIR = Path("assets") / "data"
DATA_VERSION_NAME = "DATA_VERSION.json"
DEFAULT_TARGETS = ["data", "skill"]
PACKAGED_SKILL_REPLACEMENTS = {
    (
        "   - use `ARMENIAN_BUDGET_DATA_PATH` if set\n"
        "   - otherwise use bundled `assets/data` when this skill is packaged with data\n"
        "   - otherwise use repo `data/processed`\n"
        "   - if neither exists, fail clearly"
    ): (
        "   - use `ARMENIAN_BUDGET_DATA_PATH` if set\n"
        "   - otherwise use bundled `assets/data`\n"
        "   - if neither exists, fail clearly"
    ),
}


@dataclass(frozen=True)
class Artifact:
    target: str
    path: Path
    sha256: str
    size_bytes: int


@dataclass(frozen=True)
class BuildContext:
    repo_root: Path
    build_dir: Path
    dist_dir: Path
    version: str
    generated_at: str
    source: dict[str, object]


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def read_project_version(repo_root: Path) -> str:
    pyproject = repo_root / "pyproject.toml"
    match = VERSION_RE.search(pyproject.read_text(encoding="utf-8"))
    if not match:
        raise ValueError(f"Could not read project version from {pyproject}")
    return match.group("version")


def run_git(repo_root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip()


def git_metadata(repo_root: Path) -> dict[str, object]:
    status = run_git(repo_root, "status", "--short")
    return {
        "commit": run_git(repo_root, "rev-parse", "HEAD"),
        "dirty": bool(status),
    }


def utc_timestamp() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def source_metadata(repo_root: Path, version: str) -> dict[str, object]:
    return {
        "project": "armenian-budget-tools",
        "project_version": version,
        "repository": "https://github.com/gituzh/armenian-budget-tools",
        **git_metadata(repo_root),
    }


def build_context(
    repo_root: Path, build_dir: Path, dist_dir: Path, version: str
) -> BuildContext:
    return BuildContext(
        repo_root=repo_root,
        build_dir=build_dir,
        dist_dir=dist_dir,
        version=version,
        generated_at=utc_timestamp(),
        source=source_metadata(repo_root, version),
    )


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue
        if path.name in EXCLUDE_NAMES or path.suffix in EXCLUDE_SUFFIXES:
            continue
        files.append(path)
    return files


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_processed_data(data_root: Path) -> list[Path]:
    if not data_root.exists() or not data_root.is_dir():
        raise FileNotFoundError(f"Processed data root not found: {data_root}")

    primary_csvs = [
        path for path in iter_files(data_root) if PRIMARY_DATASET_RE.match(path.name)
    ]
    if not primary_csvs:
        raise ValueError(f"No primary dataset CSVs found in {data_root}")
    return primary_csvs


def iter_processed_artifacts(data_root: Path) -> list[Path]:
    return [
        path
        for path in sorted(data_root.iterdir())
        if path.is_file()
        and should_copy(path)
        and PROCESSED_ARTIFACT_RE.match(path.name)
    ]


def relative_or_display(path: Path, root: Path) -> Path:
    try:
        return path.relative_to(root)
    except ValueError:
        return path


def build_data_version(
    repo_root: Path,
    version: str,
    data_root: Path | None = None,
    *,
    package_data_root: Path | None = None,
    generated_at: str | None = None,
    source: dict[str, object] | None = None,
) -> dict[str, object]:
    data_root = data_root or repo_root / "data" / "processed"
    package_data_root = package_data_root or relative_or_display(data_root, repo_root)
    primary_csvs = validate_processed_data(data_root)
    files = iter_processed_artifacts(data_root)
    return {
        "data_version": version,
        "generated_at": generated_at or utc_timestamp(),
        "source": source or source_metadata(repo_root, version),
        "data_root": str(package_data_root),
        "file_count": len(files),
        "primary_csv_count": len(primary_csvs),
        "files": [
            {
                "path": str(package_data_root / path.name),
                "size_bytes": path.stat().st_size,
                "sha256": file_sha256(path),
            }
            for path in files
        ],
    }


def should_copy(path: Path) -> bool:
    return (
        path.name not in EXCLUDE_NAMES
        and path.suffix not in EXCLUDE_SUFFIXES
        and not any(part in EXCLUDE_DIRS for part in path.parts)
    )


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(
        src,
        dst,
        ignore=lambda _dir, names: [
            name for name in names if not should_copy(Path(name))
        ],
    )


def copy_processed_artifacts(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    for path in iter_processed_artifacts(src):
        shutil.copy2(path, dst / path.name)


def clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def rewrite_packaged_skill(skill_path: Path) -> None:
    text = skill_path.read_text(encoding="utf-8")
    for old, new in PACKAGED_SKILL_REPLACEMENTS.items():
        if old not in text:
            raise ValueError(f"Expected packaged skill replacement text missing in {skill_path}")
        text = text.replace(old, new, 1)
    skill_path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    path.write_text(text, encoding="utf-8")


def display_path(path: Path, repo_root: Path) -> Path:
    try:
        return path.relative_to(repo_root)
    except ValueError:
        return path


def zip_directory(
    src_dir: Path, archive_path: Path, *, include_root: bool = True
) -> Artifact:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    if archive_path.exists():
        archive_path.unlink()

    with ZipFile(archive_path, "w", ZIP_DEFLATED) as archive:
        for path in iter_files(src_dir):
            if include_root:
                archive_name = path.relative_to(src_dir.parent)
            else:
                archive_name = path.relative_to(src_dir)
            archive.write(path, archive_name)

    return Artifact(
        target="",
        path=archive_path,
        sha256=file_sha256(archive_path),
        size_bytes=archive_path.stat().st_size,
    )


def build_data_archive(context: BuildContext) -> Artifact:
    staging_root = context.build_dir / "data-archive"
    staged_data_root = staging_root / "data"
    clean_dir(staging_root)
    copy_processed_artifacts(context.repo_root / "data" / "processed", staged_data_root)
    data_version = build_data_version(
        context.repo_root,
        context.version,
        staged_data_root,
        package_data_root=Path("data"),
        generated_at=context.generated_at,
        source=context.source,
    )
    write_json(staging_root / DATA_VERSION_NAME, data_version)
    artifact = zip_directory(
        staging_root,
        context.dist_dir / f"{DATA_ARCHIVE_NAME}-{context.version}.zip",
        include_root=False,
    )
    return Artifact("data", artifact.path, artifact.sha256, artifact.size_bytes)


def build_skill(context: BuildContext) -> Artifact:
    staging_root = context.build_dir / SKILL_NAME
    staged_data_root = staging_root / BUNDLED_DATA_DIR
    copy_tree(context.repo_root / SKILL_DIR, staging_root)
    rewrite_packaged_skill(staging_root / "SKILL.md")
    copy_processed_artifacts(context.repo_root / "data" / "processed", staged_data_root)
    data_version = build_data_version(
        context.repo_root,
        context.version,
        staged_data_root,
        package_data_root=BUNDLED_DATA_DIR,
        generated_at=context.generated_at,
        source=context.source,
    )
    write_json(staging_root / "assets" / DATA_VERSION_NAME, data_version)

    artifact = zip_directory(
        staging_root,
        context.dist_dir / f"{SKILL_ARCHIVE_NAME}-{context.version}.zip",
        include_root=False,
    )
    return Artifact("skill", artifact.path, artifact.sha256, artifact.size_bytes)


def write_manifest(
    context: BuildContext,
    targets: list[str],
    artifacts: list[Artifact],
) -> Path:
    manifest_path = context.dist_dir / f"manifest-{context.version}.json"
    payload = {
        "version": context.version,
        "generated_at": context.generated_at,
        "targets": targets,
        "source": context.source,
        "artifacts": [
            {
                "target": artifact.target,
                "path": artifact.path.name,
                "size_bytes": artifact.size_bytes,
                "sha256": artifact.sha256,
            }
            for artifact in artifacts
        ],
    }
    write_json(manifest_path, payload)
    return manifest_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        choices=("all", *DEFAULT_TARGETS),
        default="all",
        help="Artifact target to build.",
    )
    parser.add_argument("--version", help="Override the pyproject version.")
    parser.add_argument(
        "--dist-dir",
        default="dist",
        help="Output directory, relative to the repo root unless absolute.",
    )
    parser.add_argument(
        "--build-dir",
        default="build",
        help="Staging directory, relative to the repo root unless absolute.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = repo_root_from_script()
    version = args.version or read_project_version(repo_root)
    dist_dir = Path(args.dist_dir)
    if not dist_dir.is_absolute():
        dist_dir = repo_root / dist_dir
    build_dir = Path(args.build_dir)
    if not build_dir.is_absolute():
        build_dir = repo_root / build_dir

    context = build_context(repo_root, build_dir, dist_dir, version)
    requested_targets = DEFAULT_TARGETS if args.target == "all" else [args.target]

    builders = {
        "data": build_data_archive,
        "skill": build_skill,
    }
    artifacts = [builders[target](context) for target in requested_targets]
    manifest_path = write_manifest(context, requested_targets, artifacts)

    print(f"Wrote {display_path(manifest_path, repo_root)}")
    for artifact in artifacts:
        print(
            f"Wrote {display_path(artifact.path, repo_root)} "
            f"({artifact.size_bytes} bytes, sha256:{artifact.sha256})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
