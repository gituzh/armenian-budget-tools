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
from conftest import load_budget_data, get_all_available_data

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

# Tolerances for spending tests
# Absolute tolerance is in AMD
SPENDING_ABS_TOL: float = 5.0
# Fractional tolerance is for percentage/ratio checks
SPENDING_FRAC_TOL: float = 1e-3


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
    if "subprogram_actual" in df.columns and "subprogram_rev_annual_plan" in df.columns:
        if "subprogram_actual_vs_rev_annual_plan" in df.columns:
            # Calculate expected percentages
            expected_pct = df["subprogram_actual"] / df["subprogram_rev_annual_plan"]
            expected_pct = expected_pct.fillna(0)  # Handle NaNs (not inf)

            # Compare with actual percentages (with tolerance for floating point)
            actual_pct = df["subprogram_actual_vs_rev_annual_plan"]
            differences = abs(expected_pct - actual_pct)
            tolerance = SPENDING_FRAC_TOL  # 0.1% tolerance

            significant_diffs = differences > tolerance
            if significant_diffs.any():
                count = int(significant_diffs.sum())
                max_show = 50
                rows = df.index[significant_diffs].tolist()
                rows_shown = ", ".join([str(r) for r in rows[:max_show]])
                rows_suffix = (
                    f", +{len(rows) - max_show} more" if len(rows) > max_show else ""
                )
                codes_part = ""
                if "program_code" in df.columns and "subprogram_code" in df.columns:
                    pairs = list(
                        zip(
                            df.loc[significant_diffs, "program_code"].astype(str).tolist(),
                            df.loc[significant_diffs, "subprogram_code"].astype(str).tolist(),
                        )
                    )
                    codes_shown = ", ".join([f"({p},{s})" for p, s in pairs[:max_show]])
                    codes_suffix = (
                        f", +{len(pairs) - max_show} more" if len(pairs) > max_show else ""
                    )
                    codes_part = f"; codes=[{codes_shown}]{codes_suffix}"
                pytest.fail(
                    f"{spending_data.year}/{spending_data.source_type}: subprogram_actual_vs_rev_annual_plan calc mismatch; count={count}; rows=[{rows_shown}]{rows_suffix}{codes_part}"
                )


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
            negative_mask = df[col] < 0
            negative_count = int(negative_mask.sum())
            if negative_count > 0:
                max_show = 50
                rows = df.index[negative_mask].tolist()
                rows_shown = ", ".join([str(r) for r in rows[:max_show]])
                rows_suffix = (
                    f", +{len(rows) - max_show} more" if len(rows) > max_show else ""
                )
                codes_part = ""
                if "program_code" in df.columns and "subprogram_code" in df.columns:
                    pairs = list(
                        zip(
                            df.loc[negative_mask, "program_code"].astype(str).tolist(),
                            df.loc[negative_mask, "subprogram_code"].astype(str).tolist(),
                        )
                    )
                    codes_shown = ", ".join([f"({p},{s})" for p, s in pairs[:max_show]])
                    codes_suffix = (
                        f", +{len(pairs) - max_show} more" if len(pairs) > max_show else ""
                    )
                    codes_part = f"; codes=[{codes_shown}]{codes_suffix}"
                pytest.fail(
                    f"{spending_data.year}/{spending_data.source_type}: {col} has {negative_count} negatives; rows=[{rows_shown}]{rows_suffix}{codes_part}"
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
    if "subprogram_actual" in df.columns and "subprogram_rev_annual_plan" in df.columns:
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

        if "subprogram_actual" in df.columns and "subprogram_period_plan" in df.columns:
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


# Precompute spending parameter sets and stable IDs
_SPENDING_PARAMS = [
    (y, t) for (y, t) in get_all_available_data() if str(t).startswith("SPENDING_")
]
_SPENDING_IDS = [f"{y}_{t}" for (y, t) in _SPENDING_PARAMS]


@pytest.mark.parametrize("year, source_type", _SPENDING_PARAMS, ids=_SPENDING_IDS)
def test_spending_csv_non_empty(year: int, source_type: str) -> None:
    data = load_budget_data(year, source_type)
    assert len(data.df) > 0, f"{year}/{source_type}: CSV is empty ({data.file_path})"


@pytest.mark.parametrize("year, source_type", _SPENDING_PARAMS, ids=_SPENDING_IDS)
def test_spending_overall_matches_csv(year: int, source_type: str) -> None:
    data = load_budget_data(year, source_type)
    df = data.df
    overall = data.overall_values

    def sum_sub(col: str) -> float:
        return float(df[col].sum()) if col in df.columns else 0.0

    # Annual and revised annual totals
    if "overall_annual_plan" in overall:
        _ov = round(float(overall["overall_annual_plan"]), 2)
        _sum = round(sum_sub("subprogram_annual_plan"), 2)
        _diff = round(_ov - _sum, 2)
        if abs(_ov - _sum) > SPENDING_ABS_TOL:
            lines = [
                f"{year}/{source_type}: overall_annual_plan mismatch: overall={_ov}, sum={_sum}, diff={_diff}, tol={SPENDING_ABS_TOL}",
            ]
            col = "subprogram_annual_plan"
            if col in df.columns:
                nulls = int(df[col].isnull().sum())
                non_numeric = int(
                    (~pd.to_numeric(df[col], errors="coerce").notnull()).sum()
                )
                lines.append(f"  {col}: nulls={nulls}, non_numeric={non_numeric}")
                show_cols = [
                    "state_body",
                    "program_code",
                    "program_name",
                    "subprogram_code",
                    "subprogram_name",
                    col,
                ]
                show_cols = [c for c in show_cols if c in df.columns]
                sample = df[show_cols].sort_values(col, ascending=False).head(20)
                lines.append("  Top rows contributing to sum:")
                lines.append(sample.to_string(index=False))
            pytest.fail("\n".join(lines))
    if "overall_rev_annual_plan" in overall:
        _ov = round(float(overall["overall_rev_annual_plan"]), 2)
        _sum = round(sum_sub("subprogram_rev_annual_plan"), 2)
        _diff = round(_ov - _sum, 2)
        if abs(_ov - _sum) > SPENDING_ABS_TOL:
            lines = [
                f"{year}/{source_type}: overall_rev_annual_plan mismatch: overall={_ov}, sum={_sum}, diff={_diff}, tol={SPENDING_ABS_TOL}",
            ]
            col = "subprogram_rev_annual_plan"
            if col in df.columns:
                nulls = int(df[col].isnull().sum())
                non_numeric = int(
                    (~pd.to_numeric(df[col], errors="coerce").notnull()).sum()
                )
                lines.append(f"  {col}: nulls={nulls}, non_numeric={non_numeric}")
                show_cols = [
                    "state_body",
                    "program_code",
                    "program_name",
                    "subprogram_code",
                    "subprogram_name",
                    col,
                ]
                show_cols = [c for c in show_cols if c in df.columns]
                sample = df[show_cols].sort_values(col, ascending=False).head(20)
                lines.append("  Top rows contributing to sum:")
                lines.append(sample.to_string(index=False))
            pytest.fail("\n".join(lines))
    # Period totals for quarterly reports
    if source_type in ("SPENDING_Q1", "SPENDING_Q12", "SPENDING_Q123"):
        if "overall_period_plan" in overall:
            _ov = round(float(overall["overall_period_plan"]), 2)
            _sum = round(sum_sub("subprogram_period_plan"), 2)
            _diff = round(_ov - _sum, 2)
            if abs(_ov - _sum) > SPENDING_ABS_TOL:
                lines = [
                    f"{year}/{source_type}: overall_period_plan mismatch: overall={_ov}, sum={_sum}, diff={_diff}, tol={SPENDING_ABS_TOL}",
                ]
                col = "subprogram_period_plan"
                if col in df.columns:
                    nulls = int(df[col].isnull().sum())
                    non_numeric = int(
                        (~pd.to_numeric(df[col], errors="coerce").notnull()).sum()
                    )
                    lines.append(f"  {col}: nulls={nulls}, non_numeric={non_numeric}")
                    show_cols = [
                        "state_body",
                        "program_code",
                        "program_name",
                        "subprogram_code",
                        "subprogram_name",
                        col,
                    ]
                    show_cols = [c for c in show_cols if c in df.columns]
                    sample = df[show_cols].sort_values(col, ascending=False).head(20)
                    lines.append("  Top rows contributing to sum:")
                    lines.append(sample.to_string(index=False))
                pytest.fail("\n".join(lines))
        if "overall_rev_period_plan" in overall:
            _ov = round(float(overall["overall_rev_period_plan"]), 2)
            _sum = round(sum_sub("subprogram_rev_period_plan"), 2)
            _diff = round(_ov - _sum, 2)
            if abs(_ov - _sum) > SPENDING_ABS_TOL:
                lines = [
                    f"{year}/{source_type}: overall_rev_period_plan mismatch: overall={_ov}, sum={_sum}, diff={_diff}, tol={SPENDING_ABS_TOL}",
                ]
                col = "subprogram_rev_period_plan"
                if col in df.columns:
                    nulls = int(df[col].isnull().sum())
                    non_numeric = int(
                        (~pd.to_numeric(df[col], errors="coerce").notnull()).sum()
                    )
                    lines.append(f"  {col}: nulls={nulls}, non_numeric={non_numeric}")
                    show_cols = [
                        "state_body",
                        "program_code",
                        "program_name",
                        "subprogram_code",
                        "subprogram_name",
                        col,
                    ]
                    show_cols = [c for c in show_cols if c in df.columns]
                    sample = df[show_cols].sort_values(col, ascending=False).head(20)
                    lines.append("  Top rows contributing to sum:")
                    lines.append(sample.to_string(index=False))
                pytest.fail("\n".join(lines))
    # Actual totals
    if "overall_actual" in overall:
        _ov = round(float(overall["overall_actual"]), 2)
        _sum = round(sum_sub("subprogram_actual"), 2)
        _diff = round(_ov - _sum, 2)
        if abs(_ov - _sum) > SPENDING_ABS_TOL:
            lines = [
                f"{year}/{source_type}: overall_actual mismatch: overall={_ov}, sum={_sum}, diff={_diff}, tol={SPENDING_ABS_TOL}",
            ]
            col = "subprogram_actual"
            if col in df.columns:
                nulls = int(df[col].isnull().sum())
                non_numeric = int(
                    (~pd.to_numeric(df[col], errors="coerce").notnull()).sum()
                )
                lines.append(f"  {col}: nulls={nulls}, non_numeric={non_numeric}")
                show_cols = [
                    "state_body",
                    "program_code",
                    "program_name",
                    "subprogram_code",
                    "subprogram_name",
                    col,
                ]
                show_cols = [c for c in show_cols if c in df.columns]
                sample = df[show_cols].sort_values(col, ascending=False).head(20)
                lines.append("  Top rows contributing to sum:")
                lines.append(sample.to_string(index=False))
            pytest.fail("\n".join(lines))
    # Ratios (check math, allow tiny float error)
    if overall.get("overall_rev_annual_plan"):
        exp = float(overall.get("overall_actual", 0.0)) / float(
            overall["overall_rev_annual_plan"]
        )
        if "overall_actual_vs_rev_annual_plan" in overall:
            assert (
                abs(float(overall["overall_actual_vs_rev_annual_plan"]) - exp)
                <= SPENDING_FRAC_TOL
            )
    if source_type in ("SPENDING_Q1", "SPENDING_Q12", "SPENDING_Q123") and overall.get(
        "overall_rev_period_plan"
    ):
        exp = float(overall.get("overall_actual", 0.0)) / float(
            overall["overall_rev_period_plan"]
        )
        if "overall_actual_vs_rev_period_plan" in overall:
            assert (
                abs(float(overall["overall_actual_vs_rev_period_plan"]) - exp)
                <= SPENDING_FRAC_TOL
            )
