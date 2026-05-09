from types import SimpleNamespace

from armenian_budget.interfaces.cli.main import _ordered_checksum_items, build_parser


def test_ordered_checksum_items_follows_source_order_and_preserves_unknowns():
    sources = [
        SimpleNamespace(name="first", year=2020, source_type="spending_q1", url="a"),
        SimpleNamespace(name="second", year=2020, source_type="spending_q12", url="b"),
    ]
    unknown_key = ("legacy", 2019, "spending_q1", "z")
    second_key = ("second", 2020, "spending_q12", "b")
    first_key = ("first", 2020, "spending_q1", "a")
    checksums_by_key = {
        unknown_key: {"name": "legacy"},
        second_key: {"name": "second"},
        first_key: {"name": "first"},
    }

    ordered = _ordered_checksum_items(checksums_by_key, sources)

    assert [item["name"] for item in ordered] == ["first", "second", "legacy"]


def test_download_cli_exposes_force_without_overwrite():
    parser = build_parser()
    subparsers = next(
        action for action in parser._actions if getattr(action, "choices", None)
    )
    help_text = subparsers.choices["download"].format_help()

    assert "--force" in help_text
    assert "--overwrite" not in help_text
