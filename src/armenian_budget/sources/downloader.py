from __future__ import annotations

import hashlib
import logging
import ssl
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

import httpx

from .registry import SourceDefinition
from urllib.parse import unquote


DOWNLOAD_CHUNK_SIZE = 1024 * 256


@dataclass
class DownloadResult:
    name: str
    year: int
    url: str
    output_path: Path
    ok: bool
    reason: Optional[str] = None
    quarter: Optional[str] = None


def _safe_file_name(url: str, default_ext: Optional[str]) -> str:
    # Use last path segment when possible, fallback to hash
    try:
        filename = url.split("?")[0].rstrip("/").split("/")[-1]
        filename = unquote(filename)
        if "." in filename:
            return filename
    except Exception:
        pass
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    # If no default extension, just use .bin
    ext = default_ext or "bin"
    return f"download_{digest}.{ext}"


def _quarter_dir(source_type: str) -> str:
    st = (source_type or "").lower()
    if st == "spending_q1":
        return "Q1"
    if st == "spending_q12":
        return "Q12"
    if st == "spending_q123":
        return "Q123"
    if st == "spending_q1234":
        return "Q1234"
    # Fallback: extract suffix after spending_
    if st.startswith("spending_"):
        return st.split("_", 1)[1].upper()
    return "misc"


def _category_and_subdir(
    dest_root: Path, year: int, source_type: str
) -> tuple[Path, Optional[str]]:
    """Return destination subdir under original/ and the quarter label if applicable.

    Spending sources → original/spending_reports/{year}/Q*
    Budget law → original/budget_laws/{year}
    Others → original/other/{year}
    """
    st = (source_type or "").lower()
    if st.startswith("spending_"):
        q = _quarter_dir(st)
        return dest_root / "original" / "spending_reports" / str(year) / q, q
    if st == "budget_law":
        return dest_root / "original" / "budget_laws" / str(year), None
    return dest_root / "original" / "other" / str(year), None


def download_sources(
    sources: Iterable[SourceDefinition],
    dest_root: Path,
    timeout_sec: float = 60.0,
    skip_existing: bool = True,
    overwrite_existing: bool = False,
) -> List[DownloadResult]:
    """Download source files into data/original structure.

    - Saves to: {dest_root}/original/spending_reports/{year}/<file>
    - Skips when URL is empty.
    - If file already exists, re-download to a temporary file and replace only when size differs.
    """
    logger = logging.getLogger(__name__)
    dest_root.mkdir(parents=True, exist_ok=True)

    results: List[DownloadResult] = []
    # Use browser-like headers to avoid server blocking
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    # Create SSL context that's more permissive for problematic servers
    ssl_context = ssl.create_default_context()
    ssl_context.set_ciphers("DEFAULT@SECLEVEL=1")
    ssl_context.options |= 0x4  # OP_LEGACY_SERVER_CONNECT

    client = httpx.Client(
        timeout=timeout_sec, follow_redirects=True, headers=headers, verify=ssl_context
    )
    try:
        for s in sources:
            if not s.url:
                logger.warning(
                    "Skip (missing URL): %s [%s %s]",
                    s.name,
                    s.year,
                    s.source_type,
                )
                results.append(
                    DownloadResult(
                        name=s.name,
                        year=s.year,
                        url=s.url,
                        output_path=dest_root,
                        ok=False,
                        reason="missing_url",
                    )
                )
                continue

            subdir, quarter = _category_and_subdir(dest_root, s.year, s.source_type)
            subdir.mkdir(parents=True, exist_ok=True)
            # If override format is provided, force the extension; otherwise infer from URL
            file_name = _safe_file_name(s.url, s.file_format)
            if s.file_format:
                # Force extension to provided override
                from pathlib import PurePath

                stem = PurePath(file_name).stem
                file_name = f"{stem}.{s.file_format}"
            output_path = subdir / file_name

            try:
                logger.info(
                    "Downloading %s [%s %s] %s → %s",
                    s.name,
                    s.year,
                    s.source_type,
                    s.url,
                    output_path,
                )
                # Skip network call if file already exists and skipping is enabled
                if (
                    not overwrite_existing
                    and skip_existing
                    and output_path.exists()
                    and output_path.stat().st_size > 0
                ):
                    logger.info(
                        "Skip (exists): %s [%s %s] → %s",
                        s.name,
                        s.year,
                        s.source_type,
                        output_path,
                    )
                    results.append(
                        DownloadResult(
                            name=s.name,
                            year=s.year,
                            url=s.url,
                            output_path=output_path,
                            ok=True,
                            reason="skipped_existing",
                            quarter=quarter,
                        )
                    )
                    continue
                with client.stream("GET", s.url) as r:
                    r.raise_for_status()
                    tmp_path = output_path.with_suffix(output_path.suffix + ".part")
                    with open(tmp_path, "wb") as f:
                        for chunk in r.iter_bytes(chunk_size=DOWNLOAD_CHUNK_SIZE):
                            if chunk:
                                f.write(chunk)

                # Optional checksum verification if provided
                if getattr(s, "checksum", None):
                    sha = hashlib.sha256()
                    with open(tmp_path, "rb") as rf:
                        for block in iter(lambda: rf.read(1024 * 1024), b""):
                            sha.update(block)
                    digest = sha.hexdigest()
                    if digest.lower() != str(s.checksum).lower():
                        logging.error(
                            "Checksum mismatch for %s [%s %s]: expected=%s actual=%s",
                            s.name,
                            s.year,
                            s.source_type,
                            s.checksum,
                            digest,
                        )
                        # Clean up temp file and mark failure
                        tmp_path.unlink(missing_ok=True)
                        results.append(
                            DownloadResult(
                                name=s.name,
                                year=s.year,
                                url=s.url,
                                output_path=output_path,
                                ok=False,
                                reason="checksum_mismatch",
                                quarter=quarter,
                            )
                        )
                        continue

                # Replace if target missing or overwrite is requested or sizes differ
                if output_path.exists():
                    same_size = output_path.stat().st_size == tmp_path.stat().st_size
                    if not same_size or overwrite_existing:
                        tmp_path.replace(output_path)
                    else:
                        tmp_path.unlink(missing_ok=True)
                else:
                    tmp_path.replace(output_path)

                # Checksum persistence is handled by the CLI after successful downloads

                size = output_path.stat().st_size if output_path.exists() else 0
                logger.info(
                    "Saved %s [%s %s] → %s (%d bytes)",
                    s.name,
                    s.year,
                    s.source_type,
                    output_path,
                    size,
                )
                results.append(
                    DownloadResult(
                        name=s.name,
                        year=s.year,
                        url=s.url,
                        output_path=output_path,
                        ok=True,
                        quarter=quarter,
                    )
                )
            except Exception as e:  # noqa: BLE001
                logger.error(
                    "Failed to download %s [%s %s] %s: %s",
                    s.name,
                    s.year,
                    s.source_type,
                    s.url,
                    e,
                )
                results.append(
                    DownloadResult(
                        name=s.name,
                        year=s.year,
                        url=s.url,
                        output_path=output_path,
                        ok=False,
                        reason=str(e),
                        quarter=quarter,
                    )
                )
    finally:
        client.close()

    return results
