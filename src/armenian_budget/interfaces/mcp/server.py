"""
Minimal MCP server exposing data access tools for processed datasets.

Implements tools documented in docs/architecture.md:
 - list_available_data
 - get_data_schema
 - filter_budget_data
 - get_ministry_spending_summary
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from typing import Union
from difflib import SequenceMatcher
import importlib
import re
from uuid import uuid4
import json
import sys
import yaml
import pandas as pd

try:
    from mcp.server.fastmcp import FastMCP
except Exception as exc:
    raise RuntimeError(
        "The 'mcp' package is required for the MCP server. Install with: pip install mcp"
    ) from exc


# Global configuration
_DATA_ROOT: Path | None = None
_SERVER = FastMCP("armenian-budget-tools")

# Configure logging for MCP server
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stderr)  # MCP uses stdout for protocol
    ],
)
logger = logging.getLogger(__name__)


def _processed_data_dir() -> Path:
    """Get the processed data directory, with validation."""
    if _DATA_ROOT is None:
        base = Path("data/processed")
    else:
        base = _DATA_ROOT

    if not base.exists():
        logger.warning("Processed data directory does not exist: %s", base)
        base.mkdir(parents=True, exist_ok=True)

    return base


def _validate_data_availability() -> Dict[str, Any]:
    """Check what data is actually available and return diagnostics."""
    data_dir = _processed_data_dir()
    csv_files = list(data_dir.glob("*.csv")) if data_dir.exists() else []

    return {
        "data_dir": str(data_dir),
        "data_dir_exists": data_dir.exists(),
        "csv_count": len(csv_files),
        "sample_files": [f.name for f in csv_files[:5]],
        "data_root": str(_DATA_ROOT) if _DATA_ROOT else "default (./data/processed)",
    }


def _extract_year_and_type(filename: str) -> Tuple[Optional[int], Optional[str]]:
    """Extract year and source type from CSV filename."""
    name = Path(filename).name
    if not name.endswith(".csv"):
        return None, None
    stem = name[:-4]
    if "_" not in stem:
        return None, None
    try:
        year_part, type_part = stem.split("_", 1)
        year = int(year_part)
        return year, type_part
    except ValueError:
        return None, None


def _get_measure_columns(source_type: str) -> Dict[str, str]:
    """Return role->column mapping for financial measures."""
    st = str(source_type).strip().upper()
    if st == "BUDGET_LAW":
        return {"allocated": "subprogram_total"}
    elif st in {"SPENDING_Q1", "SPENDING_Q12", "SPENDING_Q123"}:
        return {
            "allocated": "subprogram_annual_plan",
            "revised": "subprogram_rev_annual_plan",
            "actual": "subprogram_actual",
            "execution_rate": "subprogram_actual_vs_rev_annual_plan",
        }
    elif st == "SPENDING_Q1234":
        return {
            "allocated": "subprogram_annual_plan",
            "revised": "subprogram_rev_annual_plan",
            "actual": "subprogram_actual",
        }
    return {}


def _resolve_csv_path(year: int, source_type: str) -> Path:
    """Resolve CSV path for a given year and source type or raise if missing."""
    data_dir = _processed_data_dir()
    filename = f"{int(year)}_{str(source_type).upper()}.csv"
    csv_path = data_dir / filename
    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset not found: {filename}")
    return csv_path


def _present_path(path: Union[str, Path]) -> str:
    """Return a string path for tool outputs."""
    return str(Path(path))


_rapidfuzz_fuzz = None


def _get_rapidfuzz_fuzz():
    """Lazily import rapidfuzz.fuzz to avoid hard dependency at import time."""
    global _rapidfuzz_fuzz
    if _rapidfuzz_fuzz is not None:
        return _rapidfuzz_fuzz
    try:
        module_name = "rapidfuzz" + ".fuzz"
        _module = importlib.import_module(module_name)
        _rapidfuzz_fuzz = _module  # type: ignore
    except Exception:  # pragma: no cover - optional dependency fallback
        _rapidfuzz_fuzz = None
    return _rapidfuzz_fuzz


# -------------------------
# MARK: Resources and Direct Data
# -------------------------


def _compute_state_body_summary_df(year: int) -> pd.DataFrame:
    """Compute state body totals with de-duplication.

    Reads only required columns, coerces numeric totals, and collapses
    repeated rows by taking the maximum per state body to avoid duplicates.
    """
    csv_path = _resolve_csv_path(year, "BUDGET_LAW")
    df = pd.read_csv(csv_path, usecols=["state_body", "state_body_total"])  # type: ignore[arg-type]
    df["state_body_total"] = pd.to_numeric(df["state_body_total"], errors="coerce").fillna(0)
    summary = (
        df.groupby("state_body", as_index=False)["state_body_total"]
        .max()
        .sort_values(["state_body"])  # stable ordering for usability
    )
    return summary


def _compute_program_summary_df(year: int) -> pd.DataFrame:
    """Compute program totals per program within each state body.

    Uses the maximum of program_total per (state_body, program_code, program_name)
    to avoid double counting when the same program rows repeat per subprogram.
    """
    csv_path = _resolve_csv_path(year, "BUDGET_LAW")
    cols = ["state_body", "program_code", "program_name", "program_total"]
    df = pd.read_csv(csv_path, usecols=cols)  # type: ignore[arg-type]
    df["program_total"] = pd.to_numeric(df["program_total"], errors="coerce").fillna(0)
    summary = (
        df.groupby(["state_body", "program_code", "program_name"], as_index=False)["program_total"]
        .max()
        .sort_values(["state_body", "program_code"])  # consistent ordering
    )
    return summary


def generate_state_body_summary_csv(year: int) -> str:
    """Return CSV text for state body totals for a given year."""
    summary = _compute_state_body_summary_df(year)
    return summary.to_csv(index=False)


def generate_program_summary_csv(year: int) -> str:
    """Return CSV text for program totals per state body for a given year."""
    summary = _compute_program_summary_df(year)
    return summary.to_csv(index=False)


# -------------------------
# MARK: Data Tools
# -------------------------


@_SERVER.tool(
    "preview_dataset",
    title="Preview dataset",
    description=(
        "Return sample rows, inferred schema, and basic stats for the requested dataset. "
        "Parameters: year (int), source_type (e.g. BUDGET_LAW, SPENDING_Q1), sample_size (int)."
    ),
)
async def preview_dataset(
    year: int,
    source_type: str,
    sample_size: int = 10,
) -> Dict[str, Any]:
    """Return sample data and schema for quick preview."""
    try:
        csv_path = _resolve_csv_path(year, source_type)
        df = pd.read_csv(csv_path)
        sample = df.head(int(sample_size))
        memory_mb = float(sample.memory_usage(deep=True).sum()) / float(1024**2)
        return {
            "sample_data": sample.to_dict(orient="records"),
            "schema": {col: str(dtype) for col, dtype in sample.dtypes.items()},
            "total_rows": int(len(df)),
            "unique_state_bodies": int(df["state_body"].nunique())
            if "state_body" in df.columns
            else 0,
            "date_range": str(year),
            "memory_usage_mb": memory_mb,
        }
    except FileNotFoundError as e:
        return {"error": str(e), "year": int(year), "source_type": str(source_type)}
    except Exception as e:  # pragma: no cover - defensive
        logger.error("Error in preview_dataset: %s", e)
        return {"error": str(e)}


def _apply_filters(df: pd.DataFrame, source_type: str, filters: Dict[str, Any]) -> pd.DataFrame:
    """Vectorized filtering for common fields.

    Supported filters:
      - state_body: substring (case-insensitive)
      - program_codes: list of ints
      - min_amount: numeric threshold applied to an available amount column
    """
    if not filters:
        return df

    mask = pd.Series(True, index=df.index)

    state_body_val = filters.get("state_body")
    if state_body_val:
        if "state_body" in df.columns:
            mask &= (
                df["state_body"].astype(str).str.contains(str(state_body_val), case=False, na=False)
            )

    program_codes = filters.get("program_codes")
    if program_codes and "program_code" in df.columns:
        mask &= df["program_code"].isin(program_codes)

    min_amount = filters.get("min_amount")
    if min_amount is not None:
        measures = _get_measure_columns(source_type)
        amount_col = measures.get("allocated") or measures.get("actual") or measures.get("revised")
        if amount_col and amount_col in df.columns:
            mask &= pd.to_numeric(df[amount_col], errors="coerce").fillna(0) >= float(min_amount)

    return df.loc[mask]


@_SERVER.tool(
    "stream_budget_data",
    title="Stream dataset rows",
    description=(
        "Stream rows in chunks with optional filters. "
        "Parameters: year (int), chunk_size (int), offset (int), filters (dict)."
    ),
)
async def stream_budget_data(
    year: int,
    chunk_size: int = 1000,
    offset: int = 0,
    filters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Stream large datasets in manageable chunks with optional filters."""
    try:
        source_type = "BUDGET_LAW"
        csv_path = _resolve_csv_path(year, source_type)

        # Determine total rows quickly
        with open(csv_path, "r", encoding="utf-8") as f:
            total_rows = max(0, sum(1 for _ in f) - 1)

        # If no filters, use skiprows/nrows for efficiency
        if not filters:
            df = pd.read_csv(
                csv_path,
                skiprows=range(1, 1 + int(offset)) if int(offset) > 0 else None,
                nrows=int(chunk_size),
            )
            payload = df.to_dict(orient="records")
            has_more = int(offset) + int(chunk_size) < total_rows
            return {
                "data": payload,
                "chunk_info": {
                    "offset": int(offset),
                    "size": int(len(df)),
                    "total_rows": int(total_rows),
                    "has_more": bool(has_more),
                },
            }

        # With filters: stream through chunks and collect after offset
        collected: List[Dict[str, Any]] = []
        passed = 0
        for chunk in pd.read_csv(csv_path, chunksize=min(10000, max(1000, int(chunk_size) * 2))):
            filtered = _apply_filters(chunk, source_type, filters or {})
            if filtered.empty:
                continue
            if passed + len(filtered) <= int(offset):
                passed += len(filtered)
                continue
            start = max(0, int(offset) - passed)
            rows = filtered.iloc[start : start + (int(chunk_size) - len(collected))]
            collected.extend(rows.to_dict(orient="records"))
            passed += len(filtered)
            if len(collected) >= int(chunk_size):
                break

        has_more = len(collected) >= int(chunk_size)
        return {
            "data": collected,
            "chunk_info": {
                "offset": int(offset),
                "size": int(len(collected)),
                "total_rows": int(total_rows),  # unfiltered total
                "has_more": bool(has_more),
            },
        }
    except FileNotFoundError as e:
        return {"error": str(e), "year": int(year)}
    except Exception as e:  # pragma: no cover - defensive
        logger.error("Error in stream_budget_data: %s", e)
        return {"error": str(e)}


