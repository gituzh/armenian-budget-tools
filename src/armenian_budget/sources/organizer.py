from __future__ import annotations

import logging
import shutil
import subprocess
import zipfile
from pathlib import Path

# Preference order. `unar` is last: it fails on some RAR5 archives that
# 7-Zip and `unrar` extract correctly.
RAR_EXTRACTORS = ("7zz", "7z", "unrar", "unar")


def _rar_command(tool: str, exe: str, rar_path: Path, target_dir: Path) -> list[str]:
    """Build an extraction command that never overwrites existing files."""
    if tool in ("7zz", "7z"):
        # -aos: skip existing files; `--` ends switch parsing
        return [exe, "x", "-aos", f"-o{target_dir}", "--", str(rar_path)]
    if tool == "unrar":
        # -o- : do not overwrite existing files
        return [exe, "x", "-o-", str(rar_path), str(target_dir)]
    # unar: no force-overwrite flag; rely on the empty target_dir
    return [exe, "-quiet", str(rar_path), "-o", str(target_dir)]


def extract_rar_files(input_dir: Path, output_dir: Path) -> list[Path]:
    """Extract .rar files with the first working extractor, without overwriting.

    - Skips extraction if the target directory already exists and is non-empty
      to avoid overwriting previously extracted files.
    - Tries `RAR_EXTRACTORS` in order. When a tool fails, its partial output
      is removed before the next tool runs, and no target directory is left
      behind if every tool fails, so a later run retries the archive.
    - Relies on the extractors' own path sanitisation (no unsafe switches).
    """
    logger = logging.getLogger(__name__)
    output_dir.mkdir(parents=True, exist_ok=True)

    extracted: list[Path] = []
    tools = [(tool, exe) for tool in RAR_EXTRACTORS if (exe := shutil.which(tool))]
    if not tools:
        logger.warning(
            "No RAR extractor found (install 7-Zip with RAR support or 'unrar'). "
            "Skipping extraction."
        )
        return extracted

    for rar_path in sorted(input_dir.rglob("*.rar")):
        # Preserve subdirectory structure (e.g., Q1/Q12/...)
        rel_parent = rar_path.parent.relative_to(input_dir)
        target_dir = output_dir / rel_parent / rar_path.stem
        # Skip if already extracted content exists to avoid overwriting
        if target_dir.exists() and any(target_dir.iterdir()):
            logger.info("Skip extraction (exists): %s", target_dir)
            continue
        for tool, exe in tools:
            target_dir.mkdir(parents=True, exist_ok=True)
            try:
                subprocess.run(
                    _rar_command(tool, exe, rar_path, target_dir),
                    check=True,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
            except (subprocess.CalledProcessError, OSError) as e:
                output = getattr(e, "output", None) or b""
                logger.warning(
                    "%s failed to extract %s: %s\n%s",
                    tool,
                    rar_path,
                    e,
                    output.decode(errors="replace").strip()[-2000:],
                )
                # target_dir was empty before this attempt; drop partial output
                shutil.rmtree(target_dir)
                continue
            extracted.append(target_dir)
            logger.info("Extracted %s → %s with %s", rar_path, target_dir, tool)
            break
        else:
            logger.error(
                "Failed to extract %s with any of: %s",
                rar_path,
                ", ".join(tool for tool, _ in tools),
            )

    return extracted


def extract_zip_files(input_dir: Path, output_dir: Path) -> list[Path]:
    """Extract .zip files using the standard library without overwriting.

    - Skips extraction if the target directory already exists and is non-empty.
    - Prevents path traversal (Zip Slip) by validating member paths.
    """
    logger = logging.getLogger(__name__)
    output_dir.mkdir(parents=True, exist_ok=True)

    extracted: list[Path] = []
    for zip_path in sorted(input_dir.rglob("*.zip")):
        # Preserve subdirectory structure (e.g., Q1/Q12/...)
        rel_parent = zip_path.parent.relative_to(input_dir)
        target_dir = output_dir / rel_parent / zip_path.stem
        if target_dir.exists() and any(target_dir.iterdir()):
            logger.info("Skip extraction (exists): %s", target_dir)
            continue
        target_dir.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(zip_path) as zf:
                root = target_dir.resolve()
                for member in zf.infolist():
                    name = member.filename
                    if not name or name.endswith("/"):
                        continue
                    dest_path = (root / name).resolve()
                    # Path traversal guard
                    if not str(dest_path).startswith(str(root)):
                        logger.warning("Unsafe path in zip member: %s", name)
                        continue
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(member) as src, open(dest_path, "wb") as dst:
                        shutil.copyfileobj(src, dst)
            extracted.append(target_dir)
            logger.info("Extracted %s → %s", zip_path, target_dir)
        except (zipfile.BadZipFile, OSError) as e:
            logger.error("Failed to extract %s: %s", zip_path, e)

    return extracted
