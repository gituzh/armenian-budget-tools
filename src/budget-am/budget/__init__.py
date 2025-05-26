"""This module provides functions to flatten and process Armenian state budget Excel files."""

import re
import sys
import logging
import os
from enum import Enum, auto
from typing import Union, Optional, Dict, Any, List
import pandas as pd
from tqdm import tqdm
import colorlog

# Configure logger with detailed format
logger = logging.getLogger(__name__)


class ProcessingState(Enum):
    """
    State machine states for parsing the budget Excel:
    - INIT: Searching for the grand total row
    - READY: Ready to process entities after grand total
    - STATE_BODY: Processing a state body header row
    - PROGRAM: Processing a program header row
    - SUBPROGRAM: Processing a subprogram header row
    """

    INIT = auto()
    READY = auto()
    STATE_BODY = auto()
    PROGRAM = auto()
    SUBPROGRAM = auto()


class RowType(Enum):
    """
    Row types for parsing the budget Excel:
    - GRAND_TOTAL: Grand total row
    - STATE_BODY_HEADER: State body header row
    - PROGRAM_HEADER: Program header row
    - SUBPROGRAM_MARKER: Subprogram marker row
    - SUBPROGRAM_HEADER: Subprogram header row
    - DETAIL_LINE: Detail line row
    - EMPTY: All columns empty or whitespace
    - UNKNOWN: Doesn't match any pattern
    """

    GRAND_TOTAL = auto()
    STATE_BODY_HEADER = auto()
    PROGRAM_HEADER = auto()
    SUBPROGRAM_MARKER = auto()
    SUBPROGRAM_HEADER = auto()
    DETAIL_LINE = auto()
    EMPTY = auto()
    UNKNOWN = auto()


class SourceType(Enum):
    BUDGET_LAW = auto()
    SPENDING_Q1 = auto()
    SPENDING_Q12 = auto()
    SPENDING_Q123 = auto()
    SPENDING_Q1234 = auto()


def _is_numeric(val) -> bool:
    """Returns True if val can be converted to float."""
    try:
        float(val)
        return True
    except ValueError:
        return False


def _normalize_str(s: str) -> str:
    """Trim, lowercase, and remove spaces from a string."""
    return str(s).strip().lower().replace(" ", "")


def _detect_row_type_2019_2024(row_data: list[str]) -> RowType:
    """
    Detects the row type for 2019-2024 format based on the following criteria:
      - GRAND_TOTAL: col2 == 'ԸՆԴԱՄԵՆԸ'
      - STATE_BODY_HEADER: col0=='' and col1=='' and col2!='' and col3 is numeric
      - PROGRAM_HEADER: col0 is numeric, col1=='' and col2!='' and col3 is numeric
      - SUBPROGRAM_MARKER: 'ծրագրիմիջոցառումներ' in any column
      - SUBPROGRAM_HEADER: col0=='' and col1 is numeric and col2!='' and col3 is numeric
      - DETAIL_LINE: col0=='' and col1=='' and col2!='' and col3==''
      - EMPTY: all columns empty or whitespace
      - UNKNOWN: doesn't match any pattern
    """
    col0, col1, col2, col3 = row_data[0], row_data[1], row_data[2], row_data[3]
    if all(not col.strip() for col in row_data[:4]):
        return RowType.EMPTY
    if _normalize_str(col2) == "ընդամենը":
        return RowType.GRAND_TOTAL
    subprogram_marker = "ծրագրիմիջոցառումներ"
    for col in [col0, col1, col2]:
        if _normalize_str(col) == subprogram_marker:
            return RowType.SUBPROGRAM_MARKER
    if (
        not col0.strip()
        and not col1.strip()
        and col2.strip()
        and _is_numeric(col3)
    ):
        return RowType.STATE_BODY_HEADER
    if (
        col0.strip()
        and _is_numeric(col0)
        and not col1.strip()
        and col2.strip()
        and _is_numeric(col3)
    ):
        return RowType.PROGRAM_HEADER
    if (
        not col0.strip()
        and col1.strip()
        and _is_numeric(col1)
        and col2.strip()
        and _is_numeric(col3)
    ):
        return RowType.SUBPROGRAM_HEADER
    if (
        not col0.strip()
        and not col1.strip()
        and col2.strip()
        and not col3.strip()
    ):
        return RowType.DETAIL_LINE
    return RowType.UNKNOWN


