"""
Minimal MCP server exposing basic data access tools for processed datasets.

Implements tools documented in docs/architecture.md Phase 1:
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
from uuid import uuid4
import sys

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


def _processed_csv_dir() -> Path:
    """Get the CSV directory, with validation."""
    if _DATA_ROOT is None:
        base = Path("data/processed/csv")
    else:
        base = _DATA_ROOT / "csv"

    if not base.exists():
        logger.warning("CSV directory does not exist: %s", base)
        base.mkdir(parents=True, exist_ok=True)

    return base


def _validate_data_availability() -> Dict[str, Any]:
    """Check what data is actually available and return diagnostics."""
    csv_dir = _processed_csv_dir()
    csv_files = list(csv_dir.glob("*.csv")) if csv_dir.exists() else []

    return {
        "csv_dir": str(csv_dir),
        "csv_dir_exists": csv_dir.exists(),
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


@_SERVER.tool("list_available_data")
async def list_available_data() -> Dict[str, Any]:
    """Return inventory of available datasets with diagnostics."""
    try:
        diagnostics = _validate_data_availability()
        csv_dir = _processed_csv_dir()
        csv_files = list(csv_dir.glob("*.csv")) if csv_dir.exists() else []

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
        csv_dir = _processed_csv_dir()
        filename = f"{year}_{source_type.upper()}.csv"
        csv_path = csv_dir / filename

        if not csv_path.exists():
            available_files = [f.name for f in csv_dir.glob("*.csv")]
            return {
                "error": f"Dataset not found: {filename}",
                "available_files": available_files[:10],
                "csv_dir": str(csv_dir),
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
        csv_dir = _processed_csv_dir()
        filename = f"{year}_{source_type.upper()}.csv"
        csv_path = csv_dir / filename

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
        temp_dir = csv_dir.parent / "tmp"
        temp_dir.mkdir(exist_ok=True)

        temp_filename = f"filtered_{year}_{source_type}_{uuid4().hex[:8]}.csv"
        temp_path = temp_dir / temp_filename

        filtered_df.to_csv(temp_path, index=False)
        logger.info("Saved %d filtered rows to %s", len(filtered_df), temp_path)

        return str(temp_path)

    except Exception as e:
        logger.error("Error in filter_budget_data: %s", e)
        raise


@_SERVER.tool("get_ministry_spending_summary")
async def get_ministry_spending_summary(year: int, ministry: str) -> Dict[str, Any]:
    """Get spending summary for a ministry across available datasets."""
    try:
        csv_dir = _processed_csv_dir()

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
            if (csv_dir / filename).exists():
                selected_type = source_type
                break

        if not selected_type:
            available = [f.name for f in csv_dir.glob(f"{year}_*.csv")]
            return {"error": f"No data found for year {year}", "available_files": available}

        # Load and filter data
        csv_path = csv_dir / f"{year}_{selected_type}.csv"
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
    logger.info("CSV directory: %s", _processed_csv_dir())

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