@_SERVER.resource(
    "budget://{year}/state-bodies-summary",
    name="Budget by State Body",
    title="State bodies summary",
    description="CSV with 'state_body' and deduplicated 'state_body_total' for the given year",
    mime_type="text/csv",
)
async def resource_state_bodies_summary(year: int) -> str:
    """Expose per-ministry/state-body totals as CSV content."""
    return generate_state_body_summary_csv(year)


@_SERVER.resource(
    "budget://{year}/programs-summary",
    name="Budget by Program",
    title="Program totals per state body",
    description=(
        "CSV with 'state_body','program_code','program_name','program_total' (deduped per group)"
    ),
    mime_type="text/csv",
)
async def resource_programs_summary(year: int) -> str:
    """Expose per-program totals (with state body) as CSV content."""
    return generate_program_summary_csv(year)


@_SERVER.resource(
    "budget://{year}/full-data",
    name="Full Budget Data",
    title="Full BUDGET_LAW CSV",
    description="Full BUDGET_LAW dataset for the given year as CSV text",
    mime_type="text/csv",
)
async def resource_full_data(year: int) -> str:
    """Expose full BUDGET_LAW dataset as CSV content for the given year."""
    csv_path = _resolve_csv_path(year, "BUDGET_LAW")
    return Path(csv_path).read_text(encoding="utf-8")


@_SERVER.tool(
    "get_budget_visualization_data",
    title="Visualization-ready data",
    description=(
        "Return JSON or CSV for 'state-bodies' or 'programs' summaries. "
        "Parameters: year (int), view_type (str), output_format ('json'|'csv')."
    ),
)
async def get_budget_visualization_data(
    year: int,
    view_type: str,  # "state-bodies", "programs"
    output_format: str = "json",  # "json", "csv"
) -> Dict[str, Any]:
    """Return visualization-ready data directly.

    - view_type == "state-bodies": returns state body totals
    - view_type == "programs": returns per-program totals with state body
    """
    try:
        vt = (view_type or "").strip().lower()

        if vt == "state-bodies":
            summary = _compute_state_body_summary_df(year)
            if output_format == "csv":
                return {
                    "csv_content": summary.to_csv(index=False),
                    "row_count": int(len(summary)),
                    "year": int(year),
                }
            else:
                total_budget = (
                    float(summary["state_body_total"].sum()) if not summary.empty else 0.0
                )
                return {
                    "data": summary.to_dict(orient="records"),
                    "total_budget": total_budget,
                    "currency": "AMD",
                    "year": int(year),
                }

        if vt == "programs":
            summary = _compute_program_summary_df(year)
            if output_format == "csv":
                return {
                    "csv_content": summary.to_csv(index=False),
                    "row_count": int(len(summary)),
                    "year": int(year),
                }
            else:
                return {
                    "data": summary.to_dict(orient="records"),
                    "year": int(year),
                }

        return {"error": f"Unsupported view_type: {view_type}"}

    except FileNotFoundError as e:
        return {"error": str(e), "year": int(year)}
    except Exception as e:  # pragma: no cover - defensive
        logger.error("Error in get_budget_visualization_data: %s", e)
        return {"error": str(e), "year": int(year)}


# -------------------------
# MARK: Aggregations and Analysis
# -------------------------


def _calculate_trends(year_to_metrics: Dict[str, Optional[Dict[str, Any]]]) -> Dict[str, Any]:
    """Compute simple trend deltas between consecutive years for allocated/actual."""
    years_sorted = sorted([int(y) for y in year_to_metrics.keys()])
    deltas: List[Dict[str, Any]] = []
    prev: Optional[Dict[str, Any]] = None
    for y in years_sorted:
        curr = year_to_metrics.get(str(y)) or {}
        if prev:
            deltas.append(
                {
                    "year": y,
                    "allocated_delta": (curr.get("allocated") or 0) - (prev.get("allocated") or 0),
                    "actual_delta": (curr.get("actual") or 0) - (prev.get("actual") or 0),
                }
            )
        prev = curr
    return {"deltas": deltas}


@_SERVER.tool(
    "get_ministry_comparison",
    title="Compare ministry across years",
    description=(
        "Compare allocated/actual metrics across years for a ministry pattern. "
        "Parameters: years (list[int]), ministry_pattern (str), metrics (list[str])."
    ),
)
async def get_ministry_comparison(
    years: List[int],
    ministry_pattern: str,
    metrics: List[str] | None = None,
) -> Dict[str, Any]:
    """Return ministry comparison data ready for visualization."""
    metrics = metrics or ["allocated", "actual"]
    results: Dict[str, Optional[Dict[str, Any]]] = {}
    for year in years:
        try:
            summary = await get_ministry_spending_summary(int(year), ministry_pattern)
            if "error" in summary:
                results[str(year)] = None
            else:
                results[str(year)] = {k: summary.get(f"total_{k}", 0) for k in metrics} | {
                    "execution_rate": summary.get("execution_rate", 0)
                }
        except Exception:  # pragma: no cover - defensive
            results[str(year)] = None

    return {
        "ministry_pattern": ministry_pattern,
        "yearly_data": results,
        "trend_analysis": _calculate_trends(results),
        "chart_ready": True,
    }


@_SERVER.tool(
    "get_budget_distribution",
    title="Budget distribution",
    description=(
        "Pie-chart-ready distribution. Currently supports groupby='state_body'. "
        "Parameters: year (int), groupby (str), top_n (int)."
    ),
)
async def get_budget_distribution(
    year: int,
    groupby: str = "state_body",
    top_n: int = 20,
) -> Dict[str, Any]:
    """Return pie-chart ready budget distribution for the requested grouping."""
    if groupby != "state_body":
        return {"error": f"Unsupported groupby: {groupby}"}

    summary = _compute_state_body_summary_df(year)
    summary_sorted = summary.sort_values("state_body_total", ascending=False).head(int(top_n))
    total_budget = (
        float(summary_sorted["state_body_total"].sum()) if not summary_sorted.empty else 0.0
    )

    pie = [
        {
            "name": str(row["state_body"]),
            "value": int(row["state_body_total"]),
            "percentage": round((float(row["state_body_total"]) / total_budget * 100.0), 1)
            if total_budget > 0
            else 0.0,
        }
        for _, row in summary_sorted.iterrows()
    ]

    return {
        "pie_chart_data": pie,
        "total_budget": int(total_budget),
        "currency": "AMD",
        "year": int(year),
        "chart_type": "pie",
    }


# -------------------------
# MARK: Error Handling Utilities
# -------------------------


def _handle_readonly_filesystem() -> bool:
    """Detect and handle read-only filesystem scenarios."""
    try:
        test_file = Path("data/processed/tmp/test_write.txt")
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("test", encoding="utf-8")
        test_file.unlink(missing_ok=True)
        return True
    except Exception:
        logger.warning("Filesystem is read-only, using memory-only operations")
        return False


def _save_temp_file(df: pd.DataFrame) -> Path:
    tmp_dir = Path("data/processed/tmp")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = tmp_dir / f"filtered_{uuid4().hex[:8]}.csv"
    df.to_csv(tmp_path, index=False)
    return tmp_path


