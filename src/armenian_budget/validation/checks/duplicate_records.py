"""Duplicate records check.

Flattened CSVs repeat parent keys (state body, program) on every child row, so a
key repeated on consecutive rows is expected. A key is duplicated when it
reappears in a separate, non-contiguous block of rows, or, for the full
subprogram key, on more than one row. Rows are read in source file order.

Location info uses CSV line numbers (the header is line 1).
"""

from __future__ import annotations

import pandas as pd

from armenian_budget.core.enums import SourceType

from ..config import get_severity
from ..models import CheckResult

CHECK_ID = "duplicate_records"
_CSV_LINE_OFFSET = 2  # header line + 1-based numbering


def _normalize_whitespace(values: pd.Series) -> pd.Series:
    return (
        values.fillna("").astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
    )


def _code_text(value: object) -> str:
    """Render a code as text, dropping a float-induced '.0'."""
    if pd.isna(value):
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _code_str(values: pd.Series) -> pd.Series:
    return values.map(_code_text)


def _line_range(start: int, end: int) -> str:
    start, end = start + _CSV_LINE_OFFSET, end + _CSV_LINE_OFFSET
    return str(start) if start == end else f"{start}-{end}"


def _repeated_blocks(keys: pd.Series) -> dict[str, list[str]]:
    """Map each key that occurs in more than one contiguous block to its line ranges."""
    keys = keys.reset_index(drop=True)
    block_id = keys.ne(keys.shift()).cumsum()
    positions = pd.Series(range(len(keys)))
    blocks = positions.groupby(block_id).agg(["first", "last"])
    blocks["key"] = keys.groupby(block_id).first()
    repeated = blocks[blocks["key"].duplicated(keep=False)]
    return {
        key: [_line_range(r["first"], r["last"]) for _, r in group.iterrows()]
        for key, group in repeated.groupby("key", sort=False)
    }


def _result(level: str, messages: list[str]) -> CheckResult:
    return CheckResult(
        check_id=CHECK_ID,
        severity=get_severity(CHECK_ID, level),
        passed=not messages,
        fail_count=len(messages),
        messages=messages,
    )


class DuplicateRecordsCheck:
    """Detect state bodies, programs and subprograms that appear more than once."""

    def validate(
        self, df: pd.DataFrame, overall: dict, source_type: SourceType
    ) -> list[CheckResult]:
        """Check for duplicated records.

        Args:
            df: DataFrame containing CSV data in source file order.
            overall: Overall totals (unused).
            source_type: Source type (unused; subprogram rule runs when the
                `subprogram_code` column exists).

        Returns:
            One CheckResult per rule: state body blocks, program blocks,
            subprogram rows and state body whitespace variants. A rule whose
            columns are missing is skipped (`required_fields` reports them).
        """
        del overall, source_type
        if "state_body" not in df.columns:
            return []
        df = df.reset_index(drop=True)
        state_body = _normalize_whitespace(df["state_body"])
        results = []

        messages = [
            f"State body '{sb}' appears in {len(lines)} separate blocks "
            f"(CSV lines {', '.join(lines)})"
            for sb, lines in _repeated_blocks(state_body).items()
        ]
        results.append(_result("state_body", messages))

        if "program_code" in df.columns:
            results.extend(self._program_results(df, state_body))

        messages = []
        raw = df["state_body"].fillna("").astype(str)
        for norm, group in raw.groupby(state_body, sort=False):
            variants = group.drop_duplicates()
            if len(variants) > 1:
                described = ", ".join(
                    f"'{v}' (first CSV line {i + _CSV_LINE_OFFSET})"
                    for i, v in variants.items()
                )
                messages.append(
                    f"State body '{norm}' has {len(variants)} whitespace variants: "
                    f"{described}"
                )
        results.append(_result("state_body", messages))

        return results

    @staticmethod
    def _program_results(df: pd.DataFrame, state_body: pd.Series) -> list[CheckResult]:
        """Program block rule, plus the subprogram row rule when that level exists."""
        program = _code_str(df["program_code"])
        sep = "\x1f"
        messages = []
        for key, lines in _repeated_blocks(state_body + sep + program).items():
            sb, code = key.split(sep)
            messages.append(
                f"State body '{sb}' program {code} appears in {len(lines)} separate "
                f"blocks (CSV lines {', '.join(lines)})"
            )
        results = [_result("program", messages)]

        if "subprogram_code" in df.columns:
            full = pd.DataFrame(
                {"sb": state_body, "p": program, "s": _code_str(df["subprogram_code"])}
            )
            messages = []
            dup = full[full.duplicated(keep=False)]
            for (sb, code, sub), group in dup.groupby(["sb", "p", "s"], sort=False):
                lines = ", ".join(str(i + _CSV_LINE_OFFSET) for i in group.index)
                messages.append(
                    f"State body '{sb}' program {code} subprogram {sub} appears on "
                    f"{len(group)} rows (CSV lines {lines})"
                )
            results.append(_result("subprogram", messages))
        return results

    def applies_to_source_type(self, source_type: SourceType) -> bool:
        """Check applies to all source types."""
        del source_type
        return True