def _detect_row_type_2025(row_data: list[str]) -> RowType:
    """
    Detects the row type for 2025 format based on the following criteria:
      - GRAND_TOTAL: col0 == 'ԸՆԴԱՄԵՆԸ'
      - STATE_BODY_HEADER: col0 has text and col6 is numeric
      - PROGRAM_HEADER: col1 is numeric and col3-6 are non-empty
      - SUBPROGRAM_HEADER: col2 contains dash and col3-6 are non-empty
      - EMPTY: all columns empty or whitespace
      - UNKNOWN: doesn't match any pattern
    """
    col0, col1, col2, col3, col4, col5, col6 = row_data[:7]
    if all(not col.strip() for col in row_data[:7]):
        return RowType.EMPTY
    if _normalize_str(col0) == "ընդամենը":
        return RowType.GRAND_TOTAL
    if col0.strip() and _is_numeric(col6):
        return RowType.STATE_BODY_HEADER
    if (
        not col0.strip()
        and col1.strip()
        and _is_numeric(col1)
        and all([col3.strip(), col4.strip(), col6.strip()])
    ):
        return RowType.PROGRAM_HEADER
    if (
        not col0.strip()
        and not col1.strip()
        and col2.strip()
        and "-" in col2
        and all([col3.strip(), col4.strip(), col5.strip(), col6.strip()])
    ):
        return RowType.SUBPROGRAM_HEADER
    return RowType.UNKNOWN


def _collect_details_2019_2024(
    df: pd.DataFrame, start_idx: int
) -> tuple[list[str], int]:
    """
    Collects up to 5 detail lines after a header row for 2019-2024 format.
    Returns a list of 5 values (col2 of each detail line) and the next row
    index after the details block.
    """
    details = []
    for offset in range(5):
        i = start_idx + offset
        if i >= len(df):
            row_data = ["", "", "", ""]
        else:
            row_data = [str(df.loc[i, col]).strip() for col in range(4)]
        details.append(row_data[2])
        row_type = _detect_row_type_2019_2024(row_data)
        # For value lines (offset 0,2,4): must be DETAIL_LINE or EMPTY
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
        # For label lines (offset 1,3): must be DETAIL_LINE and not empty
        else:
            if row_type != RowType.DETAIL_LINE or not row_data[2]:
                logger.error(
                    "Required label line %d (row %d) is not DETAIL_LINE or "
                    "is empty: %s",
                    offset + 1,
                    start_idx + offset,
                    row_data,
                )
                sys.exit(1)
    return details, start_idx + 5