@_SERVER.tool(
    "filter_budget_data_enhanced",
    title="Filter dataset (enhanced)",
    description=(
        "Filter by state_body/program_codes/min_amount; returns data directly "
        "for small results or a temp file path for large ones. "
        "Parameters: year (int), source_type (str), force_file_output (bool=False), "
        "max_rows (int|None), filters via keyword args."
    ),
)
async def filter_budget_data_enhanced(
    year: int,
    source_type: str,
    force_file_output: bool = False,
    max_rows: Optional[int] = None,
    max_inline_bytes: int = 200_000,
    columns: Optional[List[str]] = None,
    exclude_columns: Optional[List[str]] = None,
    text_truncate_len: Optional[int] = None,
    **filters: Any,
) -> Dict[str, Any]:
    """Enhanced filtering with multiple return options (direct or temp file).

    Args:
        year: Dataset year
        source_type: Dataset type (e.g., BUDGET_LAW)
        force_file_output: If True and filesystem is writable, always write
            filtered results to a temp CSV
        max_rows: If provided, truncate filtered results to at most this many rows
    """
    try:
        csv_path = _resolve_csv_path(year, source_type)
        df = pd.read_csv(csv_path)
        filtered_df = _apply_filters(df, source_type, dict(filters))

        # Optional column selection
        if columns:
            keep = [c for c in columns if c in filtered_df.columns]
            if keep:
                filtered_df = filtered_df[keep]
        elif exclude_columns:
            drop = [c for c in exclude_columns if c in filtered_df.columns]
            if drop:
                filtered_df = filtered_df.drop(columns=drop, errors="ignore")

        # Optional truncation of long text fields to reduce payload
        if text_truncate_len is not None and text_truncate_len > 0:
            for col in filtered_df.select_dtypes(include=["object"]).columns:
                try:
                    filtered_df[col] = (
                        filtered_df[col].astype(str).str.slice(0, int(text_truncate_len))
                    )
                except Exception:
                    pass

        # Apply explicit row cap if requested
        if max_rows is not None and len(filtered_df) > int(max_rows):
            filtered_df = filtered_df.head(int(max_rows))

        can_write = _handle_readonly_filesystem()
        if can_write and (force_file_output or len(filtered_df) > 1000):
            temp_path = _save_temp_file(filtered_df)
            return {
                "method": "file",
                "file_path": str(temp_path),
                "row_count": int(len(filtered_df)),
                "data_preview": filtered_df.head(10).to_dict(orient="records"),
            }

        # Try inline, but protect against very large JSON responses
        data_records = filtered_df.to_dict(orient="records")
        payload = {
            "method": "direct",
            "data": data_records,
            "row_count": int(len(filtered_df)),
            "csv_content": filtered_df.to_csv(index=False) if len(filtered_df) < 500 else None,
        }
        try:
            serialized = json.dumps(payload, ensure_ascii=False)
        except Exception:
            serialized = "{}"

        if can_write and (force_file_output or len(serialized) > int(max_inline_bytes)):
            temp_path = _save_temp_file(filtered_df)
            return {
                "method": "file",
                "file_path": str(temp_path),
                "row_count": int(len(filtered_df)),
                "data_preview": filtered_df.head(10).to_dict(orient="records"),
            }

        return payload
    except FileNotFoundError as e:
        return {"error": str(e), "year": int(year), "source_type": str(source_type)}
    except Exception as e:  # pragma: no cover - defensive
        logger.error("Error in filter_budget_data_enhanced: %s", e)
        return {"error": str(e)}


# -------------------------
# MARK: Overall Totals Access
# -------------------------


@_SERVER.tool(
    "get_dataset_overall",
    title="Get overall totals",
    description=(
        "Return precomputed overall totals from *_overall.json files. "
        "Parameters: year (int|None), source_type (str|None). "
        "If year is None, include all years; if source_type is None, include all sources."
    ),
)
async def get_dataset_overall(
    year: Optional[int] = None, source_type: Optional[str] = None
) -> Dict[str, Any]:
    """Return nested mapping of overall totals.

    Shape:
        {
          "overalls": {
             "2024": {"BUDGET_LAW": {...}, "SPENDING_Q12": {...}},
             "2025": {"BUDGET_LAW": {...}}
          },
          "years": [2024, 2025],
          "source_types": ["BUDGET_LAW", "SPENDING_Q12"],
          "count": 3
        }
    """
    data_dir = _processed_data_dir()
    if not data_dir.exists():
        return {
            "overalls": {},
            "years": [],
            "source_types": [],
            "count": 0,
            "error": f"Processed data directory not found: {data_dir}",
        }

    filter_year: Optional[int] = int(year) if year is not None else None
    filter_source: Optional[str] = str(source_type).upper() if source_type is not None else None

    temp_result: Dict[int, Dict[str, Any]] = {}
    source_set: set[str] = set()
    total_entries = 0

    for path in data_dir.glob("*_overall.json"):
        name = path.name
        m = re.match(r"^(\d{4})_([A-Z0-9_]+)_overall\.json$", name)
        if not m:
            continue
        y = int(m.group(1))
        st = str(m.group(2))

        if filter_year is not None and y != filter_year:
            continue
        if filter_source is not None and st != filter_source:
            continue

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError, ValueError):
            # Skip unreadable files defensively
            continue

        temp_result.setdefault(y, {})[st] = data
        source_set.add(st)
        total_entries += 1

    if not temp_result:
        return {
            "overalls": {},
            "years": [],
            "source_types": [],
            "count": 0,
            "message": "No matching overall summaries found",
            "filters": {"year": filter_year, "source_type": filter_source},
        }

    # Sort years ascending for stable output
    years_sorted = sorted(temp_result.keys())
    overalls_sorted: Dict[str, Dict[str, Any]] = {str(y): temp_result[y] for y in years_sorted}

    return {
        "overalls": overalls_sorted,
        "years": years_sorted,
        "source_types": sorted(list(source_set)),
        "count": total_entries,
    }


# -------------------------
# MARK: Tool Metadata
# -------------------------


@_SERVER.tool(
    "get_tool_capabilities",
    title="List tool capabilities",
    description=(
        "Summarize available tools/resources with key parameters for "
        "discovery/autocomplete."
    ),
)
async def get_tool_capabilities() -> Dict[str, Any]:
    """Return metadata about available tools for discovery/autocomplete."""
    return {
        "data_access_tools": [
            {"name": "list_available_data", "output": "inventory", "parameters": []},
            {"name": "get_data_schema", "output": "schema", "parameters": ["year", "source_type"]},
            {
                "name": "preview_dataset",
                "output": "sample_data",
                "parameters": ["year", "source_type", "sample_size"],
            },
            {
                "name": "stream_budget_data",
                "output": "data",
                "parameters": ["year", "chunk_size", "offset", "filters"],
            },
            {
                "name": "filter_budget_data_enhanced",
                "output": "data|file",
                "parameters": [
                    "year",
                    "source_type",
                    "force_file_output",
                    "max_rows",
                    "filters...",
                ],
            },
            {
                "name": "bulk_filter_multiple_datasets",
                "output": "file_path",
                "parameters": ["filters", "years", "source_types"],
            },
            {
                "name": "get_dataset_overall",
                "output": "overalls",
                "parameters": ["year?", "source_type?"],
            },
            {
                "name": "get_ministry_spending_summary",
                "output": "summary",
                "parameters": ["year", "ministry"],
            },
            {
                "name": "filter_budget_data",
                "output": "file_path",
                "parameters": [
                    "year",
                    "source_type",
                    "state_body",
                    "program_codes",
                    "min_amount",
                    "max_rows",
                ],
                "deprecated": True,
                "replacement": "filter_budget_data_enhanced",
            },
        ],
        "visualization_tools": [
            {
                "name": "get_budget_visualization_data",
                "output": "data|csv_content",
                "parameters": ["year", "view_type", "output_format"],
            },
            {
                "name": "get_budget_distribution",
                "output": "pie_chart_data",
                "parameters": ["year", "groupby", "top_n"],
            },
            {
                "name": "get_ministry_comparison",
                "output": "trend_data",
                "parameters": ["years", "ministry_pattern", "metrics"],
            },
        ],
        "analysis_tools": [
            {
                "name": "find_program_across_years_robust",
                "output": "matches",
                "parameters": [
                    "reference_year",
                    "reference_program_code",
                    "search_years",
                    "similarity_threshold",
                    "include_ministry_context",
                ],
            },
            {
                "name": "search_programs_by_similarity",
                "output": "results",
                "parameters": [
                    "target_name",
                    "target_description",
                    "years",
                    "ministry_filter",
                    "min_similarity",
                ],
            },
            {
                "name": "trace_program_lineage",
                "output": "timeline",
                "parameters": ["starting_program", "search_years", "confidence_threshold"],
            },
            {
                "name": "detect_program_patterns",
                "output": "results",
                "parameters": ["pattern_type", "years", "custom_keywords", "confidence_threshold"],
            },
            {
                "name": "extract_rd_budget_robust",
                "output": "rd_budget_summary",
                "parameters": [
                    "years",
                    "confidence_threshold",
                    "include_manual_mappings",
                    "return_details",
                ],
            },
            {
                "name": "register_program_equivalency",
                "output": "success",
                "parameters": ["equivalency_map", "description"],
            },
            {"name": "get_program_equivalencies", "output": "equivalencies", "parameters": []},
        ],
        "resources": [
            {
                "uri": "budget://{year}/state-bodies-summary",
                "mime_type": "text/csv",
                "description": "Deduplicated state body totals for a given year",
            },
            {
                "uri": "budget://{year}/programs-summary",
                "mime_type": "text/csv",
                "description": "Program totals per state body for a given year",
            },
            {
                "uri": "budget://{year}/full-data",
                "mime_type": "text/csv",
                "description": "Full BUDGET_LAW dataset for a given year",
            },
        ],
    }


