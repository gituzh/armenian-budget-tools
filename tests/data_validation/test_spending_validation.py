"""Tests specifically for spending report data validation."""

import pytest
import sys
from pathlib import Path
import pandas as pd

# Add parent directory to path for imports
test_dir = Path(__file__).parent.parent
if str(test_dir) not in sys.path:
    sys.path.insert(0, str(test_dir))

from conftest import (
    spending_data,
    get_percentage_columns,
    get_financial_columns,
)

# Import validation helpers with fallback
try:
    from utils.validation_helpers import (
        validate_financial_totals_consistency,
        validate_data_quality_basic,
        validate_percentage_ranges,
        validate_logical_relationships_spending,
    )
except ImportError:
    sys.path.insert(0, str(test_dir / "utils"))
    from validation_helpers import (
        validate_financial_totals_consistency,
        validate_data_quality_basic,
        validate_percentage_ranges,
        validate_logical_relationships_spending,
    )


def test_spending_financial_consistency(spending_data):
    """Test that spending report financial totals are consistent across all levels."""
    errors = validate_financial_totals_consistency(spending_data)

    if errors:
        pytest.fail("\n".join(errors))


def test_spending_data_quality(spending_data):
    """Test basic data quality for spending report files."""
    errors = validate_data_quality_basic(spending_data)

    if errors:
        pytest.fail("\n".join(errors))


def test_spending_percentage_ranges(spending_data):
    """Test that percentage columns contain valid values (0-1 range)."""
    errors = validate_percentage_ranges(spending_data)

    if errors:
        pytest.fail("\n".join(errors))


def test_spending_logical_relationships(spending_data):
    """Test logical relationships in spending data (period <= annual, etc.)."""
    errors = validate_logical_relationships_spending(spending_data)

    if errors:
        pytest.fail("\n".join(errors))


def test_spending_has_all_required_columns(spending_data):
    """Test that spending reports have all required financial columns."""
    df = spending_data.df
    financial_cols = get_financial_columns(spending_data.source_type)
    percentage_cols = get_percentage_columns(spending_data.source_type)

    # Check financial columns
    for level, cols in financial_cols.items():
        for col in cols:
            assert col in df.columns, (
                f"{spending_data.year}/{spending_data.source_type}: "
                f"Missing required {level} financial column: {col}"
            )

    # Check percentage columns
    for level, cols in percentage_cols.items():
        for col in cols:
            assert col in df.columns, (
                f"{spending_data.year}/{spending_data.source_type}: "
                f"Missing required {level} percentage column: {col}"
            )


def test_spending_percentage_calculations(spending_data):
    """Test that percentage calculations are mathematically correct."""
    df = spending_data.df

    # Test actual_vs_rev_annual_plan = actual / rev_annual_plan
    if (
        "subprogram_actual" in df.columns
        and "subprogram_rev_annual_plan" in df.columns
    ):
        if "subprogram_actual_vs_rev_annual_plan" in df.columns:
            # Calculate expected percentages
            expected_pct = (
                df["subprogram_actual"] / df["subprogram_rev_annual_plan"]
            )
            expected_pct = expected_pct.fillna(0)  # Handle NaNs (not inf)

            # Compare with actual percentages (with tolerance for floating point)
            actual_pct = df["subprogram_actual_vs_rev_annual_plan"]
            differences = abs(expected_pct - actual_pct)
            tolerance = 0.001  # 0.1% tolerance

            significant_diffs = differences > tolerance
            if significant_diffs.any():
                problem_rows = df[significant_diffs].copy()
                problem_rows = problem_rows.assign(
                    expected_pct=expected_pct[significant_diffs],
                    abs_diff=differences[significant_diffs],
                )

                # Build an informative message with key identifiers and numbers
                lines = [
                    f"{spending_data.year}/{spending_data.source_type}: "
                    f"Found {len(problem_rows)} rows with incorrect percentage calculations "
                    f"for actual_vs_rev_annual_plan (tolerance={tolerance}).",
                ]

                max_show = 20
                for _, row in problem_rows.head(max_show).iterrows():
                    sb = row.get("state_body", "<state_body>")
                    pc = row.get("program_code", "<program_code>")
                    pn = row.get("program_name", "")
                    spc = row.get("subprogram_code", "<subprogram_code>")
                    spn = row.get("subprogram_name", "")
                    actual = row.get("subprogram_actual")
                    rev_ann = row.get("subprogram_rev_annual_plan")
                    stored = row.get("subprogram_actual_vs_rev_annual_plan")
                    expected = row.get("expected_pct")
                    diff = row.get("abs_diff")

                    # Reason hints (division by zero, infinities, etc.)
                    if pd.isna(rev_ann) or rev_ann == 0:
                        reason = "division by zero (rev_annual_plan=0)"
                    elif (
                        pd.isna(actual) or pd.isna(stored) or pd.isna(expected)
                    ):
                        reason = "missing value(s)"
                    elif not isinstance(stored, (int, float)) or not isinstance(
                        expected, (int, float)
                    ):
                        reason = "non-numeric percent value"
                    else:
                        reason = "mismatch beyond tolerance"

                    lines.append(
                        " - "
                        f"{sb} | Program {pc} {pn} | Subprogram {spc} {spn}\n"
                        f"   actual={actual:.6f}, rev_annual={rev_ann:.6f}, "
                        f"stored_pct={stored:.6f}, expected_pct={expected:.6f}, "
                        f"abs_diff={diff:.6f} | {reason}"
                    )

                remaining = len(problem_rows) - min(len(problem_rows), max_show)
                if remaining > 0:
                    lines.append(f" ... and {remaining} more rows")

                pytest.fail("\n".join(lines))


