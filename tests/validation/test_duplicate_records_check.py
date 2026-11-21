"""Tests for the DuplicateRecordsCheck validation.

Flattened CSVs repeat parent keys on every child row, so contiguous repeats are
expected; only keys that reappear in a separate block (or exact leaf-key
repeats) are duplicates.
"""

import pandas as pd

from armenian_budget.core.enums import SourceType
from armenian_budget.validation.checks.duplicate_records import DuplicateRecordsCheck


def _results_by_rule(df, source_type=SourceType.BUDGET_LAW):
    results = DuplicateRecordsCheck().validate(df, {}, source_type)
    assert all(r.check_id == "duplicate_records" for r in results)
    assert all(r.severity == "error" for r in results)
    return results


def _failed(results):
    return [r for r in results if not r.passed]


def test_contiguous_repeats_pass():
    """Parent keys repeated on consecutive child rows are not duplicates."""
    df = pd.DataFrame(
        {
            "state_body": ["A", "A", "A", "B", "B"],
            "program_code": [1, 1, 2, 3, 3],
            "subprogram_code": [11, 12, 21, 31, 32],
        }
    )
    results = _results_by_rule(df)
    assert len(results) == 4
    assert _failed(results) == []


def test_state_body_in_two_blocks_fails():
    df = pd.DataFrame(
        {
            "state_body": ["A", "A", "B", "A"],
            "program_code": [1, 1, 2, 3],
            "subprogram_code": [11, 12, 21, 31],
        }
    )
    failed = _failed(_results_by_rule(df))
    assert len(failed) == 1
    assert failed[0].fail_count == 1
    msg = failed[0].messages[0]
    assert "'A'" in msg
    assert "2 separate blocks" in msg
    # CSV line numbers: header is line 1, so df rows 0-1 are lines 2-3, row 3 is line 5
    assert "2-3" in msg and "5" in msg


def test_program_in_two_blocks_fails():
    df = pd.DataFrame(
        {
            "state_body": ["A", "A", "A"],
            "program_code": [1, 2, 1],
            "subprogram_code": [11, 21, 12],
        }
    )
    failed = _failed(_results_by_rule(df))
    assert len(failed) == 1
    msg = failed[0].messages[0]
    assert "'A'" in msg and "program 1" in msg
    assert "2 separate blocks" in msg


def test_full_key_repeat_fails_even_when_contiguous():
    df = pd.DataFrame(
        {
            "state_body": ["A", "A", "A"],
            "program_code": [1, 1, 1],
            "subprogram_code": [11, 11, 12],
        }
    )
    failed = _failed(_results_by_rule(df))
    assert len(failed) == 1
    msg = failed[0].messages[0]
    assert "subprogram 11" in msg
    assert "2 rows" in msg
    assert "2, 3" in msg


def test_whitespace_variants_fail_and_normalize_blocks():
    """Whitespace variants are flagged and treated as one state body for blocks."""
    df = pd.DataFrame(
        {
            "state_body": ["A  B", "C", "A B"],
            "program_code": [1, 2, 3],
            "subprogram_code": [11, 21, 31],
        }
    )
    failed = _failed(_results_by_rule(df))
    messages = [m for r in failed for m in r.messages]
    assert len(failed) == 2
    assert any("whitespace" in m and "'A  B'" in m and "'A B'" in m for m in messages)
    assert any("'A B'" in m and "2 separate blocks" in m for m in messages)


def test_contiguous_whitespace_variants_only_flag_spacing():
    df = pd.DataFrame(
        {
            "state_body": [" A", "A ", "B"],
            "program_code": [1, 1, 2],
            "subprogram_code": [11, 12, 21],
        }
    )
    failed = _failed(_results_by_rule(df))
    assert len(failed) == 1
    assert "whitespace" in failed[0].messages[0]


def test_mtep_without_subprogram_columns():
    df = pd.DataFrame(
        {
            "state_body": ["A", "A", "B", "A"],
            "program_code": [1, 2, 3, 4],
        }
    )
    results = _results_by_rule(df, SourceType.MTEP)
    assert len(results) == 3
    failed = _failed(results)
    assert len(failed) == 1
    assert "'A'" in failed[0].messages[0]


def test_mtep_contiguous_pass():
    df = pd.DataFrame({"state_body": ["A", "A", "B"], "program_code": [1, 2, 3]})
    assert _failed(_results_by_rule(df, SourceType.MTEP)) == []


def test_applies_to_all_source_types():
    check = DuplicateRecordsCheck()
    assert all(check.applies_to_source_type(st) for st in SourceType)


def test_missing_key_columns_skip_rules():
    """Missing columns are reported by required_fields; rules needing them skip."""
    assert (
        DuplicateRecordsCheck().validate(
            pd.DataFrame({"col1": ["x"]}), {}, SourceType.SPENDING_Q1
        )
        == []
    )
    results = _results_by_rule(pd.DataFrame({"state_body": ["A", "B", "A"]}))
    assert len(results) == 2
    assert len(_failed(results)) == 1
