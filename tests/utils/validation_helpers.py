"""Reusable validation functions for budget data testing."""

import pandas as pd
import warnings
from typing import List
import sys
from pathlib import Path

# Handle imports for both direct execution and pytest
try:
    from .conftest import (
        BudgetDataInfo,
        get_financial_columns,
        get_percentage_columns,
    )
except ImportError:
    # Fallback for direct execution
    test_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(test_dir))
    from conftest import (
        BudgetDataInfo,
        get_financial_columns,
        get_percentage_columns,
    )


def validate_financial_totals_consistency(
    data: BudgetDataInfo, tolerance: float = 0.01
) -> List[str]:
    """
    Validate that financial totals are consistent across hierarchy levels.

    Args:
        data: Budget data information
        tolerance: Acceptable difference for floating point comparisons

    Returns:
        List of error messages (empty if all checks pass)
    """
    errors = []
    df = data.df
    financial_cols = get_financial_columns(data.source_type)

    # Allow higher absolute tolerance for spending reports to account for
    # repeated section totals and rounding accumulation across many rows
    local_tolerance = tolerance
    if str(data.source_type).startswith("SPENDING_"):
        local_tolerance = max(local_tolerance, 1.0)

    # For each financial column type, check consistency
    for col_type in financial_cols["state_body"]:
        base_name = col_type.replace("state_body_", "")
        program_col = f"program_{base_name}"
        subprogram_col = f"subprogram_{base_name}"

        if program_col in df.columns and subprogram_col in df.columns:
            # Check state body totals vs program sums (account for multiple sections per state body)
            state_body_program_mismatches = _check_state_body_consistency(
                df, col_type, program_col, local_tolerance
            )
            if state_body_program_mismatches:
                errors.extend(
                    [
                        f"{data.year}/{data.source_type}: State body {col_type} "
                        "vs program sums inconsistencies:"
                    ]
                    + state_body_program_mismatches
                )

            # Check state body totals vs subprogram sums (ADDED MISSING VALIDATION)
            state_body_subprogram_mismatches = (
                _check_state_body_subprogram_consistency(
                    df, col_type, subprogram_col, local_tolerance
                )
            )
            if state_body_subprogram_mismatches:
                errors.extend(
                    [
                        f"{data.year}/{data.source_type}: State body {col_type} "
                        "vs subprogram sums inconsistencies:"
                    ]
                    + state_body_subprogram_mismatches
                )

            # Check program totals vs subprogram sums (per state-body section)
            program_mismatches = _check_program_consistency(
                df, program_col, subprogram_col, col_type, local_tolerance
            )
            if program_mismatches:
                errors.extend(
                    [
                        f"{data.year}/{data.source_type}: Program {program_col} "
                        "inconsistencies:"
                    ]
                    + program_mismatches
                )

    return errors


def _check_state_body_consistency(
    df: pd.DataFrame, state_body_col: str, program_col: str, tolerance: float
) -> List[str]:
    """Check consistency between state body totals and program sums.

    For spending reports where a state body appears in multiple sections with
    different totals, compare the sum of distinct state-body totals to the sum
    of program totals de-duplicated by (state_body total value, program_code).
    """
    errors = []

    for state_body in df["state_body"].unique():
        state_body_data = df[df["state_body"] == state_body]

        # Sum distinct state body totals to account for multiple sections
        state_body_total_sum = round(
            state_body_data.drop_duplicates(subset=[state_body_col])[
                state_body_col
            ].sum(),
            2,
        )

        # Sum program totals per (section,total) and program
        program_sum = round(
            state_body_data.drop_duplicates(
                subset=[state_body_col, "program_code"]
            )[program_col].sum(),
            2,
        )

        if abs(state_body_total_sum - program_sum) > tolerance:
            errors.append(
                f"  {state_body}: {state_body_total_sum} vs {program_sum} "
                f"(diff: {state_body_total_sum - program_sum})"
            )

    return errors


def _check_state_body_subprogram_consistency(
    df: pd.DataFrame, state_body_col: str, subprogram_col: str, tolerance: float
) -> List[str]:
    """Check consistency between state body totals and direct subprogram sums (per sections)."""
    errors = []

    for state_body in df["state_body"].unique():
        state_body_data = df[df["state_body"] == state_body]
        state_body_total_sum = round(
            state_body_data.drop_duplicates(subset=[state_body_col])[
                state_body_col
            ].sum(),
            2,
        )
        subprogram_sum = round(state_body_data[subprogram_col].sum(), 2)

        if abs(state_body_total_sum - subprogram_sum) > tolerance:
            errors.append(
                f"  {state_body}: {state_body_total_sum} vs {subprogram_sum} "
                f"(diff: {state_body_total_sum - subprogram_sum})"
            )

    return errors