def test_spending_no_negative_percentages(spending_data):
    """Test that percentage columns don't have negative values."""
    df = spending_data.df
    percentage_cols = get_percentage_columns(spending_data.source_type)

    # Flatten all percentage columns
    all_pct_cols = []
    for level_cols in percentage_cols.values():
        all_pct_cols.extend(level_cols)

    for col in all_pct_cols:
        if col in df.columns:
            negative_count = (df[col] < 0).sum()
            assert negative_count == 0, (
                f"{spending_data.year}/{spending_data.source_type}: "
                f"Found {negative_count} negative values in percentage column {col}"
            )


def test_spending_revised_vs_original_plans(spending_data):
    """Test relationships between revised and original plans."""
    df = spending_data.df

    # Check that revised plans exist for all levels
    levels = ["state_body", "program", "subprogram"]

    for level in levels:
        annual_col = f"{level}_annual_plan"
        rev_annual_col = f"{level}_rev_annual_plan"

        if annual_col in df.columns and rev_annual_col in df.columns:
            # Both should exist and have values
            null_annual = df[annual_col].isnull().sum()
            null_rev_annual = df[rev_annual_col].isnull().sum()

            assert null_annual == 0, (
                f"{spending_data.year}/{spending_data.source_type}: "
                f"Found {null_annual} null values in {annual_col}"
            )

            assert null_rev_annual == 0, (
                f"{spending_data.year}/{spending_data.source_type}: "
                f"Found {null_rev_annual} null values in {rev_annual_col}"
            )


def test_spending_actual_vs_plans_reasonableness(spending_data):
    """Test that actual spending values are reasonable compared to plans."""
    df = spending_data.df

    # Test that actual values don't exceed revised annual plans by more than 10%
    if (
        "subprogram_actual" in df.columns
        and "subprogram_rev_annual_plan" in df.columns
    ):
        # Filter out zero revised annual plans to avoid division issues
        valid_data = df[df["subprogram_rev_annual_plan"] > 0]

        if not valid_data.empty:
            ratio = (
                valid_data["subprogram_actual"]
                / valid_data["subprogram_rev_annual_plan"]
            )
            excessive_spending = ratio > 1.1  # More than 110% of revised plan

            if excessive_spending.any():
                problem_count = int(excessive_spending.sum())
                # Build informative warning with examples
                examples = (
                    valid_data.loc[excessive_spending]
                    .assign(ratio=ratio[excessive_spending])
                    .sort_values("ratio", ascending=False)
                    .head(5)
                )
                lines = [
                    f"{spending_data.year}/{spending_data.source_type}: Found {problem_count} subprograms with actual spending >110% of revised annual plan",
                    f"  max_ratio={ratio[excessive_spending].max():.6f}",
                    "  examples:",
                ]
                for _, r in examples.iterrows():
                    lines.append(
                        "   - "
                        f"{r.get('state_body', '')} | Program {r.get('program_code', '')} {r.get('program_name', '')} | "
                        f"Subprogram {r.get('subprogram_code', '')} {r.get('subprogram_name', '')} | "
                        f"actual={r['subprogram_actual']:.6f}, rev_annual={r['subprogram_rev_annual_plan']:.6f}, ratio={r['ratio']:.6f}"
                    )
                # This is a warning, not a failure, as overspending can be legitimate
                import warnings

                warnings.warn("\n".join(lines))


def test_spending_quarterly_progression(spending_data):
    """Test that quarterly spending shows logical progression."""
    source_type = spending_data.source_type

    # Only test for quarterly reports, not full year
    if source_type in ["SPENDING_Q1", "SPENDING_Q12", "SPENDING_Q123"]:
        df = spending_data.df

        if (
            "subprogram_actual" in df.columns
            and "subprogram_period_plan" in df.columns
        ):
            # Period actuals should generally not exceed period plans dramatically
            valid_data = df[df["subprogram_period_plan"] > 0]

            if not valid_data.empty:
                ratio = (
                    valid_data["subprogram_actual"]
                    / valid_data["subprogram_period_plan"]
                )
                mask = ratio > 2.0  # More than 200% of period plan
                excessive_count = int(mask.sum())

                if excessive_count > 0:
                    top = (
                        valid_data.loc[mask]
                        .assign(ratio=ratio[mask])
                        .sort_values("ratio", ascending=False)
                        .head(5)
                    )
                    lines = [
                        f"{spending_data.year}/{spending_data.source_type}: Found {excessive_count} subprograms with actual spending >200% of period plan (may indicate data issues)",
                        f"  max_ratio={ratio[mask].max():.6f}",
                        "  examples:",
                    ]
                    for _, r in top.iterrows():
                        lines.append(
                            "   - "
                            f"{r.get('state_body', '')} | Program {r.get('program_code', '')} {r.get('program_name', '')} | "
                            f"Subprogram {r.get('subprogram_code', '')} {r.get('subprogram_name', '')} | "
                            f"actual={r['subprogram_actual']:.6f}, period_plan={r['subprogram_period_plan']:.6f}, ratio={r['ratio']:.6f}"
                        )
                    import warnings

                    warnings.warn("\n".join(lines))
