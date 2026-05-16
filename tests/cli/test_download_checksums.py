from types import SimpleNamespace

from armenian_budget.interfaces.cli.main import (
    _checksum_record,
    _merge_checksum_item,
    _ordered_checksum_items,
    build_parser,
)


def test_ordered_checksum_items_follows_source_order_and_preserves_unknowns():
    sources = [
        SimpleNamespace(name="first", year=2020, source_type="spending_q1", url="a"),
        SimpleNamespace(name="second", year=2020, source_type="spending_q12", url="b"),
    ]
    unknown_key = (2019, "spending_q1", "z")
    second_key = (2020, "spending_q12", "b")
    first_key = (2020, "spending_q1", "a")
    checksums_by_key = {
        unknown_key: {"name": "legacy"},
        second_key: {"name": "second"},
        first_key: {"name": "first"},
    }

    ordered = _ordered_checksum_items(checksums_by_key, sources)

    assert [item["name"] for item in ordered] == ["first", "second", "legacy"]


def test_checksum_record_preserves_timestamp_when_only_name_changes():
    source = SimpleNamespace(
        name="2024_budget_law_attachments",
        year=2024,
        source_type="budget_law",
        url="https://example.test/attachments.rar",
    )
    previous = {
        "name": "2024_budget_law",
        "year": 2024,
        "source_type": "budget_law",
        "url": "https://example.test/attachments.rar",
        "checksum": "abc",
        "checksum_updated_at": "2025-09-15T02:20:44+00:00",
    }

    record = _checksum_record(source, "abc", previous, "2026-05-10T18:32:11+00:00")

    assert record["name"] == "2024_budget_law_attachments"
    assert record["checksum_updated_at"] == "2025-09-15T02:20:44+00:00"


def test_checksum_record_uses_new_timestamp_when_checksum_changes():
    source = SimpleNamespace(
        name="2024_budget_law_attachments",
        year=2024,
        source_type="budget_law",
        url="https://example.test/attachments.rar",
    )
    previous = {
        "checksum": "abc",
        "checksum_updated_at": "2025-09-15T02:20:44+00:00",
    }

    record = _checksum_record(source, "def", previous, "2026-05-10T18:32:11+00:00")

    assert record["checksum_updated_at"] == "2026-05-10T18:32:11+00:00"


def test_merge_checksum_item_preserves_first_unknown_duplicate():
    index = {}
    key = (2024, "mtep", "https://example.test/mtep.rar")

    _merge_checksum_item(
        index,
        {"name": "2024_mtep", "year": 2024, "source_type": "mtep", "url": key[2]},
        source_names_by_key={},
    )
    _merge_checksum_item(
        index,
        {"name": "legacy_mtep", "year": 2024, "source_type": "mtep", "url": key[2]},
        source_names_by_key={},
    )

    assert index[key]["name"] == "2024_mtep"


def test_merge_checksum_item_allows_source_duplicate_to_refresh_metadata():
    index = {}
    key = (2024, "budget_law", "https://example.test/attachments.rar")

    _merge_checksum_item(
        index,
        {
            "name": "2024_budget_law",
            "year": 2024,
            "source_type": "budget_law",
            "url": key[2],
        },
        source_names_by_key={key: {"2024_budget_law_attachments"}},
    )
    _merge_checksum_item(
        index,
        {
            "name": "2024_budget_law_attachments",
            "year": 2024,
            "source_type": "budget_law",
            "url": key[2],
        },
        source_names_by_key={key: {"2024_budget_law_attachments"}},
    )

    assert index[key]["name"] == "2024_budget_law_attachments"


def test_merge_checksum_item_keeps_active_record_over_legacy_duplicate():
    index = {}
    key = (2024, "mtep", "https://example.test/mtep.rar")

    _merge_checksum_item(
        index,
        {"name": "2024_mtep", "year": 2024, "source_type": "mtep", "url": key[2]},
        source_names_by_key={key: {"2024_mtep"}},
    )
    _merge_checksum_item(
        index,
        {"name": "2025_mtep", "year": 2024, "source_type": "mtep", "url": key[2]},
        source_names_by_key={key: {"2024_mtep"}},
    )

    assert index[key]["name"] == "2024_mtep"


def test_download_cli_exposes_force_without_overwrite():
    parser = build_parser()
    subparsers = next(
        action for action in parser._actions if getattr(action, "choices", None)
    )
    help_text = subparsers.choices["download"].format_help()

    assert "--force" in help_text
    assert "--overwrite" not in help_text
