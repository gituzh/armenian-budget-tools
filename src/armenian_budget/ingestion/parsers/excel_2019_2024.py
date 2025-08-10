"""2019-2024 Excel parser implementation (migrated from legacy module).

This module contains the original state-machine based parser for historical
budget laws and spending reports, preserved as-is but relocated under the
new package structure.
"""

from __future__ import annotations

import logging
import sys
from decimal import Decimal
from typing import Dict, List, Tuple
import pandas as pd
from tqdm import tqdm
from armenian_budget.core.enums import SourceType
from ._common import (
    ProcessingState,
    RowType,
    get_column_mappings,
    get_expected_columns,
    is_numeric,
    normalize_str,
    sort_columns_by_excel_order,
)


logger = logging.getLogger(__name__)


def _norm_label(text: str) -> str:
    """Normalize labels: lowercase, trim, remove spaces and common punctuation.

    This helps tolerate variants like 'Ընդամենը:', 'Ընդամենը՝', etc.
    """
    s = normalize_str(text)
    # Remove common ASCII and Armenian punctuation that may trail labels
    for ch in (":", ".", "՝", "։", "-", "—", "–", "_"):
        s = s.replace(ch, "")
    return s


def _extract_subprogram_code(raw_code: str) -> int:
    """Extract subprogram code from either numeric or compound format."""
    if "-" in raw_code:
        parts = raw_code.split("-")
        return int(parts[1].strip())
    else:
        return int(float(raw_code.strip()))


def _detect_row_type_2019_2024(row_data: List[str]) -> RowType:
    """
    Detects the row type for 2019-2024 format based on the following criteria:
      - GRAND_TOTAL: col2 == 'ԸՆԴԱՄԵՆԸ'
      - STATE_BODY_HEADER: col0=='' and col1=='' and col2!='' and col3 is numeric
      - PROGRAM_HEADER: col0 is numeric, col1=='' and col2!='' and col3 is numeric
      - SUBPROGRAM_MARKER: 'ծրագրիմիջոցառումներ' in any column
      - SUBPROGRAM_HEADER: col0=='' and col1 is numeric/compound and col2!='' and col3 is numeric
      - DETAIL_LINE: col0=='' and col1=='' and col2!='' and col3==''
      - EMPTY: all columns empty or whitespace
      - UNKNOWN: doesn't match any pattern
    """
    col0, col1, col2, col3 = row_data[0], row_data[1], row_data[2], row_data[3]
    if all(not col.strip() for col in row_data[:4]):
        return RowType.EMPTY
    # Some years may place the label with punctuation or minor spacing; tolerate that
    if any(_norm_label(c) == "ընդամենը" for c in (col0, col1, col2)):
        return RowType.GRAND_TOTAL
    subprogram_marker = "ծրագրիմիջոցառումներ"
    for col in [col0, col1, col2]:
        if normalize_str(col) == subprogram_marker:
            return RowType.SUBPROGRAM_MARKER
    if not col0.strip() and not col1.strip() and col2.strip() and is_numeric(col3):
        return RowType.STATE_BODY_HEADER
    if col0.strip() and is_numeric(col0) and not col1.strip() and col2.strip() and is_numeric(col3):
        return RowType.PROGRAM_HEADER
    if not col0.strip() and col1.strip() and col2.strip() and is_numeric(col3):
        try:
            if "-" in col1:
                parts = col1.split("-")
                if len(parts) == 2 and all(is_numeric(p.strip()) for p in parts):
                    return RowType.SUBPROGRAM_HEADER
            elif is_numeric(col1):
                return RowType.SUBPROGRAM_HEADER
        except ValueError:
            pass
    if not col0.strip() and not col1.strip() and col2.strip() and not col3.strip():
        return RowType.DETAIL_LINE
    return RowType.UNKNOWN


