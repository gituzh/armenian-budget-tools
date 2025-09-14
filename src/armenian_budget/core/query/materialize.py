from __future__ import annotations
from typing import Any, Dict, List, Optional
import polars as pl


DEFAULT_MAX_ROWS = 5000
DEFAULT_MAX_BYTES = (
    2_000_000  # ~2MB inline budget; server will switch to file/handle beyond
)


def estimate_result_size(
    lf: pl.LazyFrame, *, sample_rows: int = 1000
) -> Dict[str, int]:
    """Estimate row/byte size by sampling a small materialization.

    This is a simple estimator; can be improved with statistics later.
    """
    try:
        sample = lf.limit(sample_rows).collect()
        row_estimate = sample.height
        # Rough JSON byte estimate: sum lengths of stringified rows (bounded)
        # Note: This is a fallback heuristic; server may also use file size hints.
        approx_bytes = len(sample.write_json(row_oriented=True))
        return {"row_estimate": int(row_estimate), "byte_estimate": int(approx_bytes)}
    except Exception:
        return {"row_estimate": 0, "byte_estimate": 0}


def materialize_result(
    lf: pl.LazyFrame,
    *,
    limit: Optional[int] = None,
    offset: int = 0,
    format: str = "json",
    max_rows: int = DEFAULT_MAX_ROWS,
    max_bytes: int = DEFAULT_MAX_BYTES,
) -> Dict[str, Any]:
    """Materialize a small result directly; defer large ones to file/handle in MCP layer.

    Returns a dict payload suitable for MCP tool responses when inline is allowed.
    """
    if offset:
        lf = lf.slice(offset, None)
    if limit:
        lf = lf.limit(limit)
    df = lf.collect()

    if format == "json":
        data = df.to_dicts()
        # very rough inline cap check
        if len(data) > max_rows:
            data = data[:max_rows]
        # byte cap approx
        import json as _json

        s = _json.dumps({"data": data})
        if len(s.encode("utf-8")) > max_bytes:
            # Caller should switch to file/handle
            return {"method": "too_large", "row_count": int(df.height)}
        return {
            "method": "direct",
            "data": data,
            "row_count": int(df.height),
        }
    elif format in {"csv", "parquet"}:
        # Leave file/handle writing to the MCP layer. Return small preview only.
        preview = df.head(10).to_dicts()
        return {"method": "preview", "preview": preview, "row_count": int(df.height)}
    else:
        raise ValueError(f"Unsupported format: {format}")


def distinct_values(
    lf: pl.LazyFrame, column: str, *, limit: int = 100, min_count: int = 1
) -> List[Dict[str, Any]]:
    out = (
        lf.group_by(column)
        .agg(pl.len().alias("count"))
        .sort("count", descending=True)
        .filter(pl.col("count") >= min_count)
        .limit(limit)
        .collect()
        .to_dicts()
    )
    # normalize None values for transport
    for row in out:
        if row.get(column) is None:
            row[column] = None
    return out
