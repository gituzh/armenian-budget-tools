from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import List
import zipfile


def extract_rar_files(input_dir: Path, output_dir: Path) -> List[Path]:
    """Extract .rar files if `unar` or `unrar` is available without overwriting.

    - Skips extraction if the target directory already exists and is non-empty
      to avoid overwriting previously extracted files.
    - Uses non-overwrite flags for `unrar`.
    - Omits force-overwrite flags for `unar`.
    """
    logger = logging.getLogger(__name__)
    output_dir.mkdir(parents=True, exist_ok=True)

    extracted: List[Path] = []
    unar = shutil.which("unar")
    unrar = shutil.which("unrar")

    if not unar and not unrar:
        logger.warning(
            "No RAR extractor found (install 'unar' or 'unrar'). Skipping extraction."
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
        target_dir.mkdir(parents=True, exist_ok=True)
        if unar:
            # Do not force overwrite; rely on empty target_dir to avoid prompts
            cmd = [unar, "-quiet", str(rar_path), "-o", str(target_dir)]
        else:
            # -o- : do not overwrite existing files
            cmd = [unrar, "x", "-o-", str(rar_path), str(target_dir)]

        try:
            import subprocess

            subprocess.run(
                cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            extracted.append(target_dir)
            logger.info("Extracted %s → %s", rar_path, target_dir)
        except (subprocess.CalledProcessError, OSError) as e:
            logger.error("Failed to extract %s: %s", rar_path, e)

    return extracted


def extract_zip_files(input_dir: Path, output_dir: Path) -> List[Path]:
    """Extract .zip files using the standard library without overwriting.

    - Skips extraction if the target directory already exists and is non-empty.
    - Prevents path traversal (Zip Slip) by validating member paths.
    """
    logger = logging.getLogger(__name__)
    output_dir.mkdir(parents=True, exist_ok=True)

    extracted: List[Path] = []
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