# -------------------------
# Pattern configuration I/O
# -------------------------

_PROGRAM_PATTERNS_CACHE: Optional[Dict[str, Dict[str, List[str]]]] = None


def _program_patterns_path() -> Path:
    return Path("config/program_patterns.yaml")


def _load_program_patterns(force_reload: bool = False) -> Dict[str, Dict[str, List[str]]]:
    """Load program patterns from YAML only.

    YAML structure expected:
    - top-level mapping of pattern_name -> config
    - or { patterns: { pattern_name: config } }
    where config has keys: keywords, required_keywords, exclude_keywords
    """
    global _PROGRAM_PATTERNS_CACHE
    if _PROGRAM_PATTERNS_CACHE is not None and not force_reload:
        return _PROGRAM_PATTERNS_CACHE

    path = _program_patterns_path()
    patterns: Dict[str, Dict[str, List[str]]] = {}
    if not path.exists():
        logger.error("Program patterns config not found: %s", path)
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            if isinstance(data, dict):
                raw = data.get("patterns", data)
                if isinstance(raw, dict):
                    for name, cfg in raw.items():
                        if not isinstance(cfg, dict):
                            continue
                        keywords = list(map(str, cfg.get("keywords", [])))
                        required = list(map(str, cfg.get("required_keywords", [])))
                        exclude = list(map(str, cfg.get("exclude_keywords", [])))
                        patterns[name] = {
                            "keywords": keywords,
                            "required_keywords": required,
                            "exclude_keywords": exclude,
                        }
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("Failed to load patterns from %s: %s", path, exc)
        patterns = {}

    # cache only non-empty results to allow later file creation without force_reload
    _PROGRAM_PATTERNS_CACHE = patterns or None
    return patterns


@_SERVER.tool("list_available_data")
async def list_available_data() -> Dict[str, Any]:
    """Return inventory of available datasets with diagnostics."""
    try:
        diagnostics = _validate_data_availability()
        data_dir = _processed_data_dir()
        csv_files = list(data_dir.glob("*.csv")) if data_dir.exists() else []

        budget_years: List[int] = []
        spending_by_year: Dict[int, List[str]] = {}

        for csv_file in csv_files:
            year, type_part = _extract_year_and_type(csv_file.name)
            if year is None or type_part is None:
                continue

            if type_part == "BUDGET_LAW":
                budget_years.append(year)
            elif type_part.startswith("SPENDING_"):
                quarter = type_part.replace("SPENDING_", "")
                spending_by_year.setdefault(year, []).append(quarter)

        # Remove duplicates and sort
        for year in spending_by_year:
            spending_by_year[year] = sorted(list(set(spending_by_year[year])))

        last_updated = None
        if csv_files:
            latest_mtime = max(f.stat().st_mtime for f in csv_files)
            last_updated = datetime.fromtimestamp(latest_mtime, tz=timezone.utc).isoformat()

        return {
            "budget_laws": sorted(budget_years),
            "spending_reports": {str(k): v for k, v in spending_by_year.items()},
            "formats": ["csv"],
            "last_updated": last_updated,
            "diagnostics": diagnostics,
            "total_datasets": len(csv_files),
        }

    except Exception as e:
        logger.error("Error in list_available_data: %s", e)
        return {
            "error": str(e),
            "diagnostics": _validate_data_availability(),
            "budget_laws": [],
            "spending_reports": {},
            "formats": [],
            "total_datasets": 0,
        }


@_SERVER.tool("get_data_schema")
async def get_data_schema(year: int, source_type: str) -> Dict[str, Any]:
    """Return schema information for a specific dataset."""
    try:
        data_dir = _processed_data_dir()
        filename = f"{year}_{source_type.upper()}.csv"
        csv_path = data_dir / filename

        if not csv_path.exists():
            available_files = [f.name for f in data_dir.glob("*.csv")]
            return {
                "error": f"Dataset not found: {filename}",
                "available_files": available_files[:10],
                "data_dir": str(data_dir),
            }

        # Read just a sample for schema detection
        df = pd.read_csv(csv_path, nrows=10)

        # Get full row count efficiently
        with open(csv_path, "r", encoding="utf-8") as f:
            total_rows = sum(1 for _ in f) - 1  # Subtract header

        # Get measure column mappings
        measures = _get_measure_columns(source_type)

        return {
            "year": year,
            "source_type": source_type,
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "shape": [total_rows, len(df.columns)],
            "file_path": str(csv_path),
            "measure_columns": measures,
            "sample_data": df.head(3).to_dict(orient="records"),
        }

    except Exception as e:
        logger.error("Error in get_data_schema: %s", e)
        return {"error": str(e)}


@_SERVER.tool("filter_budget_data")
async def filter_budget_data(
    year: int,
    source_type: str,
    state_body: Optional[str] = None,
    program_codes: Optional[List[int]] = None,
    min_amount: Optional[float] = None,
    max_rows: Optional[int] = 1000,
) -> str:
    """Filter dataset and return path to temporary CSV."""
    try:
        # Deprecation notice: prefer filter_budget_data_enhanced
        logger.warning(
            "DEPRECATED: 'filter_budget_data' will be removed in a future release. "
            "Use 'filter_budget_data_enhanced' with 'force_file_output' and 'max_rows' instead."
        )
        data_dir = _processed_data_dir()
        filename = f"{year}_{source_type.upper()}.csv"
        csv_path = data_dir / filename

        if not csv_path.exists():
            raise FileNotFoundError(f"Dataset not found: {filename}")

        df = pd.read_csv(csv_path)
        logger.info("Loaded %d rows from %s", len(df), filename)

        # Apply filters
        mask = pd.Series(True, index=df.index)

        if state_body:
            mask &= df["state_body"].astype(str).str.contains(state_body, case=False, na=False)

        if program_codes:
            mask &= df["program_code"].isin(program_codes)

        if min_amount is not None:
            measures = _get_measure_columns(source_type)
            amount_col = (
                measures.get("allocated") or measures.get("actual") or measures.get("revised")
            )
            if amount_col and amount_col in df.columns:
                numeric_col = pd.to_numeric(df[amount_col], errors="coerce").fillna(0)
                mask &= numeric_col >= min_amount

        filtered_df = df.loc[mask].copy()

        # Limit rows if requested
        if max_rows and len(filtered_df) > max_rows:
            filtered_df = filtered_df.head(max_rows)
            logger.info("Limited output to %d rows", max_rows)

        # Save to temporary file
        temp_dir = data_dir / "tmp"
        temp_dir.mkdir(exist_ok=True)

        temp_filename = f"filtered_{year}_{source_type}_{uuid4().hex[:8]}.csv"
        temp_path = temp_dir / temp_filename

        filtered_df.to_csv(temp_path, index=False)
        logger.info("Saved %d filtered rows to %s", len(filtered_df), temp_path)

        return str(temp_path)

    except Exception as e:
        logger.error("Error in filter_budget_data: %s", e)
        raise


@_SERVER.tool("find_program_across_years_robust")
async def find_program_across_years_robust(
    reference_year: int,
    reference_program_code: int,
    search_years: List[int],
    similarity_threshold: float = 0.7,
    include_ministry_context: bool = True,
) -> Dict[str, Any]:
    """Find the same conceptual program across years using multiple signals.

    Args:
        reference_year: Year with known program to use as reference
        reference_program_code: Program code in reference year
        search_years: Years to search for equivalent programs
        similarity_threshold: Minimum similarity score (0.0-1.0)
        include_ministry_context: Use ministry matching as additional signal

    Returns:
        {
            "reference_program": {program details},
            "matches": {
                "year": {
                    "exact_matches": [],
                    "fuzzy_matches": [{"program": {...}, "confidence": 0.85}],
                    "no_matches": []
                }
            },
            "summary": {"high_confidence": 3, "medium_confidence": 2, "missing": 1}
        }
    """
    try:
        # 1. Load reference program
        ref_csv_path = _resolve_csv_path(reference_year, "BUDGET_LAW")
        ref_df = pd.read_csv(ref_csv_path)
        ref_program = ref_df[ref_df["program_code"] == reference_program_code]

        if ref_program.empty:
            raise ValueError(
                f"Reference program {reference_program_code} not found in {reference_year}"
            )

        ref_data = ref_program.iloc[0].to_dict()

        # 2. Search each target year
        matches: Dict[str, Any] = {}
        for year in search_years:
            if year == reference_year:
                continue

            matches[str(year)] = await _find_program_matches_in_year(
                year, ref_data, similarity_threshold, include_ministry_context
            )

        # 3. Generate summary
        summary = _calculate_match_summary(matches)

        return {"reference_program": ref_data, "matches": matches, "summary": summary}

    except Exception as e:
        return {"error": str(e), "reference_program": None, "matches": {}, "summary": {}}