def _collect_details_2019_2024(df: pd.DataFrame, start_idx: int) -> Tuple[List[str], int]:
    """
    Collects up to 5 detail lines after a header row for 2019-2024 format.
    Returns a list of 5 values (col2 of each detail line) and the next row
    index after the details block.
    """
    details: List[str] = []
    for offset in range(5):
        i = start_idx + offset
        if i >= len(df):
            row_data = ["", "", "", ""]
        else:
            row_data = [str(df.loc[i, col]).strip() for col in range(4)]
        details.append(row_data[2])
        row_type = _detect_row_type_2019_2024(row_data)
        if offset in [0, 2, 4]:
            if row_type == RowType.DETAIL_LINE:
                continue
            if row_type == RowType.EMPTY:
                logger.warning(
                    "Optional value line %d (row %d) is empty.",
                    offset + 1,
                    start_idx + offset,
                )
                continue
            logger.error(
                "Value line %d (row %d) is not DETAIL_LINE or empty: %s",
                offset + 1,
                start_idx + offset,
                row_data,
            )
            sys.exit(1)
        else:
            if row_type != RowType.DETAIL_LINE or not row_data[2]:
                logger.error(
                    "Required label line %d (row %d) is not DETAIL_LINE or is empty: %s",
                    offset + 1,
                    start_idx + offset,
                    row_data,
                )
                sys.exit(1)
    return details, start_idx + 5


def _parse_fraction(val):
    """Convert a percentage value (e.g., 71.2 or '71.2%') to a fraction (0.712)."""
    if isinstance(val, str):
        val = val.strip().replace("%", "")

    # Handle non-numeric values (like '-') in percentage columns
    if not is_numeric(val):
        return 0.0

    # Use Decimal for exact decimal arithmetic
    return float(Decimal(val) / Decimal("100"))


def _sort_columns_by_excel_order(mappings: Dict[str, int]) -> List[str]:
    return sort_columns_by_excel_order(mappings)


def _extract_value(val: str, col_idx: int, percent_cols: set[int]) -> float:
    """Extract and convert a value, handling percentages appropriately."""
    if col_idx in percent_cols:
        return _parse_fraction(val)

    return float(val) if is_numeric(val) else 0.0