def flatten_budget_excel_2019_2024(
    excel_path: str,
) -> tuple[pd.DataFrame, float, dict, dict]:
    """
    Flattens the 2024 Armenian budget Excel file using a state machine approach.

    This function separates state transitions from data extraction for clarity
    and maintainability. It also performs strict label checks for program and
    subprogram detail rows.

    Args:
        excel_path: Path to the Excel file to process.

    Returns:
        result_df: Flattened DataFrame.
        grand_total: The grand total value from the Excel.
        rowtype_stats: Dictionary of row type counts.
        statetrans_stats: Dictionary of state transition counts.
    """
    # ===================== MARK: Read and Prepare Data ========================
    # Read the Excel file and fill NaNs with empty strings for easier processing.
    df = pd.read_excel(excel_path, sheet_name=0, header=None)
    df = df.fillna("")

    # ===================== MARK: State Machine Initialization =================
    # Initialize state, context, and statistics.
    state = ProcessingState.INIT
    grand_total = None
    results = []
    current_context = {
        "state_body": "",
        "state_body_total": 0.0,
        "program_code": 0,
        "program_name": "",
        "program_goal": "",
        "program_result_desc": "",
        "program_total": 0.0,
    }
    i = 0
    pbar = tqdm(total=len(df), desc="Processing with state machine")
    log_rows = []
    rowtype_stats = {k: 0 for k in RowType}
    statetrans_stats = {k: 0 for k in ProcessingState}

    # ===================== MARK: Main Loop =====================
    while i < len(df):
        prev_i = i
        row_data = [str(df.loc[i, col]).strip() for col in range(4)]
        row_type = _detect_row_type_2019_2024(row_data)
        log_rows.append((i, state.name, row_type.name))
        rowtype_stats[row_type] += 1
        statetrans_stats[state] += 1
        logger.debug(
            "Row %d: State=%s, Type=%s, Data=%s",
            i,
            state.name,
            row_type.name,
            row_data[:4],
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
        # Extract grand total when in READY state and on GRAND_TOTAL row
        if state == ProcessingState.READY and row_type == RowType.GRAND_TOTAL:
            if not _is_numeric(row_data[3]):
                logger.error("Grand total at row %d is not numeric", i)
                sys.exit(1)
            grand_total = float(row_data[3])
            logger.info("Found grand total: %s", grand_total)
        # Extract state body info
        elif (
            state == ProcessingState.STATE_BODY
            and row_type == RowType.STATE_BODY_HEADER
        ):
            current_context["state_body"] = row_data[2]
            current_context["state_body_total"] = float(row_data[3])
            logger.debug("New state body: %s", current_context["state_body"])
        # Extract program info and check labels
        elif (
            state == ProcessingState.PROGRAM
            and row_type == RowType.PROGRAM_HEADER
        ):
            current_context["program_code"] = int(float(row_data[0]))
            current_context["program_total"] = float(row_data[3])
            details, next_i = _collect_details_2019_2024(df, i + 1)
            # Label checks for program details
            expected_labels = [
                "ծրագրինպատակը",  # row 2
                "վերջնականարդյունքինկարագրությունը",  # row 4
            ]
            for idx, expected in zip([1, 3], expected_labels):
                label = _normalize_str(details[idx])
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
            current_context["program_name"] = (
                details[0] if len(details) > 0 else ""
            )
            current_context["program_goal"] = (
                details[2] if len(details) > 2 else ""
            )
            current_context["program_result_desc"] = (
                details[4] if len(details) > 4 else ""
            )
            i = next_i - 1
            logger.debug("New program: %s", current_context["program_code"])
        # Extract subprogram info and check labels
        elif (
            state == ProcessingState.SUBPROGRAM
            and row_type == RowType.SUBPROGRAM_HEADER
        ):
            try:
                subprogram_code = int(float(row_data[1]))
                subprogram_total = float(row_data[3])
                details, next_i = _collect_details_2019_2024(df, i + 1)
                # Label checks for subprogram details
                expected_labels = [
                    "միջոցառմաննկարագրությունը",  # row 2
                    "միջոցառմանտեսակը",  # row 4
                ]
                for idx, expected in zip([1, 3], expected_labels):
                    label = _normalize_str(details[idx])
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
                results.append(
                    {
                        "state_body": current_context["state_body"],
                        "state_body_total": current_context["state_body_total"],
                        "program_code": current_context["program_code"],
                        "program_name": current_context["program_name"],
                        "program_goal": current_context["program_goal"],
                        "program_result_desc": current_context[
                            "program_result_desc"
                        ],
                        "program_total": current_context["program_total"],
                        "subprogram_code": subprogram_code,
                        "subprogram_name": subprogram_name,
                        "subprogram_desc": subprogram_desc,
                        "subprogram_type": subprogram_type,
                        "subprogram_total": subprogram_total,
                    }
                )
                i = next_i - 1
                logger.debug("Added subprogram: %s", subprogram_code)
            except ValueError as e:
                logger.warning(
                    "Skipping invalid subprogram at row %d: %s", i, e
                )
        i += 1
        pbar.update(i - prev_i)

    # ===================== MARK: Stats and Return =============================
    pbar.close()
    if grand_total is None:
        logger.error("Could not find grand total row with 'ԸՆԴԱՄԵՆԸ'")
        sys.exit(1)
    col_order = [
        "state_body",
        "state_body_total",
        "program_code",
        "program_name",
        "program_goal",
        "program_result_desc",
        "program_total",
        "subprogram_code",
        "subprogram_name",
        "subprogram_desc",
        "subprogram_type",
        "subprogram_total",
    ]
    result_df = pd.DataFrame(results, columns=col_order)
    logger.info(
        "Processed %d subprograms with grand total: %s",
        len(results),
        grand_total,
    )
    return result_df, grand_total, rowtype_stats, statetrans_stats


def flatten_budget_excel_2025(
    excel_path: str,
) -> tuple[pd.DataFrame, float, dict, dict]:
    """
    Flattens the 2025 Armenian budget Excel file using a state machine approach.

    This function handles the 2025 format which differs from 2019-2024:
    - Grand total is in column 0 ('ԸՆԴԱՄԵՆԸ') with value in column 6
    - State bodies: col0 has text and col6 is numeric
    - Programs: col1 is numeric and col3-6 are non-empty
    - Subprograms: col2 contains dash and col3-6 are non-empty
    - Includes program_code_ext field extracted from dash-separated codes

    Args:
        excel_path: Path to the Excel file to process.

    Returns:
        result_df: Flattened DataFrame.
        grand_total: The grand total value from the Excel.
        rowtype_stats: Dictionary of row type counts.
        statetrans_stats: Dictionary of state transition counts.
    """
    # ===================== MARK: Read and Prepare Data ========================
    df = pd.read_excel(excel_path, sheet_name=0, header=None)
    df = df.fillna("")

    # ===================== MARK: State Machine Initialization =================
    state = ProcessingState.INIT
    grand_total = None
    results = []
    current_context = {
        "state_body": "",
        "state_body_total": 0.0,
        "program_code": 0,
        "program_name": "",
        "program_goal": "",
        "program_result_desc": "",
        "program_total": 0.0,
    }

    rowtype_stats = {k: 0 for k in RowType}
    statetrans_stats = {k: 0 for k in ProcessingState}

    # ===================== MARK: Main Loop ====================================
    pbar = tqdm(total=len(df), desc="Processing 2025 format with state machine")

    for i in range(len(df)):
        # Read up to 7 columns for 2025 format
        row_data = [
            str(df.loc[i, col]).strip() if col < len(df.columns) else ""
            for col in range(7)
        ]
        row_type = _detect_row_type_2025(row_data)
        rowtype_stats[row_type] += 1
        statetrans_stats[state] += 1

        logger.debug(
            "Row %d: State=%s, Type=%s, Data=%s",
            i,
            state.name,
            row_type.name,
            row_data[:7],
        )

        # ===================== MARK: State Transition =========================
        if row_type == RowType.GRAND_TOTAL:
            state = ProcessingState.READY
        elif row_type == RowType.STATE_BODY_HEADER:
            state = ProcessingState.STATE_BODY
        elif row_type == RowType.PROGRAM_HEADER:
            state = ProcessingState.PROGRAM
        # Note: No explicit SUBPROGRAM state transition since we detect
        # subprograms directly

        # ===================== MARK: Data Extraction ==========================
        # Extract grand total when in READY state and on GRAND_TOTAL row
        if state == ProcessingState.READY and row_type == RowType.GRAND_TOTAL:
            if not _is_numeric(row_data[6]):
                logger.error("Grand total at row %d, col 6 is not numeric", i)
                sys.exit(1)
            grand_total = float(row_data[6])
            logger.info("Found grand total: %s", grand_total)

        # Extract state body info
        elif (
            state == ProcessingState.STATE_BODY
            and row_type == RowType.STATE_BODY_HEADER
        ):
            current_context["state_body"] = row_data[0]
            current_context["state_body_total"] = float(row_data[6])
            # Reset program context
            current_context["program_code"] = 0
            current_context["program_name"] = ""
            current_context["program_goal"] = ""
            current_context["program_result_desc"] = ""
            current_context["program_total"] = 0.0
            logger.debug("New state body: %s", current_context["state_body"])

        # Extract program info
        elif (
            state == ProcessingState.PROGRAM
            and row_type == RowType.PROGRAM_HEADER
        ):
            current_context["program_code"] = int(float(row_data[1]))
            current_context["program_name"] = row_data[3]
            current_context["program_goal"] = row_data[4]
            current_context["program_result_desc"] = row_data[5]
            current_context["program_total"] = float(row_data[6])
            logger.debug("New program: %s", current_context["program_code"])

        # Extract subprogram info (can happen in any state after READY)
        elif (
            state != ProcessingState.INIT
            and row_type == RowType.SUBPROGRAM_HEADER
        ):
            try:
                # Parse dash-separated code (e.g., "1154 - 11001")
                parts = row_data[2].split("-")
                if len(parts) != 2:
                    logger.warning(
                        "Invalid subprogram code format at row %d: %s",
                        i,
                        row_data[2],
                    )
                    continue

                program_code_ext = int(parts[0].strip())
                subprogram_code = int(parts[1].strip())
                subprogram_total = float(row_data[6])

                results.append(
                    {
                        "state_body": current_context["state_body"],
                        "state_body_total": current_context["state_body_total"],
                        "program_code": current_context["program_code"],
                        "program_code_ext": program_code_ext,
                        "program_name": current_context["program_name"],
                        "program_goal": current_context["program_goal"],
                        "program_result_desc": current_context[
                            "program_result_desc"
                        ],
                        "program_total": current_context["program_total"],
                        "subprogram_code": subprogram_code,
                        "subprogram_name": row_data[3],
                        "subprogram_desc": row_data[4],
                        "subprogram_type": row_data[5],
                        "subprogram_total": subprogram_total,
                    }
                )
                logger.debug("Added subprogram: %s", subprogram_code)

            except (ValueError, IndexError) as e:
                logger.warning(
                    "Skipping invalid subprogram at row %d: %s", i, e
                )

        pbar.update(1)

    # ===================== MARK: Stats and Return =============================
    pbar.close()

    if grand_total is None:
        logger.error(
            "Could not find grand total row with 'ԸՆԴԱՄԵՆԸ' in column 0"
        )
        sys.exit(1)

    # Column order for 2025 format (includes program_code_ext)
    col_order = [
        "state_body",
        "state_body_total",
        "program_code",
        "program_code_ext",
        "program_name",
        "program_goal",
        "program_result_desc",
        "program_total",
        "subprogram_code",
        "subprogram_name",
        "subprogram_desc",
        "subprogram_type",
        "subprogram_total",
    ]

    result_df = pd.DataFrame(results, columns=col_order)
    logger.info(
        "Processed %d subprograms with grand total: %s",
        len(results),
        grand_total,
    )
    return result_df, grand_total, rowtype_stats, statetrans_stats