async def _find_program_matches_in_year(
    year: int, ref_data: Dict, threshold: float, use_ministry: bool
) -> Dict[str, List]:
    """Helper function to find program matches in a specific year."""
    try:
        csv_path = _resolve_csv_path(year, "BUDGET_LAW")
        df = pd.read_csv(csv_path)

        exact_matches: List[Dict[str, Any]] = []
        fuzzy_matches: List[Dict[str, Any]] = []

        # Check for exact program code match first
        exact = df[df["program_code"] == ref_data.get("program_code")]
        if not exact.empty:
            for _, row in exact.iterrows():
                exact_matches.append(
                    {"program": row.to_dict(), "confidence": 1.0, "match_reason": "exact_code"}
                )

        # Fuzzy matching on name and description
        for _, row in df.iterrows():
            if row.get("program_code") == ref_data.get("program_code"):
                continue  # Already in exact matches

            confidence = _calculate_program_similarity(ref_data, row.to_dict(), use_ministry)

            if confidence >= threshold:
                fuzzy_matches.append(
                    {
                        "program": row.to_dict(),
                        "confidence": round(confidence, 3),
                        "match_reason": "fuzzy_text",
                    }
                )

        # Sort fuzzy matches by confidence
        fuzzy_matches.sort(key=lambda x: x["confidence"], reverse=True)

        return {
            "exact_matches": exact_matches,
            "fuzzy_matches": fuzzy_matches[:5],  # Top 5 candidates
            "no_matches": [] if exact_matches or fuzzy_matches else ["no_suitable_matches"],
        }

    except FileNotFoundError:
        return {"exact_matches": [], "fuzzy_matches": [], "no_matches": ["file_not_found"]}


def _calculate_program_similarity(ref: Dict, candidate: Dict, use_ministry: bool) -> float:
    """Calculate similarity score between two programs using multiple signals."""
    scores: List[tuple[str, float, float]] = []

    # Program name similarity (weight: 0.4)
    name_sim = _armenian_text_similarity(
        str(ref.get("program_name", "")), str(candidate.get("program_name", ""))
    )
    scores.append(("name", name_sim, 0.4))

    # Program goal similarity (weight: 0.3)
    goal_sim = _armenian_text_similarity(
        str(ref.get("program_goal", "")), str(candidate.get("program_goal", ""))
    )
    scores.append(("goal", goal_sim, 0.3))

    # Ministry context similarity (weight: 0.2 if enabled)
    if use_ministry:
        ministry_sim = _armenian_text_similarity(
            str(ref.get("state_body", "")), str(candidate.get("state_body", ""))
        )
        scores.append(("ministry", ministry_sim, 0.2))

    # Budget magnitude similarity (weight: 0.1)
    budget_sim = _budget_magnitude_similarity(
        ref.get("program_total", 0), candidate.get("program_total", 0)
    )
    scores.append(("budget", budget_sim, 0.1))

    # Calculate weighted average
    total_weight = sum(weight for _, _, weight in scores)
    weighted_sum = sum(score * weight for _, score, weight in scores)

    return weighted_sum / total_weight if total_weight > 0 else 0.0


@_SERVER.tool("search_programs_by_similarity")
async def search_programs_by_similarity(
    target_name: str,
    target_description: Optional[str] = None,
    years: Optional[List[int]] = None,
    ministry_filter: Optional[str] = None,
    min_similarity: float = 0.6,
    max_per_year: int = 50,
    force_file_output: bool = False,
    max_inline_bytes: int = 200_000,
) -> Dict[str, Any]:
    """Find programs using fuzzy text matching across multiple years."""
    results: Dict[str, Any] = {}
    total_matches = 0
    years_with_matches = 0

    for year in years or []:
        try:
            csv_path = _resolve_csv_path(year, "BUDGET_LAW")
            df = pd.read_csv(csv_path)

            # Apply ministry filter if provided
            if ministry_filter:
                ministry_pattern = _normalize_armenian_text(ministry_filter)
                df = df[
                    df["state_body"]
                    .astype(str)
                    .str.contains(ministry_pattern, case=False, na=False)
                ]

            year_matches: List[Dict[str, Any]] = []

            for _, row in df.iterrows():
                similarity_scores = _calculate_text_similarities(
                    target_name, target_description, row
                )

                if similarity_scores["overall"] >= min_similarity:
                    year_matches.append(
                        {
                            "program": row.to_dict(),
                            "similarity_scores": similarity_scores,
                            "match_highlights": _extract_match_highlights(
                                target_name, str(row.get("program_name", ""))
                            ),
                        }
                    )

            # Sort by overall similarity and limit
            year_matches.sort(key=lambda x: x["similarity_scores"]["overall"], reverse=True)
            year_matches = year_matches[: int(max_per_year)]

            if year_matches:
                results[str(year)] = year_matches
                total_matches += len(year_matches)
                years_with_matches += 1

        except FileNotFoundError:
            continue

    payload = {
        "query": {"name": target_name, "description": target_description},
        "results": results,
        "summary": {"total_matches": total_matches, "years_with_matches": years_with_matches},
    }

    try:
        serialized = json.dumps(payload, ensure_ascii=False)
    except Exception:
        serialized = "{}"

    if force_file_output or len(serialized) > int(max_inline_bytes):
        try:
            # Flatten into a CSV file
            flat_rows: List[Dict[str, Any]] = []
            for y, matches in results.items():
                for m in matches:
                    p = m.get("program", {})
                    sim = m.get("similarity_scores", {})
                    flat_rows.append(
                        {
                            "year": int(y) if str(y).isdigit() else y,
                            "program_code": p.get("program_code"),
                            "program_name": p.get("program_name"),
                            "state_body": p.get("state_body"),
                            "overall": sim.get("overall"),
                            "name_sim": sim.get("name"),
                            "desc_sim": sim.get("description"),
                        }
                    )
            df_out = pd.DataFrame(flat_rows)
            temp_path = _save_temp_file(df_out)
            return {
                "method": "file",
                "file_path": str(temp_path),
                "row_count": int(len(df_out)),
                "summary": payload["summary"],
            }
        except Exception:  # pragma: no cover - defensive
            # Fall back to truncated JSON if file write fails
            pass

    return payload


def _calculate_text_similarities(
    target_name: str, target_desc: Optional[str], row: pd.Series
) -> Dict[str, float]:
    """Calculate similarity scores for name and description."""
    name_sim = _armenian_text_similarity(target_name, str(row.get("program_name", "")))

    desc_sim = 0.0
    if target_desc:
        desc_sim = max(
            _armenian_text_similarity(target_desc, str(row.get("program_goal", ""))),
            _armenian_text_similarity(target_desc, str(row.get("program_result_desc", ""))),
        )

    # Overall score (weighted average)
    if target_desc:
        overall = (name_sim * 0.7) + (desc_sim * 0.3)
    else:
        overall = name_sim

    return {
        "name": round(name_sim, 3),
        "description": round(desc_sim, 3),
        "overall": round(overall, 3),
    }


@_SERVER.tool("trace_program_lineage")
async def trace_program_lineage(
    starting_program: Dict[str, Any],  # {year, code, name, ministry}
    search_years: List[int],
    confidence_threshold: float = 0.8,
) -> Dict[str, Any]:
    """Trace a program's evolution across years with confidence scoring."""
    lineage: Dict[str, Any] = {}
    timeline: List[Dict[str, Any]] = []
    gaps: List[int] = []
    recommendations: List[str] = []

    # Start with the known program
    ref_year = starting_program["year"]
    ref_code = starting_program["code"]

    # Add starting point to timeline
    timeline.append({"year": ref_year, "code": ref_code, "confidence": 1.0, "status": "reference"})

    # Trace forward and backward from reference year
    all_years = sorted(search_years)

    for year in all_years:
        if year == ref_year:
            continue

        try:
            # Get the most recent confident match as reference
            current_ref = _get_latest_confident_match(timeline, year)

            matches = await _find_program_matches_in_year(
                year, current_ref, confidence_threshold, True
            )

            status, best_match, confidence, notes = _evaluate_lineage_matches(
                matches, confidence_threshold
            )

            lineage[str(year)] = {
                "status": status,
                "matches": matches,
                "confidence": confidence,
                "notes": notes,
            }

            if status == "found" and best_match is not None:
                timeline.append(
                    {
                        "year": year,
                        "code": best_match["program"]["program_code"],
                        "confidence": confidence,
                        "status": "traced",
                    }
                )
            elif status == "missing":
                gaps.append(year)
            elif status == "uncertain":
                recommendations.append(f"Manual review needed for {year} - multiple candidates")

        except Exception as e:  # pragma: no cover - defensive
            lineage[str(year)] = {
                "status": "error",
                "matches": {},
                "confidence": 0.0,
                "notes": f"Error: {str(e)}",
            }
            gaps.append(year)

    # Sort timeline by year
    timeline.sort(key=lambda x: x["year"])

    return {
        "lineage": lineage,
        "timeline": timeline,
        "gaps": sorted(gaps),
        "recommendations": recommendations,
    }


