"""2025 Excel parser implementation (migrated from legacy module)."""

from __future__ import annotations

import logging
import sys
from typing import List
import pandas as pd
from tqdm import tqdm
from ._common import ProcessingState, RowType, is_numeric
from armenian_budget.core.enums import SourceType


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
        # In 2025 spending, many rows have F (type) empty and sometimes G empty.
        # Treat as subprogram when basic descriptor columns (D, E) are present.
        and col3.strip()
        and col4.strip()
    ):
        return RowType.SUBPROGRAM_HEADER
    return RowType.UNKNOWN


def flatten_budget_excel_2025(
    excel_file_path: str,
    source_type: SourceType = SourceType.BUDGET_LAW,
) -> tuple[pd.DataFrame, float | dict, dict, dict]:
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
        # For BUDGET_LAW this is used; for SPENDING_* we will populate dynamic fields
        "state_body_total": 0.0,
        "program_code": 0,
        "program_name": "",
        "program_goal": "",
        "program_result_desc": "",
        # For BUDGET_LAW this is used; for SPENDING_* we will populate dynamic fields
        "program_total": 0.0,
    }

    rowtype_stats = {k: 0 for k in RowType}
    statetrans_stats = {k: 0 for k in ProcessingState}

    # ===================== MARK: Main Loop ====================================
    # Pad desc to align with 2019-2024 label width; include unit rows
    pbar = tqdm(
        total=len(df),
        desc=f"{'Processing 2025 ' + source_type.name:<31}",
        unit="rows",
        bar_format="{desc}{percentage:3.0f}%|{bar}| {n:>5}/{total:>5} [{elapsed}<{remaining}, {rate_fmt}]",
    )

    for i in range(len(df)):
        # Read a sufficient number of columns.
        # 2025 BUDGET_LAW uses 7 columns (0..6), 2025 SPENDING uses additional value columns.
        read_width = 14 if source_type != SourceType.BUDGET_LAW else 7
        row_data = [
            str(df.loc[i, col]).strip() if col < len(df.columns) else ""
            for col in range(read_width)
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
            # Overall values
            if source_type == SourceType.BUDGET_LAW:
                if not is_numeric(row_data[6]):
                    logger.error("Overall value at row %d, col 6 is not numeric", i)
                    sys.exit(1)
                overall_values = {"overall_total": float(row_data[6])}
            elif source_type in (
                SourceType.SPENDING_Q1,
                SourceType.SPENDING_Q12,
                SourceType.SPENDING_Q123,
            ):
                # Column mapping for 2025 spending (Q1/Q12/Q123)
                # G..M → indices 6..12
                def _to_float(val: str) -> float:
                    try:
                        return float(val)
                    except Exception:
                        return 0.0

                def _to_frac(val: str) -> float:
                    try:
                        v = str(val).replace("%", "").strip()
                        return float(v) / 100.0 if v else 0.0
                    except Exception:
                        return 0.0

                overall_values = {
                    "overall_annual_plan": _to_float(
                        row_data[6] if len(row_data) > 6 else ""
                    ),
                    "overall_rev_annual_plan": _to_float(
                        row_data[7] if len(row_data) > 7 else ""
                    ),
                    "overall_period_plan": _to_float(
                        row_data[8] if len(row_data) > 8 else ""
                    ),
                    "overall_rev_period_plan": _to_float(
                        row_data[9] if len(row_data) > 9 else ""
                    ),
                    "overall_actual": _to_float(
                        row_data[10] if len(row_data) > 10 else ""
                    ),
                    "overall_actual_vs_rev_annual_plan": _to_frac(
                        row_data[11] if len(row_data) > 11 else ""
                    ),
                    "overall_actual_vs_rev_period_plan": _to_frac(
                        row_data[12] if len(row_data) > 12 else ""
                    ),
                }
            elif source_type == SourceType.SPENDING_Q1234:

                def _to_float(val: str) -> float:
                    try:
                        return float(val)
                    except Exception:
                        return 0.0

                def _to_frac(val: str) -> float:
                    try:
                        v = str(val).replace("%", "").strip()
                        return float(v) / 100.0 if v else 0.0
                    except Exception:
                        return 0.0

                overall_values = {
                    "overall_annual_plan": _to_float(
                        row_data[6] if len(row_data) > 6 else ""
                    ),
                    "overall_rev_annual_plan": _to_float(
                        row_data[7] if len(row_data) > 7 else ""
                    ),
                    "overall_actual": _to_float(
                        row_data[10] if len(row_data) > 10 else ""
                    ),
                    "overall_actual_vs_rev_annual_plan": _to_frac(
                        row_data[11] if len(row_data) > 11 else ""
                    ),
                }
            logger.info("Found overall row: %s", overall_values)

        # Extract state body info
        elif (
            state == ProcessingState.STATE_BODY
            and row_type == RowType.STATE_BODY_HEADER
        ):
            current_context["state_body"] = row_data[0]
            # Populate context depending on source type
            if source_type == SourceType.BUDGET_LAW:
                current_context["state_body_total"] = (
                    float(row_data[6]) if is_numeric(row_data[6]) else 0.0
                )
            elif source_type in (
                SourceType.SPENDING_Q1,
                SourceType.SPENDING_Q12,
                SourceType.SPENDING_Q123,
            ):
                # Annual/revised/period/revised-period/actual + 2 pct columns
                current_context["state_body_annual_plan"] = (
                    float(row_data[6]) if is_numeric(row_data[6]) else 0.0
                )
                current_context["state_body_rev_annual_plan"] = (
                    float(row_data[7]) if is_numeric(row_data[7]) else 0.0
                )
                current_context["state_body_period_plan"] = (
                    float(row_data[8]) if is_numeric(row_data[8]) else 0.0
                )
                current_context["state_body_rev_period_plan"] = (
                    float(row_data[9]) if is_numeric(row_data[9]) else 0.0
                )
                current_context["state_body_actual"] = (
                    float(row_data[10]) if is_numeric(row_data[10]) else 0.0
                )

                # Percentages are fractions
                def _frac(v: str) -> float:
                    try:
                        s = str(v).replace("%", "").strip()
                        return float(s) / 100.0 if s else 0.0
                    except Exception:
                        return 0.0

                current_context["state_body_actual_vs_rev_annual_plan"] = _frac(
                    row_data[11] if len(row_data) > 11 else ""
                )
                current_context["state_body_actual_vs_rev_period_plan"] = _frac(
                    row_data[12] if len(row_data) > 12 else ""
                )
            elif source_type == SourceType.SPENDING_Q1234:
                current_context["state_body_annual_plan"] = (
                    float(row_data[6]) if is_numeric(row_data[6]) else 0.0
                )
                current_context["state_body_rev_annual_plan"] = (
                    float(row_data[7]) if is_numeric(row_data[7]) else 0.0
                )
                current_context["state_body_actual"] = (
                    float(row_data[10]) if is_numeric(row_data[10]) else 0.0
                )

                def _frac(v: str) -> float:
                    try:
                        s = str(v).replace("%", "").strip()
                        return float(s) / 100.0 if s else 0.0
                    except Exception:
                        return 0.0

                current_context["state_body_actual_vs_rev_annual_plan"] = _frac(
                    row_data[11] if len(row_data) > 11 else ""
                )

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
            if source_type == SourceType.BUDGET_LAW:
                current_context["program_total"] = (
                    float(row_data[6]) if is_numeric(row_data[6]) else 0.0
                )
            elif source_type in (
                SourceType.SPENDING_Q1,
                SourceType.SPENDING_Q12,
                SourceType.SPENDING_Q123,
            ):
                current_context["program_annual_plan"] = (
                    float(row_data[6]) if is_numeric(row_data[6]) else 0.0
                )
                current_context["program_rev_annual_plan"] = (
                    float(row_data[7]) if is_numeric(row_data[7]) else 0.0
                )
                current_context["program_period_plan"] = (
                    float(row_data[8]) if is_numeric(row_data[8]) else 0.0
                )
                current_context["program_rev_period_plan"] = (
                    float(row_data[9]) if is_numeric(row_data[9]) else 0.0
                )
                current_context["program_actual"] = (
                    float(row_data[10]) if is_numeric(row_data[10]) else 0.0
                )

                def _frac(v: str) -> float:
                    try:
                        s = str(v).replace("%", "").strip()
                        return float(s) / 100.0 if s else 0.0
                    except Exception:
                        return 0.0

                current_context["program_actual_vs_rev_annual_plan"] = _frac(
                    row_data[11] if len(row_data) > 11 else ""
                )
                current_context["program_actual_vs_rev_period_plan"] = _frac(
                    row_data[12] if len(row_data) > 12 else ""
                )
            elif source_type == SourceType.SPENDING_Q1234:
                current_context["program_annual_plan"] = (
                    float(row_data[6]) if is_numeric(row_data[6]) else 0.0
                )
                current_context["program_rev_annual_plan"] = (
                    float(row_data[7]) if is_numeric(row_data[7]) else 0.0
                )
                current_context["program_actual"] = (
                    float(row_data[10]) if is_numeric(row_data[10]) else 0.0
                )

                def _frac(v: str) -> float:
                    try:
                        s = str(v).replace("%", "").strip()
                        return float(s) / 100.0 if s else 0.0
                    except Exception:
                        return 0.0

                current_context["program_actual_vs_rev_annual_plan"] = _frac(
                    row_data[11] if len(row_data) > 11 else ""
                )
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

                # Build base record common fields
                base_record = {
                    "state_body": current_context["state_body"],
                    "program_code": current_context["program_code"],
                    "program_code_ext": program_code_ext,
                    "program_name": current_context["program_name"],
                    "program_goal": current_context["program_goal"],
                    "program_result_desc": current_context["program_result_desc"],
                    "subprogram_code": subprogram_code,
                    "subprogram_name": row_data[3],
                    "subprogram_desc": row_data[4],
                    "subprogram_type": row_data[5],
                }

                if source_type == SourceType.BUDGET_LAW:
                    record = {
                        **base_record,
                        "state_body_total": current_context["state_body_total"],
                        "program_total": current_context["program_total"],
                        "subprogram_total": float(row_data[6])
                        if is_numeric(row_data[6])
                        else 0.0,
                    }
                elif source_type in (
                    SourceType.SPENDING_Q1,
                    SourceType.SPENDING_Q12,
                    SourceType.SPENDING_Q123,
                ):

                    def _frac(v: str) -> float:
                        try:
                            s = str(v).replace("%", "").strip()
                            return float(s) / 100.0 if s else 0.0
                        except Exception:
                            return 0.0

                    record = {
                        **base_record,
                        # State body level roll-ups carried from context
                        "state_body_annual_plan": current_context.get(
                            "state_body_annual_plan", 0.0
                        ),
                        "state_body_rev_annual_plan": current_context.get(
                            "state_body_rev_annual_plan", 0.0
                        ),
                        "state_body_period_plan": current_context.get(
                            "state_body_period_plan", 0.0
                        ),
                        "state_body_rev_period_plan": current_context.get(
                            "state_body_rev_period_plan", 0.0
                        ),
                        "state_body_actual": current_context.get(
                            "state_body_actual", 0.0
                        ),
                        "state_body_actual_vs_rev_annual_plan": current_context.get(
                            "state_body_actual_vs_rev_annual_plan", 0.0
                        ),
                        "state_body_actual_vs_rev_period_plan": current_context.get(
                            "state_body_actual_vs_rev_period_plan", 0.0
                        ),
                        # Program level from context
                        "program_annual_plan": current_context.get(
                            "program_annual_plan", 0.0
                        ),
                        "program_rev_annual_plan": current_context.get(
                            "program_rev_annual_plan", 0.0
                        ),
                        "program_period_plan": current_context.get(
                            "program_period_plan", 0.0
                        ),
                        "program_rev_period_plan": current_context.get(
                            "program_rev_period_plan", 0.0
                        ),
                        "program_actual": current_context.get("program_actual", 0.0),
                        "program_actual_vs_rev_annual_plan": current_context.get(
                            "program_actual_vs_rev_annual_plan", 0.0
                        ),
                        "program_actual_vs_rev_period_plan": current_context.get(
                            "program_actual_vs_rev_period_plan", 0.0
                        ),
                        # Subprogram level from current row
                        "subprogram_annual_plan": float(row_data[6])
                        if is_numeric(row_data[6])
                        else 0.0,
                        "subprogram_rev_annual_plan": float(row_data[7])
                        if is_numeric(row_data[7])
                        else 0.0,
                        "subprogram_period_plan": float(row_data[8])
                        if is_numeric(row_data[8])
                        else 0.0,
                        "subprogram_rev_period_plan": float(row_data[9])
                        if is_numeric(row_data[9])
                        else 0.0,
                        "subprogram_actual": float(row_data[10])
                        if is_numeric(row_data[10])
                        else 0.0,
                        "subprogram_actual_vs_rev_annual_plan": _frac(
                            row_data[11] if len(row_data) > 11 else ""
                        ),
                        "subprogram_actual_vs_rev_period_plan": _frac(
                            row_data[12] if len(row_data) > 12 else ""
                        ),
                    }
                else:  # SPENDING_Q1234

                    def _frac(v: str) -> float:
                        try:
                            s = str(v).replace("%", "").strip()
                            return float(s) / 100.0 if s else 0.0
                        except Exception:
                            return 0.0

                    record = {
                        **base_record,
                        # State body from context
                        "state_body_annual_plan": current_context.get(
                            "state_body_annual_plan", 0.0
                        ),
                        "state_body_rev_annual_plan": current_context.get(
                            "state_body_rev_annual_plan", 0.0
                        ),
                        "state_body_actual": current_context.get(
                            "state_body_actual", 0.0
                        ),
                        "state_body_actual_vs_rev_annual_plan": current_context.get(
                            "state_body_actual_vs_rev_annual_plan", 0.0
                        ),
                        # Program from context
                        "program_annual_plan": current_context.get(
                            "program_annual_plan", 0.0
                        ),
                        "program_rev_annual_plan": current_context.get(
                            "program_rev_annual_plan", 0.0
                        ),
                        "program_actual": current_context.get("program_actual", 0.0),
                        "program_actual_vs_rev_annual_plan": current_context.get(
                            "program_actual_vs_rev_annual_plan", 0.0
                        ),
                        # Subprogram from row
                        "subprogram_annual_plan": float(row_data[6])
                        if is_numeric(row_data[6])
                        else 0.0,
                        "subprogram_rev_annual_plan": float(row_data[7])
                        if is_numeric(row_data[7])
                        else 0.0,
                        "subprogram_actual": float(row_data[10])
                        if is_numeric(row_data[10])
                        else 0.0,
                        "subprogram_actual_vs_rev_annual_plan": _frac(
                            row_data[11] if len(row_data) > 11 else ""
                        ),
                    }

                results.append(record)
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
    if source_type == SourceType.BUDGET_LAW:
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
    elif source_type in (
        SourceType.SPENDING_Q1,
        SourceType.SPENDING_Q12,
        SourceType.SPENDING_Q123,
    ):
        col_order = [
            "state_body",
            "program_code",
            "program_code_ext",
            "program_name",
            "program_goal",
            "program_result_desc",
            "subprogram_code",
            "subprogram_name",
            "subprogram_desc",
            "subprogram_type",
            # State body
            "state_body_annual_plan",
            "state_body_rev_annual_plan",
            "state_body_period_plan",
            "state_body_rev_period_plan",
            "state_body_actual",
            "state_body_actual_vs_rev_annual_plan",
            "state_body_actual_vs_rev_period_plan",
            # Program
            "program_annual_plan",
            "program_rev_annual_plan",
            "program_period_plan",
            "program_rev_period_plan",
            "program_actual",
            "program_actual_vs_rev_annual_plan",
            "program_actual_vs_rev_period_plan",
            # Subprogram
            "subprogram_annual_plan",
            "subprogram_rev_annual_plan",
            "subprogram_period_plan",
            "subprogram_rev_period_plan",
            "subprogram_actual",
            "subprogram_actual_vs_rev_annual_plan",
            "subprogram_actual_vs_rev_period_plan",
        ]
    else:  # SPENDING_Q1234
        col_order = [
            "state_body",
            "program_code",
            "program_code_ext",
            "program_name",
            "program_goal",
            "program_result_desc",
            "subprogram_code",
            "subprogram_name",
            "subprogram_desc",
            "subprogram_type",
            # State body
            "state_body_annual_plan",
            "state_body_rev_annual_plan",
            "state_body_actual",
            "state_body_actual_vs_rev_annual_plan",
            # Program
            "program_annual_plan",
            "program_rev_annual_plan",
            "program_actual",
            "program_actual_vs_rev_annual_plan",
            # Subprogram
            "subprogram_annual_plan",
            "subprogram_rev_annual_plan",
            "subprogram_actual",
            "subprogram_actual_vs_rev_annual_plan",
        ]

    result_df = pd.DataFrame(results, columns=col_order)
    logger.info(
        "Processed %d subprograms with overall values: %s",
        len(results),
        overall_values,
    )
    return result_df, overall_values, rowtype_stats, statetrans_stats