def _check_program_consistency(
    df: pd.DataFrame,
    program_col: str,
    subprogram_col: str,
    state_body_col: str,
    tolerance: float,
) -> List[str]:
    """Check consistency between program totals and subprogram sums per state-body section."""
    errors = []

    subprogram_sums = (
        df.groupby(["state_body", state_body_col, "program_code"])[
            subprogram_col
        ]
        .sum()
        .reset_index()
    )

    program_totals = df.drop_duplicates(
        subset=["state_body", state_body_col, "program_code"]
    )[["state_body", state_body_col, "program_code", program_col]]

    merged = subprogram_sums.merge(
        program_totals, on=["state_body", state_body_col, "program_code"]
    )
    mismatches = merged[
        abs(merged[subprogram_col] - merged[program_col]) > tolerance
    ]

    for _, row in mismatches.iterrows():
        errors.append(
            f"  {row['state_body']} - Program {row['program_code']}: "
            f"{row[program_col]} vs {row[subprogram_col]} "
            f"(diff: {row[program_col] - row[subprogram_col]})"
        )

    return errors


def validate_percentage_ranges(data: BudgetDataInfo) -> List[str]:
    """
    Validate that percentage columns contain values between 0 and 1.

    Args:
        data: Budget data information

    Returns:
        List of error messages (empty if all checks pass)
    """
    errors = []
    df = data.df
    percentage_cols = get_percentage_columns(data.source_type)

    # Flatten all percentage columns
    all_pct_cols = []
    for level_cols in percentage_cols.values():
        all_pct_cols.extend(level_cols)

    for col in all_pct_cols:
        if col in df.columns:
            # Negative percentages are errors
            neg_count = int((df[col] < 0).sum())
            if neg_count > 0:
                errors.append(
                    f"{data.year}/{data.source_type}: {neg_count} "
                    f"negative percentage values in {col}"
                )

            # Percentages above 1 (overspend) are allowed but should warn
            overs = df[df[col] > 1]
            over_count = int(len(overs))
            if over_count > 0:
                # Build informative, compact warning with examples
                top = overs.sort_values(by=col, ascending=False)[
                    [
                        "state_body",
                        "program_code",
                        "subprogram_code",
                        col,
                    ]
                ].head(5)
                lines = [
                    f"{data.year}/{data.source_type}: {over_count} percentage values > 1 in {col} (overspend allowed)",
                    f"  max={overs[col].max():.6f}",
                    "  examples:",
                ]
                for _, r in top.iterrows():
                    lines.append(
                        "   - "
                        f"{r['state_body']} | Program {int(r['program_code'])} | Subprogram {int(r['subprogram_code'])} | "
                        f"{col}={r[col]:.6f}"
                    )
                warnings.warn("\n".join(lines))

    return errors