def _get_latest_confident_match(timeline: List[Dict], target_year: int) -> Dict:
    """Get the most recent confident match to use as reference."""
    # Find the closest year with high confidence
    confident_matches = [t for t in timeline if t.get("confidence", 0.0) >= 0.8]
    if not confident_matches:
        return timeline[0]  # Use original reference

    # Get closest year (prefer earlier years for forward tracing)
    closest = min(confident_matches, key=lambda x: abs(int(x["year"]) - int(target_year)))
    return {"program_code": closest["code"], "year": closest["year"]}


def _evaluate_lineage_matches(matches: Dict, threshold: float) -> tuple:
    """Evaluate lineage matches and determine status."""
    exact = matches.get("exact_matches", [])
    fuzzy = matches.get("fuzzy_matches", [])

    if exact:
        return "found", exact[0], 1.0, "Exact code match"

    if fuzzy:
        best = fuzzy[0]
        if best["confidence"] >= threshold:
            return "found", best, best["confidence"], "Fuzzy match above threshold"
        elif best["confidence"] >= 0.5:
            return "uncertain", best, best["confidence"], "Fuzzy match below threshold"

    return "missing", None, 0.0, "No suitable matches found"


@_SERVER.tool("register_program_equivalency")
async def register_program_equivalency(
    equivalency_map: Dict[str, List[Dict]], description: Optional[str] = None
) -> Dict[str, Any]:
    """Register manual program equivalencies for robust tracking."""
    config_path = Path("config/program_equivalencies.yaml")
    config_path.parent.mkdir(exist_ok=True)

    # Load existing equivalencies
    existing: Dict[str, Any] = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            existing = yaml.safe_load(f) or {}

    if "equivalencies" not in existing:
        existing["equivalencies"] = {}

    # Add new equivalencies
    registered_count = 0
    concept_ids: List[str] = []

    for concept_id, mappings in equivalency_map.items():
        existing["equivalencies"][concept_id] = {
            "description": description or f"Manual equivalency for {concept_id}",
            "mappings": mappings,
            "created_at": pd.Timestamp.now().isoformat(),
        }
        registered_count += len(mappings)
        concept_ids.append(concept_id)

    # Save back to file
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(existing, f, allow_unicode=True, sort_keys=False)

    return {
        "success": True,
        "registered": registered_count,
        "concept_ids": concept_ids,
        "config_path": str(config_path),
    }


@_SERVER.tool("get_program_equivalencies")
async def get_program_equivalencies() -> Dict[str, Any]:
    """Get all registered program equivalencies."""
    config_path = Path("config/program_equivalencies.yaml")

    if not config_path.exists():
        return {"equivalencies": {}, "count": 0}

    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    equivalencies = data.get("equivalencies", {})

    return {
        "equivalencies": equivalencies,
        "count": len(equivalencies),
        "config_path": str(config_path),
    }


@_SERVER.tool("detect_program_patterns")
async def detect_program_patterns(
    pattern_type: str,  # "research", "education", "infrastructure", "custom"
    years: List[int],
    custom_keywords: Optional[List[str]] = None,
    confidence_threshold: float = 0.7,
    max_per_year: int = 50,
    force_file_output: bool = False,
    max_inline_bytes: int = 200_000,
) -> Dict[str, Any]:
    """Detect programs matching conceptual patterns rather than exact identifiers."""
    # Load pattern keywords from YAML (with defaults if missing)
    patterns: Dict[str, Dict[str, List[str]]] = _load_program_patterns()
    if not patterns:
        return {
            "error": "No program patterns configured",
            "config_path": str(_program_patterns_path()),
            "hint": "Create YAML with a 'patterns' map of named keyword sets.",
        }

    if pattern_type == "custom":
        if not custom_keywords:
            return {"error": "custom_keywords required for pattern_type='custom'"}
        pattern_config = {
            "keywords": custom_keywords,
            "required_keywords": custom_keywords[:1],
            "exclude_keywords": [],
        }
    else:
        pattern_config = patterns.get(pattern_type)
        if not pattern_config:
            # Suggest available patterns from config
            return {
                "error": f"Unknown pattern_type: {pattern_type}",
                "available_patterns": sorted(list(patterns.keys())),
                "config_path": str(_program_patterns_path()),
            }

    results: Dict[str, Any] = {}
    total_programs = 0
    confidence_scores: List[float] = []

    for year in years:
        try:
            csv_path = _resolve_csv_path(year, "BUDGET_LAW")
            df = pd.read_csv(csv_path)

            year_matches: List[Dict[str, Any]] = []

            for _, row in df.iterrows():
                match_result = _evaluate_pattern_match(row, pattern_config)

                if match_result["score"] >= confidence_threshold:
                    year_matches.append(
                        {
                            "program": row.to_dict(),
                            "match_score": match_result["score"],
                            "matched_keywords": match_result["matched_keywords"],
                            "match_locations": match_result["locations"],
                        }
                    )
                    confidence_scores.append(match_result["score"])

            if year_matches:
                year_matches.sort(key=lambda x: x["match_score"], reverse=True)
                year_matches = year_matches[: int(max_per_year)]
                results[str(year)] = year_matches
                total_programs += len(year_matches)

        except FileNotFoundError:
            continue

    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0

    payload = {
        "pattern": {"type": pattern_type, "keywords": pattern_config.get("keywords", [])},
        "results": results,
        "summary": {
            "total_programs": total_programs,
            "avg_confidence": round(avg_confidence, 3),
        },
    }

    try:
        serialized = json.dumps(payload, ensure_ascii=False)
    except Exception:
        serialized = "{}"

    if force_file_output or len(serialized) > int(max_inline_bytes):
        try:
            flat_rows = []
            for y, matches in results.items():
                for m in matches:
                    p = m.get("program", {})
                    flat_rows.append(
                        {
                            "year": int(y) if str(y).isdigit() else y,
                            "program_code": p.get("program_code"),
                            "program_name": p.get("program_name"),
                            "state_body": p.get("state_body"),
                            "match_score": m.get("match_score"),
                            "matched_keywords": ",".join(m.get("matched_keywords", [])),
                            "match_locations": ",".join(m.get("match_locations", [])),
                        }
                    )
            df_out = pd.DataFrame(flat_rows)
            temp_path = _save_temp_file(df_out)
            return {
                "method": "file",
                "file_path": str(temp_path),
                "row_count": int(len(df_out)),
                "summary": payload["summary"],
            }
        except Exception:  # pragma: no cover - defensive
            pass

    return payload


def _evaluate_pattern_match(row: pd.Series, pattern_config: Dict) -> Dict:
    """Evaluate how well a program matches a pattern."""
    text_fields = [
        ("name", str(row.get("program_name", ""))),
        ("goal", str(row.get("program_goal", ""))),
        ("description", str(row.get("program_result_desc", ""))),
    ]

    matched_keywords: set[str] = set()
    match_locations: List[str] = []

    for location, text in text_fields:
        normalized_text = _normalize_armenian_text(text).lower()

        for keyword in pattern_config["keywords"]:
            if keyword.lower() in normalized_text:
                matched_keywords.add(keyword)
                if location not in match_locations:
                    match_locations.append(location)

    # Check required keywords
    required_met = all(
        req in matched_keywords for req in pattern_config.get("required_keywords", [])
    )

    # Check exclusion keywords
    excluded_found = any(
        excl.lower() in " ".join(text for _, text in text_fields).lower()
        for excl in pattern_config.get("exclude_keywords", [])
    )

    if not required_met or excluded_found:
        score = 0.0
    else:
        # Score based on keyword match ratio
        score = len(matched_keywords) / max(1, len(pattern_config.get("keywords", [])))

        # Bonus for required keywords
        if required_met:
            score = min(1.0, score + 0.2)

    return {
        "score": round(score, 3),
        "matched_keywords": list(matched_keywords),
        "locations": match_locations,
    }


