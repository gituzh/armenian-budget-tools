"""MTEP (Mid-Term Expenditure Program) Excel parser for 2024 format.

Two-level hierarchy: state body → program (no subprograms).
Emits lean program-level rows (no subprogram columns).

Output columns:
- state_body
- program_code, program_name, program_goal, program_result_desc
- state_body_total_y0/y1/y2
- program_total_y0/y1/y2

Overall JSON contains:
{ "plan_years": [year, year+1, year+2],
  "overall_total_y0": ..., "overall_total_y1": ..., "overall_total_y2": ... }
"""

from __future__ import annotations

import logging
from typing import Dict, List
import pandas as pd
from tqdm import tqdm

from ._common import RowType, ProcessingState, is_numeric, normalize_str


logger = logging.getLogger(__name__)


def _detect_row_type_mtep_2024(row: List[str]) -> RowType:
    # Expect at least 5 columns: A:?, B:label/code, C:D:E values (y0,y1,y2)
    # GRAND_TOTAL: any of first 3 cells normalized == 'ընդամենը'
    label_cells = [normalize_str(c) for c in row[:3]]
    if any(c == "ընդամենը" for c in label_cells):
        return RowType.GRAND_TOTAL
    # STATE_BODY_HEADER: col0 empty, col1 text, and col2/3/4 numeric
    if (
        (not row[0].strip())
        and row[1].strip()
        and all(is_numeric(row[i]) for i in [2, 3, 4] if i < len(row))
    ):
        return RowType.STATE_BODY_HEADER
    # PROGRAM_HEADER: col0 numeric (program code), col1 text, col2/3/4 numeric
    if (
        row[0].strip()
        and is_numeric(row[0])
        and row[1].strip()
        and all(is_numeric(row[i]) for i in [2, 3, 4] if i < len(row))
    ):
        return RowType.PROGRAM_HEADER
    # EMPTY
    if not any(str(c).strip() for c in row[:5]):
        return RowType.EMPTY
    return RowType.UNKNOWN


def flatten_mtep_excel(
    excel_file_path: str,
    *,
    year: int,
) -> tuple[pd.DataFrame, Dict, Dict, Dict]:
    """Parse the 2024 MTEP Excel and return normalized DataFrame and metadata.

    Only the first sheet is parsed.
    """
    df = pd.read_excel(excel_file_path, sheet_name=0, header=None)
    df = df.fillna("")

    results: List[dict] = []
    rowtype_stats = {k: 0 for k in RowType}
    statetrans_stats = {k: 0 for k in ProcessingState}
    state = ProcessingState.INIT

    current_state_body = ""
    current_state_body_totals = {"y0": 0.0, "y1": 0.0, "y2": 0.0}
    program_context = {"goal": "", "result": ""}

    pbar = tqdm(
        total=len(df),
        desc=f"{'Processing MTEP':<31}",
        unit="rows",
        bar_format="{desc}{percentage:3.0f}%|{bar}| {n:>5}/{total:>5} [{elapsed}<{remaining}, {rate_fmt}]",
    )

    overall = {
        "overall_total_y0": 0.0,
        "overall_total_y1": 0.0,
        "overall_total_y2": 0.0,
    }

    i = 0
    while i < len(df):
        row = [str(df.loc[i, j]).strip() if j in df.columns else "" for j in range(6)]
        row_type = _detect_row_type_mtep_2024(row)
        rowtype_stats[row_type] += 1
        statetrans_stats[state] += 1

        if row_type == RowType.GRAND_TOTAL:
            state = ProcessingState.READY

            # Totals in C/D/E (indices 2/3/4)
            def _f(v: str) -> float:
                try:
                    return float(v) if is_numeric(v) else 0.0
                except Exception:
                    return 0.0

            overall = {
                "plan_years": [int(year), int(year) + 1, int(year) + 2],
                "overall_total_y0": _f(row[2]) if len(row) > 2 else 0.0,
                "overall_total_y1": _f(row[3]) if len(row) > 3 else 0.0,
                "overall_total_y2": _f(row[4]) if len(row) > 4 else 0.0,
            }
        elif row_type == RowType.STATE_BODY_HEADER:
            state = ProcessingState.STATE_BODY
            current_state_body = row[1]

            def _f(v: str) -> float:
                try:
                    return float(v) if is_numeric(v) else 0.0
                except Exception:
                    return 0.0

            current_state_body_totals = {
                "y0": _f(row[2]) if len(row) > 2 else 0.0,
                "y1": _f(row[3]) if len(row) > 3 else 0.0,
                "y2": _f(row[4]) if len(row) > 4 else 0.0,
            }
            # reset program context
            program_context = {"goal": "", "result": ""}
        elif row_type == RowType.PROGRAM_HEADER:
            state = ProcessingState.PROGRAM
            program_code = int(float(row[0]))
            program_name = row[1]
            # Attempt to read next four lines for goal/result like budget law (optional)
            goal = ""
            result = ""
            # We expect optional pattern of up to 5 lines with labels alternating
            # To avoid strict label enforcement, just capture positions 2 and 4 if present
            # under same assumption as historical parser
            # Line i+1..i+5 might contain details
            detail_vals: List[str] = []
            for offset in range(5):
                j = i + 1 + offset
                if j >= len(df):
                    detail_vals.append("")
                else:
                    detail_vals.append(str(df.loc[j, 1]).strip())
            # positions 1 and 3 are labels in budget structure; values at 0,2,4
            # In 2024 layout, the first detail value (next line col B) holds the program name
            program_name = detail_vals[0] if len(detail_vals) > 0 else program_name
            goal = detail_vals[2] if len(detail_vals) > 2 else ""
            result = detail_vals[4] if len(detail_vals) > 4 else ""
            program_context = {"goal": goal, "result": result}

            # Totals for program in C/D/E
            def _f(v: str) -> float:
                try:
                    return float(v) if is_numeric(v) else 0.0
                except Exception:
                    return 0.0

            program_totals = {
                "y0": _f(row[2]) if len(row) > 2 else 0.0,
                "y1": _f(row[3]) if len(row) > 3 else 0.0,
                "y2": _f(row[4]) if len(row) > 4 else 0.0,
            }

            record = {
                "state_body": current_state_body,
                "program_code": program_code,
                "program_name": program_name,
                "program_goal": program_context["goal"],
                "program_result_desc": program_context["result"],
                # totals
                "state_body_total_y0": current_state_body_totals["y0"],
                "state_body_total_y1": current_state_body_totals["y1"],
                "state_body_total_y2": current_state_body_totals["y2"],
                "program_total_y0": program_totals["y0"],
                "program_total_y1": program_totals["y1"],
                "program_total_y2": program_totals["y2"],
            }
            results.append(record)

        i += 1
        pbar.update(1)

    pbar.close()

    col_order = [
        "state_body",
        "program_code",
        "program_name",
        "program_goal",
        "program_result_desc",
        "state_body_total_y0",
        "state_body_total_y1",
        "state_body_total_y2",
        "program_total_y0",
        "program_total_y1",
        "program_total_y2",
    ]
    result_df = pd.DataFrame(results, columns=col_order)

    return result_df, overall, rowtype_stats, statetrans_stats
