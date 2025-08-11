from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import json
import math
import pandas as pd

from .financial import (
    validate_financial_totals_consistency,
    validate_percentage_ranges,
    validate_logical_relationships_spending,
)


@dataclass
class CheckResult:
    check_id: str
    severity: str  # "error" | "warning"
    passed: bool
    fail_count: int
    messages: List[str]


@dataclass
class ValidationReport:
    results: List[CheckResult]

    def has_errors(self, strict: bool = False) -> bool:
        for r in self.results:
            if r.severity == "error" and not r.passed:
                return True
            if strict and r.severity == "warning" and not r.passed:
                return True
        return False


def _detect_is_spending(df: pd.DataFrame) -> bool:
    return any(
        c.startswith("subprogram_") and (c.endswith("annual_plan") or c.endswith("actual"))
        for c in df.columns
    )


def _check_required_columns(df: pd.DataFrame) -> CheckResult:
    required = [
        "state_body",
        "program_code",
        "program_name",
        "subprogram_code",
        "subprogram_name",
    ]
    missing = [c for c in required if c not in df.columns]
    passed = len(missing) == 0
    msgs = [f"Missing: {', '.join(missing)}"] if missing else []
    return CheckResult("required_columns_present", "error", passed, len(missing), msgs)


def _check_empty_identifiers(df: pd.DataFrame) -> CheckResult:
    id_cols = [c for c in ["state_body", "program_name", "subprogram_name"] if c in df.columns]
    if not id_cols:
        return CheckResult("empty_texts_in_identifiers", "warning", True, 0, [])
    empty_rows = pd.Series(False, index=df.index)
    for c in id_cols:
        empty_rows |= df[c].astype(str).str.strip() == ""
    count = int(empty_rows.sum())
    msgs = []
    if count:
        sample = df.loc[empty_rows, id_cols].head(5).to_dict(orient="records")
        msgs.append(f"Rows with empty identifiers: {count}; sample: {sample}")
    return CheckResult("empty_texts_in_identifiers", "warning", count == 0, count, msgs)