@_SERVER.tool("bulk_filter_multiple_datasets")
async def bulk_filter_multiple_datasets(
    filters: Dict[str, Any], years: List[int], source_types: Optional[List[str]] = None
) -> str:
    """Apply same filters across multiple years/datasets and return combined results.

    Returns:
        Path to combined CSV with added columns: year, source_type, dataset_name
    """
    if source_types is None:
        source_types = ["BUDGET_LAW"]

    combined_data: List[pd.DataFrame] = []

    for year in years:
        for source_type in source_types:
            try:
                csv_path = _resolve_csv_path(year, source_type)
                df = pd.read_csv(csv_path)

                # Apply filters
                mask = pd.Series(True, index=df.index)

                if "state_body" in filters:
                    mask &= (
                        df["state_body"]
                        .astype(str)
                        .str.contains(str(filters["state_body"]), case=False, na=False)
                    )

                if "program_codes" in filters:
                    mask &= df["program_code"].isin(filters["program_codes"])

                if "min_amount" in filters:
                    # Find appropriate amount column
                    amount_cols = [c for c in df.columns if ("total" in c) or ("actual" in c)]
                    if amount_cols:
                        primary_col = amount_cols[0]  # Use first available
                        mask &= pd.to_numeric(df[primary_col], errors="coerce").fillna(0) >= float(
                            filters["min_amount"]
                        )

                # Add metadata columns
                filtered_df = df.loc[mask].copy()
                if not filtered_df.empty:
                    filtered_df["year"] = year
                    filtered_df["source_type"] = source_type
                    filtered_df["dataset_name"] = f"{year}_{source_type}"
                    combined_data.append(filtered_df)

            except FileNotFoundError:
                continue

    tmp_dir = Path("data/processed/tmp")
    tmp_dir.mkdir(parents=True, exist_ok=True)

    if not combined_data:
        # Return empty file
        empty_path = tmp_dir / f"bulk_filter_empty_{uuid4().hex}.csv"
        pd.DataFrame().to_csv(empty_path, index=False)
        return _present_path(empty_path)

    # Combine all data
    combined_df = pd.concat(combined_data, ignore_index=True)

    # Save to temporary file
    tmp_path = tmp_dir / f"bulk_filter_{uuid4().hex}.csv"
    combined_df.to_csv(tmp_path, index=False)

    return _present_path(tmp_path)


@_SERVER.tool("extract_rd_budget_robust")
async def extract_rd_budget_robust(
    years: List[int],
    confidence_threshold: float = 0.8,
    include_manual_mappings: bool = True,
    return_details: bool = False,
) -> Dict[str, Any]:
    """Extract R&D budgets using robust program identification across ministries."""
    rd_summary: Dict[str, Any] = {}
    confidence_flags: List[str] = []
    details: Dict[str, Any] = {}

    # Load manual mappings if enabled
    manual_mappings: Dict[str, Any] = {}
    if include_manual_mappings:
        try:
            equiv_data = await get_program_equivalencies()
            manual_mappings = equiv_data.get("equivalencies", {})
        except Exception:  # pragma: no cover - defensive
            manual_mappings = {}

    for year in years:
        year_data: Dict[str, Any] = {
            "minescs": {"budget": 0, "confidence": 0.0, "program_code": None},
            "minhti": {"budget": 0, "confidence": 0.0, "subprogram_count": 0},
            "total": 0,
            "currency": "AMD",
        }

        if return_details:
            details[str(year)] = {"minescs_matches": [], "minhti_matches": []}

        # 1. Extract MinESCS R&D (Program 1162 and variants)
        minescs_result = await _extract_minescs_rd(year, manual_mappings, confidence_threshold)
        year_data["minescs"] = minescs_result["summary"]

        if minescs_result["confidence"] < confidence_threshold:
            confidence_flags.append(
                f"{year}: MinESCS R&D match uncertain (confidence: {minescs_result['confidence']})"
            )

        if return_details:
            details[str(year)]["minescs_matches"] = minescs_result["matches"]

        # 2. Extract MinHTI R&D (subprogram pattern matching)
        minhti_result = await _extract_minhti_rd(year, confidence_threshold)
        year_data["minhti"] = minhti_result["summary"]

        if (
            minhti_result["confidence"] < confidence_threshold
            and minhti_result["summary"]["budget"] > 0
        ):
            confidence_flags.append(
                f"{year}: MinHTI R&D pattern match (confidence: {minhti_result['confidence']})"
            )

        if return_details:
            details[str(year)]["minhti_matches"] = minhti_result["matches"]

        # 3. Calculate totals
        year_data["total"] = year_data["minescs"]["budget"] + year_data["minhti"]["budget"]

        rd_summary[str(year)] = year_data

    # Calculate data quality metrics
    complete_years = sum(
        1 for y in rd_summary.values() if y["minescs"]["budget"] > 0 and y["minhti"]["budget"] > 0
    )
    partial_years = sum(
        1
        for y in rd_summary.values()
        if (y["minescs"]["budget"] > 0) != (y["minhti"]["budget"] > 0)
    )
    missing_years = sum(1 for y in rd_summary.values() if y["total"] == 0)

    result: Dict[str, Any] = {
        "rd_budget_summary": rd_summary,
        "confidence_flags": confidence_flags,
        "data_quality": {
            "complete_years": complete_years,
            "partial_years": partial_years,
            "missing_years": missing_years,
        },
    }

    if return_details:
        result["details"] = details

    return result


async def _extract_minescs_rd(year: int, manual_mappings: Dict, threshold: float) -> Dict:
    """Extract MinESCS R&D budget for a specific year."""
    try:
        # Check manual mappings first
        for concept_id, mapping in manual_mappings.items():
            if "minescs" in concept_id.lower() or "research" in concept_id.lower():
                year_mapping = next(
                    (m for m in mapping.get("mappings", []) if m.get("year") == year), None
                )
                if year_mapping:
                    csv_path = _resolve_csv_path(year, "BUDGET_LAW")
                    df = pd.read_csv(csv_path)
                    program = df[df["program_code"] == year_mapping.get("program_code")]
                    if not program.empty:
                        return {
                            "summary": {
                                "budget": int(program.iloc[0]["program_total"]),
                                "confidence": 1.0,
                                "program_code": year_mapping.get("program_code"),
                            },
                            "confidence": 1.0,
                            "matches": [
                                {
                                    "source": "manual_mapping",
                                    "program": program.iloc[0].to_dict(),
                                }
                            ],
                        }

        # Try exact Program 1162 match
        csv_path = _resolve_csv_path(year, "BUDGET_LAW")
        df = pd.read_csv(csv_path)

        # Filter to education ministry first
        edu_ministry = df[
            df["state_body"].astype(str).str.contains("կրթություն", case=False, na=False)
        ]

        program_1162 = edu_ministry[edu_ministry["program_code"] == 1162]
        if not program_1162.empty:
            program_row = program_1162.iloc[0]
            return {
                "summary": {
                    "budget": int(program_row["program_total"]),
                    "confidence": 1.0,
                    "program_code": 1162,
                },
                "confidence": 1.0,
                "matches": [{"source": "exact_match", "program": program_row.to_dict()}],
            }

        # Try fuzzy matching for R&D programs in education ministry
        rd_matches: List[Dict[str, Any]] = []
        for _, row in edu_ministry.iterrows():
            name = str(row.get("program_name", "")).lower()
            goal = str(row.get("program_goal", "")).lower()

            rd_keywords = ["գիտական", "հետազոտ", "գիտատեխնիկական"]
            keyword_matches = sum(1 for kw in rd_keywords if (kw in name) or (kw in goal))

            if keyword_matches >= 2:  # Must match at least 2 R&D keywords
                confidence = min(1.0, keyword_matches / len(rd_keywords) + 0.3)
                rd_matches.append(
                    {
                        "program": row.to_dict(),
                        "confidence": confidence,
                        "matched_keywords": keyword_matches,
                    }
                )

        if rd_matches:
            best_match = max(rd_matches, key=lambda x: x["confidence"])
            if best_match["confidence"] >= threshold:
                return {
                    "summary": {
                        "budget": int(best_match["program"]["program_total"]),
                        "confidence": best_match["confidence"],
                        "program_code": best_match["program"]["program_code"],
                    },
                    "confidence": best_match["confidence"],
                    "matches": rd_matches,
                }

        return {
            "summary": {"budget": 0, "confidence": 0.0, "program_code": None},
            "confidence": 0.0,
            "matches": [],
        }

    except FileNotFoundError:
        return {
            "summary": {"budget": 0, "confidence": 0.0, "program_code": None},
            "confidence": 0.0,
            "matches": [],
        }


async def _extract_minhti_rd(year: int, threshold: float) -> Dict:
    """Extract MinHTI R&D budget for a specific year."""
    try:
        csv_path = _resolve_csv_path(year, "BUDGET_LAW")
        df = pd.read_csv(csv_path)

        # Filter to high-tech ministry
        hti_ministry = df[
            df["state_body"].astype(str).str.contains("բարձր տեխնոլոգիական", case=False, na=False)
        ]

        rd_subprograms: List[Dict[str, Any]] = []
        rd_pattern = "գիտահետազոտական և փորձակոնստրուկտորական աշխատանքներ"

        for _, row in hti_ministry.iterrows():
            subprog_name = str(row.get("subprogram_name", ""))

            # Check for exact R&D pattern
            if rd_pattern in subprog_name:
                rd_subprograms.append(
                    {
                        "subprogram": row.to_dict(),
                        "confidence": 1.0,
                        "match_type": "exact_pattern",
                    }
                )
            # Check for partial matches
            elif any(kw in subprog_name for kw in ["գիտահետազոտական", "փորձակոնստրուկտորական"]):
                confidence = 0.7 if "գիտահետազոտական" in subprog_name else 0.5
                rd_subprograms.append(
                    {
                        "subprogram": row.to_dict(),
                        "confidence": confidence,
                        "match_type": "partial_pattern",
                    }
                )

        # Calculate total budget
        total_budget = 0
        avg_confidence = 0.0
        qualifying_subprograms = [
            sp for sp in rd_subprograms if sp.get("confidence", 0.0) >= threshold
        ]

        if qualifying_subprograms:
            total_budget = sum(
                int(sp["subprogram"].get("subprogram_total", 0)) for sp in qualifying_subprograms
            )
            avg_confidence = sum(sp["confidence"] for sp in qualifying_subprograms) / len(
                qualifying_subprograms
            )

        return {
            "summary": {
                "budget": total_budget,
                "confidence": round(avg_confidence, 3),
                "subprogram_count": len(qualifying_subprograms),
            },
            "confidence": avg_confidence,
            "matches": rd_subprograms,
        }

    except FileNotFoundError:
        return {
            "summary": {"budget": 0, "confidence": 0.0, "subprogram_count": 0},
            "confidence": 0.0,
            "matches": [],
        }


