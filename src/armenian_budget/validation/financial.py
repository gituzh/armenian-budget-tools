from __future__ import annotations

from typing import List
import pandas as pd


def validate_financial_totals_consistency(data, tolerance: float = 0.01) -> List[str]:
    """Validate hierarchical totals consistency using test helper logic.

    Ports tests/utils/validation_helpers.validate_financial_totals_consistency
    behavior into a callable suitable for CLI/API.
    """
    df = data.df if hasattr(data, "df") else data
    errors: List[str] = []

    def _check_state_body_consistency(
        df: pd.DataFrame, state_body_col: str, program_col: str
    ) -> List[str]:
        msgs: List[str] = []
        for state_body in df["state_body"].unique():
            state_body_data = df[df["state_body"] == state_body]
            state_body_total = round(state_body_data[state_body_col].iloc[0], 2)
            program_sum = round(
                state_body_data.drop_duplicates(subset="program_code")[program_col].sum(), 2
            )
            if abs(state_body_total - program_sum) > tolerance:
                msgs.append(
                    f"  {state_body}: {state_body_total} vs {program_sum} (diff: {state_body_total - program_sum})"
                )
        return msgs

    def _check_state_body_subprogram_consistency(
        df: pd.DataFrame, state_body_col: str, subprogram_col: str
    ) -> List[str]:
        msgs: List[str] = []
        for state_body in df["state_body"].unique():
            state_body_data = df[df["state_body"] == state_body]
            state_body_total = round(state_body_data[state_body_col].iloc[0], 2)
            subprogram_sum = round(state_body_data[subprogram_col].sum(), 2)
            if abs(state_body_total - subprogram_sum) > tolerance:
                msgs.append(
                    f"  {state_body}: {state_body_total} vs {subprogram_sum} (diff: {state_body_total - subprogram_sum})"
                )
        return msgs

    def _check_program_consistency(
        df: pd.DataFrame, program_col: str, subprogram_col: str
    ) -> List[str]:
        msgs: List[str] = []
        subprogram_sums = (
            df.groupby(["state_body", "program_code"])[subprogram_col].sum().reset_index()
        )
        program_totals = df.drop_duplicates(subset=["state_body", "program_code"])[
            ["state_body", "program_code", program_col]
        ]
        merged = subprogram_sums.merge(program_totals, on=["state_body", "program_code"])
        mismatches = merged[abs(merged[subprogram_col] - merged[program_col]) > tolerance]
        for _, row in mismatches.iterrows():
            msgs.append(
                f"  {row['state_body']} - Program {row['program_code']}: {row[program_col]} vs {row[subprogram_col]} (diff: {row[program_col] - row[subprogram_col]})"
            )
        return msgs

    # Infer source type from available columns
    if "subprogram_total" in df.columns:
        financial_cols = {
            "state_body": ["state_body_total"],
            "program": ["program_total"],
            "subprogram": ["subprogram_total"],
        }
    else:
        base_cols = [
            "annual_plan",
            "rev_annual_plan",
            "period_plan",
            "rev_period_plan",
            "actual",
        ]
        financial_cols = {
            "state_body": [f"state_body_{c}" for c in base_cols if f"state_body_{c}" in df.columns],
            "program": [f"program_{c}" for c in base_cols if f"program_{c}" in df.columns],
            "subprogram": [
                f"subprogram_{c}"
                for c in df.columns
                if c.startswith("subprogram_") and c.split("_")[1] in base_cols
            ],
        }

    for col_type in financial_cols["state_body"]:
        base_name = col_type.replace("state_body_", "")
        program_col = f"program_{base_name}" if base_name else "program_total"
        subprogram_col = f"subprogram_{base_name}" if base_name else "subprogram_total"

        if program_col in df.columns and subprogram_col in df.columns:
            sb_prog = _check_state_body_consistency(df, col_type, program_col)
            if sb_prog:
                errors.extend([f"State body {col_type} vs program sums inconsistencies:"] + sb_prog)
            sb_sub = _check_state_body_subprogram_consistency(df, col_type, subprogram_col)
            if sb_sub:
                errors.extend(
                    [f"State body {col_type} vs subprogram sums inconsistencies:"] + sb_sub
                )
            prog = _check_program_consistency(df, program_col, subprogram_col)
            if prog:
                errors.extend([f"Program {program_col} inconsistencies:"] + prog)

    return errors


def validate_percentage_ranges(data) -> List[str]:
    df = data.df if hasattr(data, "df") else data
    errors: List[str] = []
    pct_cols = [
        c
        for c in df.columns
        if c.endswith("_actual_vs_rev_annual_plan") or c.endswith("_actual_vs_rev_period_plan")
    ]
    for col in pct_cols:
        invalid = df[(df[col] < 0) | (df[col] > 1)]
        if not invalid.empty:
            errors.append(f"{len(invalid)} invalid percentage values in {col} (outside 0-1 range)")
    return errors


def validate_logical_relationships_spending(data) -> List[str]:
    df = data.df if hasattr(data, "df") else data
    errors: List[str] = []

    def has_cols(*cols: str) -> bool:
        return all(c in df.columns for c in cols)

    if has_cols("subprogram_period_plan", "subprogram_annual_plan"):
        v = df[df["subprogram_period_plan"] > df["subprogram_annual_plan"]]
        if not v.empty:
            errors.append(f"{len(v)} violations where subprogram period_plan > annual_plan")

    if has_cols("subprogram_rev_period_plan", "subprogram_rev_annual_plan"):
        v = df[df["subprogram_rev_period_plan"] > df["subprogram_rev_annual_plan"]]
        if not v.empty:
            errors.append(f"{len(v)} violations where subprogram rev_period_plan > rev_annual_plan")

    return errors


def validate_data_quality_basic(data) -> List[str]:
    df = data.df if hasattr(data, "df") else data
    errors: List[str] = []
    required_columns = [
        "state_body",
        "program_code",
        "program_name",
        "subprogram_code",
        "subprogram_name",
    ]
    for column in required_columns:
        if column not in df.columns:
            errors.append(f"Missing column '{column}'")
            continue
        if df[column].isnull().sum() > 0:
            errors.append(f"Null values in '{column}'")
        if df[column].dtype == "object":
            if (df[column].astype(str).str.strip() == "").sum() > 0:
                errors.append(f"Empty strings in '{column}'")
    return errors
