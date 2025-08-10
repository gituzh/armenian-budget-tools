"""Minimal MCP server exposing basic data access tools for processed datasets.

Implements tools documented in docs/architecture.md Phase 1:
 - list_available_data
 - get_data_schema
 - filter_budget_data
 - get_ministry_spending_summary

Transport: stdio (sufficient for local MCP clients like IDEs).
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4
import os

import pandas as pd

try:
    # Official Python MCP SDK (FastMCP provides decorators and stdio runner)
    from mcp.server.fastmcp import FastMCP
except Exception as exc:  # pragma: no cover - informative import error
    raise RuntimeError(
        "The 'mcp' package is required for the MCP server. Install with: pip install mcp"
    ) from exc


# Global configuration for the server instance
_DATA_ROOT: Path | None = None  # Path pointing to data/processed
_SERVER = FastMCP("armenian-budget-tools")


# ----------------------------- Helpers -------------------------------------


def _processed_csv_dir() -> Path:
    if _DATA_ROOT is None:
        # Default relative to CWD: ./data/processed/csv
        return Path("data/processed/csv")
    return _DATA_ROOT / "csv"


def _normalize_source_type(source_type: str) -> str:
    return str(source_type).strip().upper()


def _build_csv_filename(year: int, source_type: str) -> str:
    return f"{int(year)}_{_normalize_source_type(source_type)}.csv"


def _resolve_csv_path(year: int, source_type: str) -> Path:
    candidate = _processed_csv_dir() / _build_csv_filename(year, source_type)
    if not candidate.exists():
        raise FileNotFoundError(f"CSV not found: {candidate}")
    return candidate


def _list_processed_csvs() -> List[Path]:
    csv_dir = _processed_csv_dir()
    if not csv_dir.exists():
        return []
    return sorted(p for p in csv_dir.glob("*.csv") if p.is_file())


def _present_path(path_like: Path) -> str:
    """Return a relative presentation of a path when possible.

    - Prefer path relative to current working directory.
    - Fallback to os.path.relpath
    - Last resort: file name
    """
    try:
        rel = path_like.resolve().relative_to(Path.cwd().resolve())
        return rel.as_posix()
    except Exception:
        try:
            return os.path.relpath(str(path_like), start=str(Path.cwd()))
        except Exception:
            return path_like.name


def _extract_year_and_type(
    filename: str,
) -> Tuple[Optional[int], Optional[str]]:
    name = Path(filename).name
    if not name.endswith(".csv"):
        return None, None
    stem = name[:-4]
    if "_" not in stem:
        return None, None
    year_part, type_part = stem.split("_", 1)
    try:
        year = int(year_part)
    except ValueError:
        return None, None
    return year, type_part


def _get_measure_columns(source_type: str) -> Dict[str, str]:
    """Return role->column mapping based on dataset type.

    Roles: allocated, revised, actual, execution_rate
    """
    st = _normalize_source_type(source_type)
    if st == "BUDGET_LAW":
        return {"allocated": "subprogram_total"}
    if st in {"SPENDING_Q1", "SPENDING_Q12", "SPENDING_Q123"}:
        return {
            "allocated": "subprogram_annual_plan",
            "revised": "subprogram_rev_annual_plan",
            "actual": "subprogram_actual",
            "execution_rate": "subprogram_actual_vs_rev_annual_plan",
        }
    if st == "SPENDING_Q1234":
        return {
            "allocated": "subprogram_annual_plan",
            "revised": "subprogram_rev_annual_plan",
            "actual": "subprogram_actual",
        }
    return {}


# ------------------------------ Tools --------------------------------------


@_SERVER.tool("list_available_data")
async def list_available_data() -> Dict[str, Any]:
    """Return inventory of processed datasets available under data/processed.

    Scans csv/ subdir and groups by type.
    """
    csv_files = _list_processed_csvs()
    budget_years: List[int] = []
    spending_by_year: Dict[int, List[str]] = {}

    for p in csv_files:
        year, type_part = _extract_year_and_type(p.name)
        if year is None or type_part is None:
            continue
        if type_part == "BUDGET_LAW":
            budget_years.append(year)
        elif type_part.startswith("SPENDING_"):
            spending_by_year.setdefault(year, [])
            if type_part.replace("SPENDING_", "") not in spending_by_year[year]:
                spending_by_year[year].append(type_part.replace("SPENDING_", ""))

    formats = ["csv"]
    # If parquet/ exists, advertise it
    if (_DATA_ROOT or Path("data/processed")).joinpath("parquet").exists():
        formats.append("parquet")

    last_updated: Optional[str] = None
    if csv_files:
        latest = max(p.stat().st_mtime for p in csv_files)
        last_updated = datetime.fromtimestamp(latest, tz=timezone.utc).isoformat()

    return {
        "budget_laws": sorted(sorted(set(budget_years))),
        "spending_reports": {str(y): sorted(v) for y, v in spending_by_year.items()},
        "formats": formats,
        "last_updated": last_updated,
        "root": _present_path((_DATA_ROOT or Path("data/processed"))),
    }


@_SERVER.tool("get_data_schema")
async def get_data_schema(year: int, source_type: str) -> Dict[str, Any]:
    """Return column names, dtypes, shape, and file path for a dataset."""
    csv_path = _resolve_csv_path(year, source_type)
    df = pd.read_csv(csv_path, nrows=100)  # partial read for speed
    # If fewer than 100 rows, re-read fully only if needed for shape
    total_rows = sum(1 for _ in open(csv_path, "r", encoding="utf-8")) - 1
    dtypes = {c: str(dt) for c, dt in df.dtypes.items()}
    return {
        "columns": list(df.columns),
        "dtypes": dtypes,
        "shape": [total_rows, len(df.columns)],
        "file_path": _present_path(csv_path),
    }


@_SERVER.tool("filter_budget_data")
async def filter_budget_data(
    year: int,
    source_type: str,
    state_body: Optional[str] = None,
    program_codes: Optional[List[int]] = None,
    min_amount: Optional[float] = None,
) -> str:
    """Filter budget data and return path to a temporary CSV.

    - Filters are applied vectorially using pandas.
    - min_amount threshold applies to the primary measure column (allocated).
    """
    csv_path = _resolve_csv_path(year, source_type)
    df = pd.read_csv(csv_path)

    mask = pd.Series(True, index=df.index)
    if state_body:
        mask &= df["state_body"].astype(str) == str(state_body)
    if program_codes:
        mask &= df["program_code"].isin([int(x) for x in program_codes])
    if min_amount is not None:
        measures = _get_measure_columns(source_type)
        amount_col = measures.get("allocated") or measures.get("actual") or measures.get("revised")
        if amount_col and amount_col in df.columns:
            mask &= pd.to_numeric(df[amount_col], errors="coerce").fillna(0) >= float(min_amount)

    filtered = df.loc[mask].copy()
    tmp_dir = Path("data/processed/tmp")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = tmp_dir / f"filtered_{year}_{_normalize_source_type(source_type)}_{uuid4().hex}.csv"
    filtered.to_csv(tmp_path, index=False)
    return _present_path(tmp_path)


@_SERVER.tool("get_ministry_spending_summary")
async def get_ministry_spending_summary(year: int, ministry: str) -> Dict[str, Any]:
    """Compute totals and simple summary for a given ministry/state body.

    Works for both budget laws and spending reports.
    """
    # Heuristically pick the best available dataset for the year.
    # Prefer SPENDING_Q1234, then Q123, Q12, Q1, else BUDGET_LAW.
    preferred = [
        "SPENDING_Q1234",
        "SPENDING_Q123",
        "SPENDING_Q12",
        "SPENDING_Q1",
        "BUDGET_LAW",
    ]
    csv_dir = _processed_csv_dir()
    selected_type: Optional[str] = None
    for t in preferred:
        if (csv_dir / _build_csv_filename(year, t)).exists():
            selected_type = t
            break
    if selected_type is None:
        raise FileNotFoundError(f"No processed dataset for {year} among: {', '.join(preferred)}")

    csv_path = _resolve_csv_path(year, selected_type)
    df = pd.read_csv(csv_path)
    df = df[df["state_body"].astype(str) == str(ministry)]

    measures = _get_measure_columns(selected_type)
    allocated_col = measures.get("allocated")
    revised_col = measures.get("revised")
    actual_col = measures.get("actual")

    def _sum(col: Optional[str]) -> float:
        if not col or col not in df.columns:
            return 0.0
        return float(pd.to_numeric(df[col], errors="coerce").fillna(0).sum())

    total_allocated = _sum(allocated_col)
    total_actual = _sum(actual_col)
    total_revised = _sum(revised_col)
    execution_rate = (total_actual / total_revised) if total_revised else None

    program_count = int(df["program_code"].nunique()) if "program_code" in df else 0
    subprogram_count = int(df["subprogram_code"].nunique()) if "subprogram_code" in df else 0

    # Top programs by allocated/actual depending on availability
    amount_col = allocated_col or actual_col or revised_col
    top_programs: List[Dict[str, Any]] = []
    if amount_col and amount_col in df.columns:
        grouped = (
            df.groupby(["program_code", "program_name"], dropna=False)[amount_col]
            .sum()
            .sort_values(ascending=False)
            .head(5)
        )
        for (code, name), amount in grouped.items():
            top_programs.append(
                {
                    "code": int(code) if pd.notna(code) else None,
                    "name": str(name),
                    "amount": float(amount),
                }
            )

    return {
        "ministry": ministry,
        "year": int(year),
        "source_type": selected_type,
        "total_allocated": total_allocated or None,
        "total_revised": total_revised or None,
        "total_actual": total_actual or None,
        "execution_rate": execution_rate,
        "program_count": program_count,
        "subprogram_count": subprogram_count,
        "top_programs": top_programs,
    }


# ---------------------------- Entrypoint -----------------------------------


@dataclass
class ServerConfig:
    data_root: Path


async def _run_stdio() -> None:
    await _SERVER.run_stdio_async()


def run(data_path: Optional[str] = None) -> None:
    """Run the MCP server over stdio.

    Args:
        data_path: Path to data/processed directory. Defaults to ./data/processed.
    """
    global _DATA_ROOT
    _DATA_ROOT = Path(data_path) if data_path else Path("data/processed")
    asyncio.run(_run_stdio())


async def _run_http(host: str, port: int) -> None:
    # Configure server settings before starting HTTP transport
    try:
        _SERVER.settings.host = host
        _SERVER.settings.port = int(port)
    except Exception:
        pass
    await _SERVER.run_streamable_http_async()


def run_http(data_path: Optional[str] = None, *, host: str = "127.0.0.1", port: int = 8000) -> None:
    """Run the MCP server over HTTP for remote connectors (e.g., Claude custom connector).

    Args:
        data_path: Path to data/processed directory. Defaults to ./data/processed.
        host: Bind host (default 127.0.0.1).
        port: Bind port (default 8000).
    """
    global _DATA_ROOT
    _DATA_ROOT = Path(data_path) if data_path else Path("data/processed")
    asyncio.run(_run_http(host, int(port)))


async def _run_https(host: str, port: int, certfile: str, keyfile: str) -> None:
    # Configure host/port and security, then start HTTPS server via uvicorn
    from mcp.server.transport_security import TransportSecuritySettings
    import uvicorn

    try:
        _SERVER.settings.host = host
        _SERVER.settings.port = int(port)
        _SERVER.settings.transport_security = TransportSecuritySettings(
            allowed_hosts=[host, "localhost", "127.0.0.1"],
            allowed_origins=[f"https://{host}:{port}", "https://localhost", "https://127.0.0.1"],
        )
    except Exception:
        pass

    app = _SERVER.streamable_http_app()
    config = uvicorn.Config(
        app,
        host=host,
        port=int(port),
        log_level=getattr(_SERVER.settings, "log_level", "INFO").lower(),
        ssl_certfile=str(certfile),
        ssl_keyfile=str(keyfile),
    )
    server = uvicorn.Server(config)
    await server.serve()


def run_https(
    data_path: Optional[str] = None,
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
    certfile: str = "config/certs/localhost.pem",
    keyfile: str = "config/certs/localhost-key.pem",
) -> None:
    """Run the MCP server over HTTPS for remote connectors that require TLS.

    Args:
        data_path: Path to data/processed directory. Defaults to ./data/processed.
        host: Bind host (default 127.0.0.1).
        port: Bind port (default 8765).
        certfile: Path to PEM certificate file.
        keyfile: Path to PEM private key file.
    """
    global _DATA_ROOT
    _DATA_ROOT = Path(data_path) if data_path else Path("data/processed")
    asyncio.run(_run_https(host, int(port), certfile, keyfile))
