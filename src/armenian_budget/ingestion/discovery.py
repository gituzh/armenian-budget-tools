from __future__ import annotations

import hashlib
import json
import logging
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern, Tuple

import yaml

# Import parser implementations from the new package location
from armenian_budget.ingestion.parsers import (
    flatten_budget_excel_2019_2024,
    flatten_budget_excel_2025,
    SourceType,
)


DISCOVERY_INDEX_FILENAME = "discovery_index.json"


@dataclass
class DiscoveryIndexEntry:
    key: str
    path: str
    matched_by: str
    pattern: str
    mtime: float
    size: int
    checksum: Optional[str]
    discovered_at: str


def _quarter_label_for_source_type(source_type: str) -> Optional[str]:
    st = (source_type or "").lower()
    if st == "spending_q1":
        return "Q1"
    if st == "spending_q12":
        return "Q12"
    if st == "spending_q123":
        return "Q123"
    if st == "spending_q1234":
        return "Q1234"
    return None


def _load_parsers_config(parsers_yaml: Path) -> Dict[str, Any]:
    if not parsers_yaml.exists():
        raise FileNotFoundError(f"Parsers config not found: {parsers_yaml}")
    with parsers_yaml.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data


def _compile_pattern_for(
    *,
    cfg: Dict[str, Any],
    source_type: str,
    year: int,
    quarter: Optional[str],
) -> Tuple[Optional[Pattern[str]], str]:
    # Determine parser group: budget_law vs spending
    st = (source_type or "").lower()
    group = "budget_law" if st == "budget_law" else "spending"
    group_cfg = (cfg.get("parsers", {}).get(group, {}) or {}).get("search", {})
    # Precedence: exact year/quarter > year > global
    matched_by = ""
    regex_str: Optional[str] = None
    if quarter is not None:
        key = f"{year}/{quarter}"
        regex_str = (group_cfg.get("by_year", {}) or {}).get(str(key), {}).get("regex")
        if regex_str:
            matched_by = str(key)
    if not regex_str:
        regex_str = (group_cfg.get("by_year", {}) or {}).get(str(year), {}).get("regex")
        if regex_str:
            matched_by = str(year)
    if not regex_str:
        regex_str = (group_cfg.get("global", {}) or {}).get("regex")
        if regex_str:
            matched_by = "global"
    if not regex_str:
        return None, matched_by
    try:
        return re.compile(regex_str), matched_by
    except re.error as e:  # noqa: BLE001
        logging.error("Invalid regex in parsers.yaml for %s: %s", group, e)
        return None, matched_by


def _iter_search_roots(extracted_root: Path, year: int, source_type: str) -> List[Path]:
    st = (source_type or "").lower()
    if st == "budget_law":
        return [extracted_root / "budget_laws" / str(year)]
    if st.startswith("spending_"):
        base = extracted_root / "spending_reports" / str(year)
        q = _quarter_label_for_source_type(st)
        if q:
            return [base / q]
        return [base]
    # Fallback: search whole extracted
    return [extracted_root]


def _candidate_score(path: Path) -> float:
    try:
        size = path.stat().st_size
    except OSError:
        size = 0
    ext_bonus = 1.0 if path.suffix.lower() == ".xlsx" else 0.8
    size_score = min(size / float(10 * 1024 * 1024), 1.0)  # up to 10MB scaled
    depth = (
        len(path.relative_to(path.anchor).parts)
        if path.is_absolute()
        else len(path.parts)
    )
    depth_penalty = 1.0 - min(max(depth - 1, 0) * 0.02, 0.3)
    return ext_bonus + size_score + depth_penalty


