"""Guard against two source entries pointing at the same upstream file.

A copy-pasted URL makes one year's pipeline silently process another year's
archive, so every URL and checksum must belong to a single source entry.
Entries sharing a name are the same source (checksums.yaml keeps superseded
URLs of a source), so only different names count as a conflict.

One exception: versions of the same year and source type with different labels
may share a checksum, because a draft is often republished unchanged on another
site. URLs stay unique for every entry.
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
    """File entries of sources.yaml, each with its entry's year, type and label."""
    with (CONFIG_DIR / "sources.yaml").open(encoding="utf-8") as f:
        sources = yaml.safe_load(f)["sources"]
    return [
        {
            **file,
            "year": source["year"],
            "source_type": source["source_type"],
            "label": source.get("label"),
        }
        for source in sources
        for file in source.get("files") or [source]
    ]


def _checksum_entries() -> list[dict]:
    """Entries of checksums.yaml, labelled like the source file of the same name."""
    labels = {file["name"]: file["label"] for file in _source_files()}
    with (CONFIG_DIR / "checksums.yaml").open(encoding="utf-8") as f:
        entries = yaml.safe_load(f)["checksums"]
    return [{**entry, "label": labels.get(entry["name"])} for entry in entries]


def _are_versions_of_one_document(entries: list[dict]) -> bool:
    """Same year and source type, and every name carries a different label."""
    labels_by_name = {entry["name"]: entry.get("label") for entry in entries}
    labels = list(labels_by_name.values())
    return len(
        {(entry["year"], entry["source_type"]) for entry in entries}
    ) == 1 and len(set(labels)) == len(labels)


def _shared_values(entries: list[dict], field: str) -> dict[str, list[str]]:
    entries_by_value: dict[str, list[dict]] = defaultdict(list)
    for entry in entries:
        entries_by_value[entry[field]].append(entry)
    conflicts = {}
    for value, sharing in entries_by_value.items():
        names = {entry["name"] for entry in sharing}
        if len(names) < 2 or frozenset(names) in ALLOWED_SHARED:
            continue
        if field == "checksum" and _are_versions_of_one_document(sharing):
            continue
        conflicts[value] = sorted(names)
    return conflicts


def test_source_urls_are_unique():
    assert _shared_values(_source_files(), "url") == {}


@pytest.mark.parametrize("field", ["url", "checksum"])
def test_checksum_entries_do_not_share_files(field):
    assert _shared_values(_checksum_entries(), field) == {}


def _version(name, label, year=2026, source_type="budget_law", **fields):
    return {
        "name": name,
        "year": year,
        "source_type": source_type,
        "label": label,
        "url": f"https://example.test/{name}",
        "checksum": "abc",
        **fields,
    }


def test_same_year_versions_may_share_checksum():
    entries = [
        _version("edraft", "EDRAFT"),
        _version("parliament", "PARLIAMENT"),
        _version("law", None),
    ]

    assert _shared_values(entries, "checksum") == {}


@pytest.mark.parametrize(
    "other",
    [
        _version("other", "PARLIAMENT", year=2025),
        _version("other", "PARLIAMENT", source_type="mtep"),
        _version("other", "EDRAFT"),
    ],
    ids=["two years", "two source types", "same label"],
)
def test_other_shared_checksums_still_conflict(other):
    entries = [_version("edraft", "EDRAFT"), other]

    assert _shared_values(entries, "checksum") == {"abc": ["edraft", "other"]}


def test_two_unlabelled_entries_sharing_a_checksum_conflict():
    entries = [_version("law", None), _version("copy", None)]

    assert _shared_values(entries, "checksum") == {"abc": ["copy", "law"]}


def test_shared_url_always_conflicts():
    url = "https://example.test/same.rar"
    entries = [
        _version("edraft", "EDRAFT", url=url),
        _version("parliament", "PARLIAMENT", url=url),
    ]

    assert _shared_values(entries, "url") == {url: ["edraft", "parliament"]}