def validate_logical_relationships_spending(data: BudgetDataInfo) -> List[str]:
    """
    Validate logical relationships in spending data:
    - period_plan <= annual_plan
    - rev_period_plan <= rev_annual_plan
    - actual values should be reasonable

    Args:
        data: Budget data information

    Returns:
        List of error messages (empty if all checks pass)
    """
    errors = []

    if not data.source_type.startswith("SPENDING_"):
        return errors

    df = data.df
    financial_cols = get_financial_columns(data.source_type)

    # Check for each level (state_body, program, subprogram)
    for level, cols in financial_cols.items():
        level_cols = {col.replace(f"{level}_", ""): col for col in cols}

        # Check period_plan <= annual_plan
        if "period_plan" in level_cols and "annual_plan" in level_cols:
            period_col = level_cols["period_plan"]
            annual_col = level_cols["annual_plan"]

            over_mask = df[period_col] > df[annual_col]
            mask_nonneg = (df[period_col] >= 0) & (df[annual_col] >= 0)
            mask_has_neg = ~mask_nonneg

            # If revised columns exist and satisfy the constraint, downgrade to warning
            r_ok_mask = None
            if (
                "rev_period_plan" in level_cols
                and "rev_annual_plan" in level_cols
            ):
                rperiod_col = level_cols["rev_period_plan"]
                rannual_col = level_cols["rev_annual_plan"]
                r_ok_mask = df[rperiod_col] <= df[rannual_col]

            # Strict violations: non-negative and not covered by a valid revised relationship
            if r_ok_mask is not None:
                strict_mask = mask_nonneg & over_mask & (~r_ok_mask)
                warn_mask = (mask_nonneg & over_mask & r_ok_mask) | (
                    mask_has_neg & over_mask
                )
            else:
                strict_mask = mask_nonneg & over_mask
                warn_mask = mask_has_neg & over_mask

            strict_count = int(strict_mask.sum())
            warn_count = int(warn_mask.sum())

            if strict_count > 0:
                errors.append(
                    f"{data.year}/{data.source_type}: {strict_count} violations where "
                    f"{level} period_plan > annual_plan"
                )
            if warn_count > 0:
                # Split reasons for better guidance
                lines_main = [
                    f"{data.year}/{data.source_type}: {int(warn_count)} cases where {level} period_plan > annual_plan (downgraded to warnings)",
                ]
                if r_ok_mask is not None:
                    warn_due_revised = mask_nonneg & over_mask & r_ok_mask
                    count_rev = int(warn_due_revised.sum())
                    if count_rev > 0:
                        df_rev = df[warn_due_revised].copy()
                        df_rev["delta"] = (
                            df_rev[period_col] - df_rev[annual_col]
                        )
                        top_rev = df_rev.sort_values(
                            "delta", ascending=False
                        ).head(5)
                        lines_main.append(
                            f"  - {count_rev} with revised constraint satisfied (rev_period <= rev_annual):"
                        )
                        for _, r in top_rev.iterrows():
                            lines_main.append(
                                "     * "
                                f"{r.get('state_body', '')} | Program {r.get('program_code', '')} | Subprogram {r.get('subprogram_code', '')} | "
                                f"period={r[period_col]:.6f}, annual={r[annual_col]:.6f}, delta={r['delta']:.6f}"
                            )
                warn_due_neg = mask_has_neg & over_mask
                count_neg = int(warn_due_neg.sum())
                if count_neg > 0:
                    df_neg = df[warn_due_neg].copy()
                    df_neg["delta"] = df_neg[period_col] - df[annual_col]
                    top_neg = df_neg.sort_values("delta", ascending=False).head(
                        5
                    )
                    lines_main.append(
                        f"  - {count_neg} with negative values present:"
                    )
                    for _, r in top_neg.iterrows():
                        lines_main.append(
                            "     * "
                            f"{r.get('state_body', '')} | Program {r.get('program_code', '')} | Subprogram {r.get('subprogram_code', '')} | "
                            f"period={r[period_col]:.6f}, annual={r[annual_col]:.6f}, delta={r['delta']:.6f}"
                        )
                warnings.warn("\n".join(lines_main))

        # Check rev_period_plan <= rev_annual_plan
        if "rev_period_plan" in level_cols and "rev_annual_plan" in level_cols:
            rperiod_col = level_cols["rev_period_plan"]
            rannual_col = level_cols["rev_annual_plan"]

            mask_nonneg = (df[rperiod_col] >= 0) & (df[rannual_col] >= 0)
            strict_viol = df[mask_nonneg & (df[rperiod_col] > df[rannual_col])]
            if not strict_viol.empty:
                errors.append(
                    f"{data.year}/{data.source_type}: {len(strict_viol)} violations where "
                    f"{level} rev_period_plan > rev_annual_plan"
                )

            mask_has_neg = ~mask_nonneg
            warn_viol = df[mask_has_neg & (df[rperiod_col] > df[rannual_col])]
            if not warn_viol.empty:
                top = warn_viol.copy()
                top["delta"] = top[rperiod_col] - top[rannual_col]
                top = top.sort_values("delta", ascending=False).head(5)
                lines = [
                    f"{data.year}/{data.source_type}: {len(warn_viol)} cases (with negative values) where {level} rev_period_plan > rev_annual_plan",
                    "  examples:",
                ]
                for _, r in top.iterrows():
                    lines.append(
                        "   - "
                        f"{r.get('state_body', '')} | Program {r.get('program_code', '')} | Subprogram {r.get('subprogram_code', '')} | "
                        f"rev_period={r[rperiod_col]:.6f}, rev_annual={r[rannual_col]:.6f}, delta={r['delta']:.6f}"
                    )
                warnings.warn("\n".join(lines))

    return errors