def flatten_budget_excel_2019_2024(
    excel_file_path: str,
    source_type: SourceType = SourceType.BUDGET_LAW,
    year: int | None = None,
) -> tuple[pd.DataFrame, float, dict, dict]:
    """
    Flattens Armenian budget and spending Excel files (2019-2024 format) using
    a state machine approach.

    This function supports both budget law files and spending reports (Q1, Q12,
    Q123, Q1234). It separates state transitions from data extraction for
    clarity and maintainability, and performs strict label checks for program
    and subprogram detail rows.

    Args:
        excel_file_path: Path to the Excel file to process.
        source_type: Type of source file (BUDGET_LAW, SPENDING_Q1, etc.).

    Returns:
        result_df: Flattened DataFrame with dynamic columns based on source type.
        overall_values: The overall values from the Excel (float for budget,
            dict for spending reports).
        rowtype_stats: Dictionary of row type counts.
        statetrans_stats: Dictionary of state transition counts.
    """
    # ===================== MARK: Read and Prepare Data ========================
    # Read the Excel file and fill NaNs with empty strings for easier processing.
    df = pd.read_excel(excel_file_path, sheet_name=0, header=None)
    df = df.fillna("")

    # Get expected number of columns for this source type
    expected_cols = get_expected_columns(source_type)
    logger.debug("Expected cols: %s", expected_cols)
    logger.debug("DF columns: %s", df.columns)

    # ===================== MARK: State Machine Initialization =================
    # Initialize state, context, and statistics.
    state = ProcessingState.INIT
    overall_values = None
    results = []
    current_context = {
        "state_body": "",
        "program_code": 0,
        "program_name": "",
        "program_goal": "",
        "program_result_desc": "",
    }

    # Add dynamic columns based on source type
    state_body_mappings = get_column_mappings(source_type, "state_body_")
    program_mappings = get_column_mappings(source_type, "program_")

    # Initialize context with zero values for all mappings
    for key in state_body_mappings:
        current_context[key] = 0.0
    for key in program_mappings:
        current_context[key] = 0.0

    i = 0
    desc_label = (
        f"Processing {year} {source_type.name}" if year else f"Processing {source_type.name}"
    )
    # Pad to fixed width so bars align across different labels; set unit to rows
    desc_padded = f"{desc_label:<31}"
    pbar = tqdm(
        total=len(df),
        desc=desc_padded,
        unit="rows",
        bar_format="{desc}{percentage:3.0f}%|{bar}| {n:>5}/{total:>5} [{elapsed}<{remaining}, {rate_fmt}]",
    )
    log_rows = []
    rowtype_stats = {k: 0 for k in RowType}
    statetrans_stats = {k: 0 for k in ProcessingState}

    # ===================== MARK: Main Loop =====================
    percent_cols = set()
    if source_type in [
        SourceType.SPENDING_Q1,
        SourceType.SPENDING_Q12,
        SourceType.SPENDING_Q123,
    ]:
        # actual_vs_rev_annual_plan, actual_vs_rev_period_plan
        percent_cols = {8, 9}
    elif source_type == SourceType.SPENDING_Q1234:
        # actual_vs_rev_annual_plan
        percent_cols = {6}
    while i < len(df):
        prev_i = i
        row_data = [
            str(df.loc[i, col]).strip() if col < len(df.columns) else ""
            for col in range(expected_cols)
        ]
        row_type = _detect_row_type_2019_2024(row_data)
        log_rows.append((i, state.name, row_type.name))
        rowtype_stats[row_type] += 1
        statetrans_stats[state] += 1
        logger.debug(
            "Row %d: State=%s, Type=%s, Data=%s",
            i,
            state.name,
            row_type.name,
            row_data,
        )

        # ===================== MARK: State Transition =========================
        # Only update state here, do not extract data
        if row_type == RowType.GRAND_TOTAL:
            state = ProcessingState.READY
        elif row_type == RowType.STATE_BODY_HEADER:
            state = ProcessingState.STATE_BODY
        elif row_type == RowType.PROGRAM_HEADER:
            state = ProcessingState.PROGRAM
        elif row_type == RowType.SUBPROGRAM_MARKER:
            state = ProcessingState.SUBPROGRAM
        # No state change for DETAIL_LINE, EMPTY, UNKNOWN, SUBPROGRAM_HEADER

        # ===================== MARK: Data Extraction ==========================
        # Extract overall values when in READY state and on GRAND_TOTAL row
        if state == ProcessingState.READY and row_type == RowType.GRAND_TOTAL:
            if source_type == SourceType.BUDGET_LAW:
                if not is_numeric(row_data[3]):
                    logger.error("Grand total at row %d is not numeric", i)
                    sys.exit(1)
                overall_values = {
                    "overall_total": float(row_data[3]),
                }
                logger.info("Found overall row: %s", overall_values)
            else:
                # For spending reports, extract all overall values
                overall_mappings = get_column_mappings(source_type, "overall_")
                overall_values = {}
                logger.debug("Overall mappings: %s", overall_mappings)
                for key, col_idx in overall_mappings.items():
                    overall_values[key] = _extract_value(row_data[col_idx], col_idx, percent_cols)
                logger.info("Found overall row: %s", overall_values)
        # Extract state body info
        elif state == ProcessingState.STATE_BODY and row_type == RowType.STATE_BODY_HEADER:
            current_context["state_body"] = row_data[2]
            # Extract values for all state body columns based on source type
            state_body_mappings = get_column_mappings(source_type, "state_body_")
            for key, col_idx in state_body_mappings.items():
                current_context[key] = _extract_value(row_data[col_idx], col_idx, percent_cols)
            logger.debug("New state body: %s", current_context["state_body"])
        # Extract program info and check labels
        elif state == ProcessingState.PROGRAM and row_type == RowType.PROGRAM_HEADER:
            current_context["program_code"] = int(float(row_data[0]))
            # Extract values for all program columns based on source type
            program_mappings = get_column_mappings(source_type, "program_")
            for key, col_idx in program_mappings.items():
                current_context[key] = _extract_value(row_data[col_idx], col_idx, percent_cols)
            details, next_i = _collect_details_2019_2024(df, i + 1)
            # Label checks for program details
            expected_labels = [
                "ծրագրինպատակը",  # row 2
                "վերջնականարդյունքինկարագրությունը",  # row 4
            ]
            for idx, expected in zip([1, 3], expected_labels):
                label = normalize_str(details[idx])
                if expected not in label:
                    logger.error(
                        "Label check failed for program detail line %d "
                        "(row %d): expected '%s' in '%s'",
                        idx + 1,
                        i + idx,
                        expected,
                        label,
                    )
                    sys.exit(1)
            current_context["program_name"] = details[0] if len(details) > 0 else ""
            current_context["program_goal"] = details[2] if len(details) > 2 else ""
            current_context["program_result_desc"] = details[4] if len(details) > 4 else ""
            i = next_i - 1
            logger.debug(
                "New program - code: %s, name: %s, goal: %s, result_desc: %s",
                current_context["program_code"],
                current_context["program_name"],
                current_context["program_goal"],
                current_context["program_result_desc"],
            )
        # Extract subprogram info and check labels
        elif state == ProcessingState.SUBPROGRAM and row_type == RowType.SUBPROGRAM_HEADER:
            try:
                subprogram_code = _extract_subprogram_code(row_data[1])
                # Extract values for all subprogram columns based on source type
                subprogram_mappings = get_column_mappings(source_type, "subprogram_")
                subprogram_values = {}
                for key, col_idx in subprogram_mappings.items():
                    subprogram_values[key] = _extract_value(
                        row_data[col_idx], col_idx, percent_cols
                    )
                details, next_i = _collect_details_2019_2024(df, i + 1)
                # Label checks for subprogram details
                expected_labels = [
                    "միջոցառմաննկարագրությունը",  # row 2
                    "միջոցառմանտեսակը",  # row 4
                ]
                for idx, expected in zip([1, 3], expected_labels):
                    label = normalize_str(details[idx])
                    if expected not in label:
                        logger.error(
                            "Label check failed for subprogram detail line %d "
                            "(row %d): expected '%s' in '%s'",
                            idx + 1,
                            i + idx,
                            expected,
                            label,
                        )
                        sys.exit(1)
                subprogram_name = details[0] if len(details) > 0 else ""
                subprogram_desc = details[2] if len(details) > 2 else ""
                subprogram_type = details[4] if len(details) > 4 else ""

                # Create result record with dynamic columns
                result_record = {
                    "state_body": current_context["state_body"],
                    "program_code": current_context["program_code"],
                    "program_name": current_context["program_name"],
                    "program_goal": current_context["program_goal"],
                    "program_result_desc": current_context["program_result_desc"],
                    "subprogram_code": subprogram_code,
                    "subprogram_name": subprogram_name,
                    "subprogram_desc": subprogram_desc,
                    "subprogram_type": subprogram_type,
                }

                # Add all state body columns
                for key in state_body_mappings:
                    result_record[key] = current_context[key]

                # Add all program columns
                for key in program_mappings:
                    result_record[key] = current_context[key]

                # Add all subprogram columns
                for key, value in subprogram_values.items():
                    result_record[key] = value

                results.append(result_record)
                i = next_i - 1
                logger.debug(
                    "Added subprogram - code: %s, name: %s, desc: %s, type: %s",
                    subprogram_code,
                    subprogram_name,
                    subprogram_desc,
                    subprogram_type,
                )
            except ValueError as e:
                logger.warning("Skipping invalid subprogram at row %d: %s", i, e)
        i += 1
        pbar.update(i - prev_i)

    # ===================== MARK: Stats and Return =============================
    pbar.close()
    if overall_values is None:
        logger.error("Could not find overall row with 'ԸՆԴԱՄԵՆԸ'")
        sys.exit(1)

    # Create dynamic column order
    col_order = [
        "state_body",
        "program_code",
        "program_name",
        "program_goal",
        "program_result_desc",
        "subprogram_code",
        "subprogram_name",
        "subprogram_desc",
        "subprogram_type",
    ]

    # Add state body columns (in Excel column order)
    col_order.extend(_sort_columns_by_excel_order(state_body_mappings))

    # Add program columns (in Excel column order)
    col_order.extend(_sort_columns_by_excel_order(program_mappings))

    # Add subprogram columns (in Excel column order)
    subprogram_mappings = get_column_mappings(source_type, "subprogram_")
    col_order.extend(_sort_columns_by_excel_order(subprogram_mappings))

    result_df = pd.DataFrame(results, columns=col_order)
    logger.info(
        "Processed %d subprograms with overall values: %s",
        len(results),
        overall_values,
    )
    return result_df, overall_values, rowtype_stats, statetrans_stats