def _list_candidates(roots: List[Path], pattern: Optional[Pattern[str]]) -> List[Path]:
    candidates: List[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*.xls*"):
            if not p.is_file():
                continue
            name = p.name
            if pattern is not None and not pattern.search(name):
                continue
            try:
                if p.stat().st_size < 20_000:  # Ignore tiny files < 20KB
                    continue
            except OSError:
                continue
            candidates.append(p)
    # Rank by heuristic score
    candidates.sort(key=_candidate_score, reverse=True)
    return candidates


def _sha256_of_file(path: Path) -> str:
    sha = hashlib.sha256()
    with open(path, "rb") as rf:
        for block in iter(lambda: rf.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def _ensure_index_path(extracted_root: Path) -> Path:
    index_dir = extracted_root
    index_dir.mkdir(parents=True, exist_ok=True)
    return index_dir / DISCOVERY_INDEX_FILENAME


def _load_index(extracted_root: Path) -> Dict[str, Any]:
    index_path = _ensure_index_path(extracted_root)
    if not index_path.exists():
        return {}
    try:
        with index_path.open("r", encoding="utf-8") as f:
            return json.load(f) or {}
    except (json.JSONDecodeError, OSError):
        logging.warning(
            "Failed to read discovery index; starting fresh: %s", index_path
        )
        return {}


def _save_index(extracted_root: Path, index: Dict[str, Any]) -> None:
    index_path = _ensure_index_path(extracted_root)
    with index_path.open("w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def _to_relative_index_path(file_path: Path, *, extracted_root: Path) -> str:
    """Return a stable path relative to the extracted root for the index.

    Args:
      file_path: Absolute or relative path to a discovered file.
      extracted_root: Extracted data root directory (usually ``./data/extracted``).

    Returns:
      POSIX-style relative path string under ``dest_root``.
    """
    abs_path = file_path.resolve()
    base = extracted_root.resolve()
    try:
        rel = abs_path.relative_to(base)
        return rel.as_posix()
    except ValueError:
        # If the file is outside dest_root, return absolute POSIX path
        return abs_path.as_posix()


def _is_entry_still_valid(entry: Dict[str, Any], *, extracted_root: Path) -> bool:
    """Determine whether a cached discovery entry is still valid.

    The entry is considered valid if it resolves to an existing file and the
    content matches. When a checksum is present, validity is based solely on
    checksum equality. If no checksum is stored (legacy entries), validity
    falls back to size and mtime equality.

    Args:
      entry: A dictionary representing a discovery index entry.
      extracted_root: Extracted data root directory used to resolve
        relative paths stored in the index.

    Returns:
      True if the entry points to a file whose content matches the stored
      checksum (or matches size and mtime for legacy entries); False otherwise.
    """
    try:
        path_str = entry.get("path", "")
        if not path_str:
            return False
        raw = Path(path_str)
        # Resolve only relative to extracted root
        candidates: List[Path]
        if raw.is_absolute():
            candidates = [raw]
        else:
            candidates = [
                (extracted_root / raw).resolve(),
            ]
        path: Optional[Path] = None
        for cand in candidates:
            try:
                if cand.exists():
                    path = cand
                    break
            except OSError:
                continue
        if path is None:
            return False

        stored_checksum = entry.get("checksum")
        if stored_checksum:
            # Normalize possible "sha256:..." prefix
            if isinstance(stored_checksum, str) and stored_checksum.lower().startswith(
                "sha256:"
            ):
                stored_checksum = stored_checksum.split(":", 1)[1]
            current_checksum = _sha256_of_file(path)
            return bool(stored_checksum) and stored_checksum == current_checksum

        # Fallback: size + mtime equality when no checksum was stored
        st = path.stat()
        if int(entry.get("size", -1)) != st.st_size:
            return False
        if float(entry.get("mtime", -1)) != st.st_mtime:
            return False
        return True
    except (OSError, ValueError, TypeError):
        return False


def _validate_with_parser(candidate: Path, year: int, source_type: str) -> bool:
    try:
        if int(year) == 2025:
            df, _overall, _, _ = flatten_budget_excel_2025(str(candidate))
        else:
            df, _overall, _, _ = flatten_budget_excel_2019_2024(
                str(candidate), source_type=SourceType[source_type], year=int(year)
            )
        if df is None:
            return False
        if getattr(df, "empty", False):
            return False
        return True
    except (
        AssertionError,
        ValueError,
        KeyError,
        IndexError,
        OSError,
        RuntimeError,
    ):
        return False


def discover_best_file(
    *,
    extracted_root: Path,
    year: int,
    source_type: str,
    parsers_config_path: Path,
    force_discover: bool = False,
    deep_validate: bool = False,
) -> Path:
    """Discover the best-matching source workbook and cache the result.

    Args:
      extracted_root: Extracted data root directory (usually ``./data/extracted``).
      year: Four-digit year to search under ``extracted``.
      source_type: One of ``BUDGET_LAW``, ``SPENDING_Q1``, ``SPENDING_Q12``,
        ``SPENDING_Q123``, ``SPENDING_Q1234``.
      parsers_config_path: Path to ``parsers.yaml`` that defines discovery
        patterns.
      force_discover: If True, bypass cache validity and re-discover.
      deep_validate: If True, probe-parse candidates to validate content.

    Returns:
      Absolute path to the selected workbook.

    Raises:
      FileNotFoundError: If no candidate workbook is found.
    """
    logger = logging.getLogger(__name__)
    index = _load_index(extracted_root)
    key = f"{year}/{source_type.lower()}"
    existing = index.get(key)
    if (
        existing
        and not force_discover
        and _is_entry_still_valid(existing, extracted_root=extracted_root)
    ):
        return Path(existing["path"]).resolve()

    cfg = _load_parsers_config(parsers_config_path)
    quarter = _quarter_label_for_source_type(source_type)
    pattern, matched_by = _compile_pattern_for(
        cfg=cfg, source_type=source_type, year=int(year), quarter=quarter
    )
    roots = _iter_search_roots(extracted_root, int(year), source_type)
    candidates = _list_candidates(roots, pattern)
    if not candidates:
        # As a fallback, search without the regex but still restrict to .xls*
        candidates = _list_candidates(roots, None)
    if not candidates:
        raise FileNotFoundError(
            f"No .xls/.xlsx candidates found for {year} {source_type} under {roots}"
        )

    selected: Optional[Path] = None
    if deep_validate:
        # Probe up to top-N candidates with the parser
        for candidate in candidates[:8]:
            if _validate_with_parser(candidate, int(year), source_type):
                selected = candidate
                break
        # If none validated, still pick the best scored candidate
        if selected is None:
            selected = candidates[0]
    else:
        # Choose best-scored candidate without parsing
        selected = candidates[0]

    st = selected.stat()
    checksum = _sha256_of_file(selected)
    entry = DiscoveryIndexEntry(
        key=key,
        path=_to_relative_index_path(selected, extracted_root=extracted_root),
        matched_by=matched_by
        or (pattern.pattern if pattern is not None else "fallback"),
        pattern=pattern.pattern if pattern is not None else "",
        mtime=st.st_mtime,
        size=st.st_size,
        checksum=f"sha256:{checksum}",
        discovered_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )
    index[key] = asdict(entry)
    _save_index(extracted_root, index)
    logger.info("Discovered %s → %s", key, selected)
    return selected.resolve()


__all__ = ["discover_best_file"]