def validate_data_quality_basic(data: BudgetDataInfo) -> List[str]:
    """
    Validate basic data quality issues:
    - No null values in required columns
    - No empty strings in text columns
    - Warn about negative values

    Args:
        data: Budget data information

    Returns:
        List of error messages (empty if all checks pass)
    """
    errors = []
    df = data.df

    required_columns = [
        "state_body",
        "program_code",
        "program_name",
        "subprogram_code",
        "subprogram_name",
    ]

    # Add financial columns based on source type
    financial_cols = get_financial_columns(data.source_type)
    for level_cols in financial_cols.values():
        required_columns.extend(level_cols)

    for column in required_columns:
        if column not in df.columns:
            errors.append(
                f"{data.year}/{data.source_type}: Missing column '{column}'"
            )
            continue

        # Check for null values
        null_count = df[column].isnull().sum()
        if null_count > 0:
            errors.append(
                f"{data.year}/{data.source_type}: {null_count} null values in '{column}'"
            )

        # Check for empty strings in text columns
        if df[column].dtype == "object":
            empty_count = (df[column].str.strip() == "").sum()
            if empty_count > 0:
                errors.append(
                    f"{data.year}/{data.source_type}: {empty_count} empty strings in '{column}'"
                )

        # Warn about negative values in financial columns
        if column in [
            col for level_cols in financial_cols.values() for col in level_cols
        ]:
            negative_count = (df[column] < 0).sum()
            if negative_count > 0:
                neg_df = df[df[column] < 0]
                # Show the 5 most negative values as examples
                top = neg_df.sort_values(by=column)[
                    [
                        "state_body",
                        "program_code",
                        "subprogram_code",
                        column,
                    ]
                ].head(5)
                lines = [
                    f"{data.year}/{data.source_type}: {int(negative_count)} negative values in '{column}'",
                    "  examples:",
                ]
                for _, r in top.iterrows():
                    lines.append(
                        "   - "
                        f"{r['state_body']} | Program {int(r['program_code'])} | Subprogram {int(r['subprogram_code'])} | "
                        f"{column}={r[column]:.6f}"
                    )
                warnings.warn("\n".join(lines))

    return errors


def compare_annual_plans_with_budget(
    spending_data: BudgetDataInfo,
    budget_data: BudgetDataInfo,
    tolerance: float = 0.01,
) -> List[str]:
    """
    Compare annual plan values in spending reports with budget law totals.

    Args:
        spending_data: Spending report data
        budget_data: Budget law data for the same year
        tolerance: Acceptable difference for comparisons

    Returns:
        List of error messages (empty if all checks pass)
    """
    errors = []

    if spending_data.year != budget_data.year:
        errors.append(
            f"Year mismatch: spending {spending_data.year} vs budget {budget_data.year}"
        )
        return errors

    # Compare at subprogram level
    spending_df = spending_data.df
    budget_df = budget_data.df

    # Merge on program and subprogram codes
    merged = spending_df.merge(
        budget_df[["program_code", "subprogram_code", "subprogram_total"]],
        on=["program_code", "subprogram_code"],
        suffixes=("_spending", "_budget"),
        how="outer",
    )

    # Check for missing subprograms
    missing_in_spending = merged[merged["subprogram_annual_plan"].isna()]
    if not missing_in_spending.empty:
        errors.append(
            f"Found {len(missing_in_spending)} subprograms in "
            "budget but not in spending report"
        )

    missing_in_budget = merged[merged["subprogram_total"].isna()]
    if not missing_in_budget.empty:
        errors.append(
            f"Found {len(missing_in_budget)} subprograms in spending report but not in budget"
        )

    # Compare values for matching subprograms
    valid_comparisons = merged[
        merged["subprogram_annual_plan"].notna()
        & merged["subprogram_total"].notna()
    ]

    mismatches = valid_comparisons[
        abs(
            valid_comparisons["subprogram_annual_plan"]
            - valid_comparisons["subprogram_total"]
        )
        > tolerance
    ]

    if not mismatches.empty:
        errors.append(
            f"Found {len(mismatches)} subprograms with mismatched annual plan vs budget totals"
        )

    return errors
