"""2025 Excel parser implementation (migrated from legacy module)."""

from __future__ import annotations

import logging
import sys
from typing import List
import pandas as pd
from tqdm import tqdm
from ._common import ProcessingState, RowType, is_numeric


logger = logging.getLogger(__name__)


def _detect_row_type_2025(row_data: List[str]) -> RowType:
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
    if str(col0).strip().lower().replace(" ", "") == "ընդամենը":
        return RowType.GRAND_TOTAL
    if col0.strip() and is_numeric(col6):
        return RowType.STATE_BODY_HEADER
    if (
        not col0.strip()
        and col1.strip()
        and is_numeric(col1)
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


def flatten_budget_excel_2025(
    excel_file_path: str,
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
        excel_file_path: Path to the Excel file to process.

    Returns:
        result_df: Flattened DataFrame.
        overall_values: The overall values value from the Excel.
        rowtype_stats: Dictionary of row type counts.
        statetrans_stats: Dictionary of state transition counts.
    """
    # ===================== MARK: Read and Prepare Data ========================
    df = pd.read_excel(excel_file_path, sheet_name=0, header=None)
    df = df.fillna("")

    logger.debug("DF columns: %s", df.columns)

    # ===================== MARK: State Machine Initialization =================
    state = ProcessingState.INIT
    overall_values = None
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
    # Pad desc to align with 2019-2024 label width; include unit rows
    pbar = tqdm(
        total=len(df),
        desc=f"{'Processing 2025 BUDGET_LAW':<31}",
        unit="rows",
        bar_format="{desc}{percentage:3.0f}%|{bar}| {n:>5}/{total:>5} [{elapsed}<{remaining}, {rate_fmt}]",
    )

    for i in range(len(df)):
        # Read up to 7 columns for 2025 format
        row_data = [
            str(df.loc[i, col]).strip() if col < len(df.columns) else "" for col in range(7)
        ]
        row_type = _detect_row_type_2025(row_data)
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
        if row_type == RowType.GRAND_TOTAL:
            state = ProcessingState.READY
        elif row_type == RowType.STATE_BODY_HEADER:
            state = ProcessingState.STATE_BODY
        elif row_type == RowType.PROGRAM_HEADER:
            state = ProcessingState.PROGRAM
        # Note: No explicit SUBPROGRAM state transition since we detect
        # subprograms directly

        # ===================== MARK: Data Extraction ==========================
        # Extract overall values when in READY state and on GRAND_TOTAL row
        if state == ProcessingState.READY and row_type == RowType.GRAND_TOTAL:
            if not is_numeric(row_data[6]):
                logger.error("Overall value at row %d, col 6 is not numeric", i)
                sys.exit(1)
            overall_values = {
                "overall_total": float(row_data[6]),
            }
            logger.info("Found overall row: %s", overall_values)

        # Extract state body info
        elif state == ProcessingState.STATE_BODY and row_type == RowType.STATE_BODY_HEADER:
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
        elif state == ProcessingState.PROGRAM and row_type == RowType.PROGRAM_HEADER:
            current_context["program_code"] = int(float(row_data[1]))
            current_context["program_name"] = row_data[3]
            current_context["program_goal"] = row_data[4]
            current_context["program_result_desc"] = row_data[5]
            current_context["program_total"] = float(row_data[6])
            logger.debug("New program: %s", current_context["program_code"])

        # Extract subprogram info (can happen in any state after READY)
        elif state != ProcessingState.INIT and row_type == RowType.SUBPROGRAM_HEADER:
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
                        "program_result_desc": current_context["program_result_desc"],
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
                logger.warning("Skipping invalid subprogram at row %d: %s", i, e)

        pbar.update(1)

    # ===================== MARK: Stats and Return =============================
    pbar.close()

    if overall_values is None:
        logger.error("Could not find overall values row with 'ԸՆԴԱՄԵՆԸ' in column 0")
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
        "Processed %d subprograms with overall values: %s",
        len(results),
        overall_values,
    )
    return result_df, overall_values, rowtype_stats, statetrans_stats