def _armenian_text_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between Armenian texts using multiple algorithms."""
    if not text1 or not text2:
        return 0.0

    # Normalize texts
    norm1 = _normalize_armenian_text(text1)
    norm2 = _normalize_armenian_text(text2)

    # Try multiple similarity algorithms
    jw_score = 0.0
    _fuzz = _get_rapidfuzz_fuzz()
    if _fuzz is not None:
        try:
            jw_score = float(_fuzz.WRatio(norm1, norm2)) / 100.0
        except Exception:  # pragma: no cover - defensive
            jw_score = 0.0
    sequence_match = SequenceMatcher(None, norm1, norm2).ratio()

    # Return the higher score
    return max(jw_score, sequence_match)


def _normalize_armenian_text(text: str) -> str:
    """Normalize Armenian text for better matching."""
    if not text:
        return ""

    # Convert to string and strip
    text = str(text).strip()

    # Remove common punctuation variants
    for ch in [":", ".", "׳", "՝", "։", "-", "—", "–", "_", ",", ";"]:
        text = text.replace(ch, " ")

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Convert to lowercase (Armenian safe)
    text = text.lower()

    return text


def _budget_magnitude_similarity(budget1: float, budget2: float) -> float:
    """Calculate similarity based on budget magnitude."""
    try:
        b1 = float(pd.to_numeric(budget1, errors="coerce"))
        b2 = float(pd.to_numeric(budget2, errors="coerce"))
    except Exception:
        return 0.0

    if b1 == 0 and b2 == 0:
        return 1.0
    if b1 == 0 or b2 == 0:
        return 0.0

    ratio = min(b1, b2) / max(b1, b2)
    return float(ratio)


def _extract_match_highlights(target: str, candidate: str) -> List[str]:
    """Extract matching phrases between target and candidate text."""
    target_words = _normalize_armenian_text(target).split()
    candidate_words = _normalize_armenian_text(candidate).split()

    matches: List[str] = []
    for word in target_words:
        if len(word) > 2 and word in candidate_words:
            matches.append(word)

    return matches[:5]  # Return top 5 matches


def _calculate_match_summary(matches: Dict) -> Dict[str, int]:
    """Calculate summary statistics for match results."""
    high_confidence = 0
    medium_confidence = 0
    missing = 0

    for year_matches in matches.values():
        exact = year_matches.get("exact_matches", [])
        fuzzy = year_matches.get("fuzzy_matches", [])

        if exact:
            high_confidence += 1
        elif fuzzy and fuzzy[0]["confidence"] >= 0.8:
            high_confidence += 1
        elif fuzzy:
            medium_confidence += 1
        else:
            missing += 1

    return {
        "high_confidence": high_confidence,
        "medium_confidence": medium_confidence,
        "missing": missing,
    }


@_SERVER.tool("get_ministry_spending_summary")
async def get_ministry_spending_summary(year: int, ministry: str) -> Dict[str, Any]:
    """Get spending summary for a ministry across available datasets."""
    try:
        data_dir = _processed_data_dir()

        # Try to find the best dataset for this year
        preferred_order = [
            "SPENDING_Q1234",
            "SPENDING_Q123",
            "SPENDING_Q12",
            "SPENDING_Q1",
            "BUDGET_LAW",
        ]
        selected_type = None

        for source_type in preferred_order:
            filename = f"{year}_{source_type}.csv"
            if (data_dir / filename).exists():
                selected_type = source_type
                break

        if not selected_type:
            available = [f.name for f in data_dir.glob(f"{year}_*.csv")]
            return {"error": f"No data found for year {year}", "available_files": available}

        # Load and filter data
        csv_path = data_dir / f"{year}_{selected_type}.csv"
        df = pd.read_csv(csv_path)

        # Filter by ministry (case-insensitive partial match)
        ministry_data = df[
            df["state_body"].astype(str).str.contains(ministry, case=False, na=False)
        ]

        if ministry_data.empty:
            unique_ministries = df["state_body"].unique()[:10]
            return {
                "error": f"No data found for ministry '{ministry}'",
                "available_ministries": list(unique_ministries),
                "year": year,
                "source_type": selected_type,
            }

        # Calculate summaries
        measures = _get_measure_columns(selected_type)

        def safe_sum(col_name: str) -> float:
            if col_name in ministry_data.columns:
                return float(
                    pd.to_numeric(ministry_data[col_name], errors="coerce").fillna(0).sum()
                )
            return 0.0

        total_allocated = safe_sum(measures.get("allocated", ""))
        total_revised = safe_sum(measures.get("revised", ""))
        total_actual = safe_sum(measures.get("actual", ""))

        execution_rate = None
        if total_revised > 0 and total_actual > 0:
            execution_rate = round(total_actual / total_revised, 3)

        # Top programs
        top_programs = []
        amount_col = measures.get("allocated") or measures.get("actual") or measures.get("revised")
        if amount_col and amount_col in ministry_data.columns:
            program_totals = (
                ministry_data.groupby(["program_code", "program_name"])[amount_col]
                .sum()
                .sort_values(ascending=False)
                .head(5)
            )

            for (code, name), amount in program_totals.items():
                top_programs.append(
                    {
                        "code": int(code) if pd.notna(code) else None,
                        "name": str(name),
                        "amount": float(amount),
                    }
                )

        return {
            "ministry": ministry,
            "year": year,
            "source_type": selected_type,
            "total_allocated": total_allocated if total_allocated > 0 else None,
            "total_revised": total_revised if total_revised > 0 else None,
            "total_actual": total_actual if total_actual > 0 else None,
            "execution_rate": execution_rate,
            "program_count": int(ministry_data["program_code"].nunique()),
            "subprogram_count": int(ministry_data["subprogram_code"].nunique()),
            "top_programs": top_programs,
            "total_records": len(ministry_data),
        }

    except Exception as e:
        logger.error("Error in get_ministry_spending_summary: %s", e)
        return {"error": str(e)}


# Transport functions
def run(data_path: Optional[str] = None) -> None:
    """Run MCP server over stdio."""
    global _DATA_ROOT
    _DATA_ROOT = Path(data_path) if data_path else Path("data/processed")

    logger.info("Starting MCP server with data path: %s", _DATA_ROOT)
    logger.info("Processed data directory: %s", _processed_data_dir())

    asyncio.run(_SERVER.run_stdio_async())


async def _run_http(host: str, port: int) -> None:
    """Start HTTP server with explicit uvicorn configuration."""
    try:
        import uvicorn
    except ImportError:
        raise RuntimeError("uvicorn is required for HTTP mode: pip install uvicorn")

    app = _SERVER.streamable_http_app()
    config = uvicorn.Config(
        app,
        host=host,
        port=int(port),
        log_level="info",
    )
    server = uvicorn.Server(config)
    await server.serve()


def run_http(data_path: Optional[str] = None, *, host: str = "127.0.0.1", port: int = 8765) -> None:
    """Run MCP server over HTTP."""
    global _DATA_ROOT
    _DATA_ROOT = Path(data_path) if data_path else Path("data/processed")

    logger.info("Starting HTTP MCP server on %s:%d", host, port)
    logger.info("Data path: %s", _DATA_ROOT)

    # Use our explicit uvicorn config instead of FastMCP's default
    asyncio.run(_run_http(host, port))


def run_https(
    data_path: Optional[str] = None,
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
    certfile: str = "config/certs/localhost.pem",
    keyfile: str = "config/certs/localhost-key.pem",
) -> None:
    """Run MCP server over HTTPS."""
    global _DATA_ROOT
    _DATA_ROOT = Path(data_path) if data_path else Path("data/processed")

    logger.info("Starting HTTPS MCP server on %s:%d", host, port)
    logger.info("Data path: %s", _DATA_ROOT)

    # Import uvicorn here to avoid startup dependency
    try:
        import uvicorn
    except ImportError:
        raise RuntimeError("uvicorn is required for HTTPS mode: pip install uvicorn")

    app = _SERVER.streamable_http_app()
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level="info",
        ssl_certfile=certfile,
        ssl_keyfile=keyfile,
    )
    server = uvicorn.Server(config)
    asyncio.run(server.serve())
