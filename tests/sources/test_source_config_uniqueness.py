"""Guard against two source entries pointing at the same upstream file.

A copy-pasted URL makes one year's pipeline silently process another year's
archive, so every URL and checksum must belong to a single source entry.
Entries sharing a name are the same source (checksums.yaml keeps superseded
URLs of a source), so only different names count as a conflict.
"""

from collections import defaultdict
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "config"

# Genuine cases of different sources sharing a file: frozenset of names -> reason.
ALLOWED_SHARED: dict[frozenset[str], str] = {}


def _source_files() -> list[dict]:
    with (CONFIG_DIR / "sources.yaml").open(encoding="utf-8") as f:
        sources = yaml.safe_load(f)["sources"]
    return [file for source in sources for file in source.get("files") or [source]]


def _checksum_entries() -> list[dict]:
    with (CONFIG_DIR / "checksums.yaml").open(encoding="utf-8") as f:
        return yaml.safe_load(f)["checksums"]


def _shared_values(entries: list[dict], field: str) -> dict[str, list[str]]:
    names_by_value: dict[str, set[str]] = defaultdict(set)
    for entry in entries:
        names_by_value[entry[field]].add(entry["name"])
    return {
        value: sorted(names)
        for value, names in names_by_value.items()
        if len(names) > 1 and frozenset(names) not in ALLOWED_SHARED
    }


def test_source_urls_are_unique():
    assert _shared_values(_source_files(), "url") == {}


@pytest.mark.parametrize("field", ["url", "checksum"])
def test_checksum_entries_do_not_share_files(field):
    assert _shared_values(_checksum_entries(), field) == {}