def _check_grand_total_consistency(df: pd.DataFrame, overall_path: Optional[Path]) -> CheckResult:
    if overall_path is None or not overall_path.exists():
        return CheckResult("grand_total_consistency", "error", True, 0, [])
    if "subprogram_total" not in df.columns:
        return CheckResult("grand_total_consistency", "error", True, 0, [])
    try:
        overall = json.loads(overall_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return CheckResult("grand_total_consistency", "error", True, 0, [])

    grand_total = overall.get("overall_total")
    if grand_total is None:
        return CheckResult("grand_total_consistency", "error", True, 0, [])

    # Sums
    state_body_sum = (
        round(df.drop_duplicates(subset="state_body")["state_body_total"].sum(), 2)
        if "state_body_total" in df.columns
        else math.nan
    )
    program_sum = (
        round(df.drop_duplicates(subset="program_code")["program_total"].sum(), 2)
        if "program_total" in df.columns
        else math.nan
    )
    subprogram_sum = round(df["subprogram_total"].sum(), 2)
    grand_total = round(grand_total, 2)

    failures = []
    if not math.isnan(state_body_sum) and state_body_sum != grand_total:
        failures.append(f"grand vs state_body ({grand_total} != {state_body_sum})")
    if not math.isnan(program_sum) and program_sum != grand_total:
        failures.append(f"grand vs program ({grand_total} != {program_sum})")
    if subprogram_sum != grand_total:
        failures.append(f"grand vs subprogram ({grand_total} != {subprogram_sum})")

    return CheckResult(
        "grand_total_consistency",
        "error",
        len(failures) == 0,
        len(failures),
        failures[:5],
    )


def _check_negative_totals(df: pd.DataFrame) -> List[CheckResult]:
    results: List[CheckResult] = []
    for col, check_id, severity in [
        ("state_body_total", "negative_state_body_totals", "error"),
        ("program_total", "negative_program_totals", "warning"),
        ("subprogram_total", "negative_subprogram_totals", "warning"),
    ]:
        if col not in df.columns:
            continue
        count = int((df[col] < 0).sum())
        msgs = []
        if count:
            msgs.append(f"{count} negative values in {col}")
        results.append(CheckResult(check_id, severity, count == 0, count, msgs))
    return results


def _check_percentage_ranges(df: pd.DataFrame) -> CheckResult:
    errors = validate_percentage_ranges(df)
    return CheckResult(
        "percentage_ranges_valid",
        "error",
        len(errors) == 0,
        len(errors),
        errors[:5],
    )


def _check_spending_logic(df: pd.DataFrame) -> List[CheckResult]:
    results: List[CheckResult] = []
    # period_plan <= annual_plan; revised_period_plan <= revised_annual_plan
    msgs = validate_logical_relationships_spending(df)
    # Split into two counts by searching substrings
    pp = [m for m in msgs if "period_plan > annual_plan" in m]
    rp = [m for m in msgs if "rev_period_plan > rev_annual_plan" in m]
    results.append(
        CheckResult("period_plan_le_annual_plan", "error", len(pp) == 0, len(pp), pp[:5])
    )
    results.append(
        CheckResult(
            "revised_period_le_revised_annual",
            "error",
            len(rp) == 0,
            len(rp),
            rp[:5],
        )
    )

    # percentage_calculation_correct: compare actual / revised_annual to reported pct
    if all(
        c in df.columns
        for c in [
            "subprogram_actual",
            "subprogram_rev_annual_plan",
            "subprogram_actual_vs_rev_annual_plan",
        ]
    ):
        den = df["subprogram_rev_annual_plan"].replace(0, pd.NA)
        expected = (df["subprogram_actual"] / den).fillna(0)
        diff = (expected - df["subprogram_actual_vs_rev_annual_plan"]).abs()
        mismatches = int((diff > 0.001).sum())
        msgs2 = []
        if mismatches:
            sample_rows = df.loc[
                (diff > 0.001),
                [
                    "program_code",
                    "subprogram_code",
                    "subprogram_actual",
                    "subprogram_rev_annual_plan",
                    "subprogram_actual_vs_rev_annual_plan",
                ],
            ].head(5)
            msgs2.append(
                f"mismatches: {mismatches}; sample: {sample_rows.to_dict(orient='records')}"
            )
        results.append(
            CheckResult(
                "percentage_calculation_correct",
                "error",
                mismatches == 0,
                mismatches,
                msgs2,
            )
        )

    # presence checks
    for col, cid in [
        ("subprogram_rev_annual_plan", "revised_annual_presence"),
        ("subprogram_annual_plan", "annual_presence"),
    ]:
        if col in df.columns:
            nulls = int(df[col].isnull().sum())
            results.append(
                CheckResult(
                    cid,
                    "error",
                    nulls == 0,
                    nulls,
                    [f"nulls in {col}: {nulls}"] if nulls else [],
                )
            )
    # no negative percentages
    pct_cols = [
        c
        for c in df.columns
        if c.endswith("_actual_vs_rev_annual_plan") or c.endswith("_actual_vs_rev_period_plan")
    ]
    negatives = 0
    for c in pct_cols:
        negatives += int((df[c] < 0).sum())
    results.append(
        CheckResult(
            "no_negative_percentages",
            "error",
            negatives == 0,
            negatives,
            [f"negative percentage values: {negatives}"] if negatives else [],
        )
    )
    return results


def _check_hierarchical_totals(df: pd.DataFrame) -> CheckResult:
    errors = validate_financial_totals_consistency(df)
    return CheckResult(
        "hierarchical_totals_consistency",
        "error",
        len(errors) == 0,
        len(errors),
        errors[:5],
    )


def run_all_checks(df: pd.DataFrame, csv_path: Path) -> ValidationReport:
    results: List[CheckResult] = []

    # Structural
    results.append(_check_required_columns(df))
    results.append(_check_empty_identifiers(df))

    is_spending = _detect_is_spending(df)

    # Financial consistency
    results.append(_check_hierarchical_totals(df))

    # grand total (budget laws only, if overall file exists)
    overall_path = None
    stem = csv_path.stem  # e.g., 2019_BUDGET_LAW
    overall_path = csv_path.parent / f"{stem}_overall.json"
    results.append(_check_grand_total_consistency(df, overall_path))

    # Negative totals
    results.extend(_check_negative_totals(df))

    # Spending checks
    if is_spending:
        results.append(_check_percentage_ranges(df))
        results.extend(_check_spending_logic(df))

    return ValidationReport(results=results)


def print_report(report: ValidationReport, strict: bool = False, max_examples: int = 5) -> None:
    for r in report.results:
        if r.severity == "warning" and strict:
            sev = "ERROR"  # warnings treated as errors under --strict
        else:
            sev = r.severity.upper()
        status = "PASS" if r.passed else ("FAIL" if sev == "ERROR" else "WARN")
        print(f"- {r.check_id} — {status}" + (f" ({r.fail_count})" if not r.passed else ""))
        if not r.passed and r.messages:
            for m in r.messages[:max_examples]:
                print(f"  {m}")
