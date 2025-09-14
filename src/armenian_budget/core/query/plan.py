from __future__ import annotations

from typing import Any, Dict, List, Optional

import polars as pl


def _apply_filters(
    lf: pl.LazyFrame, filters: Optional[List[Dict[str, Any]]]
) -> pl.LazyFrame:
    if not filters:
        return lf
    exprs = []
    for f in filters:
        col = f.get("col")
        op = f.get("op")
        val = f.get("value")
        if not col or op is None:
            continue
        c = pl.col(col)
        if op == "eq":
            exprs.append(c == val)
        elif op == "neq":
            exprs.append(c != val)
        elif op == "in":
            exprs.append(c.is_in(val if isinstance(val, list) else [val]))
        elif op == "contains":
            exprs.append(
                pl.col(col)
                .cast(pl.Utf8, strict=False)
                .str.contains(str(val), literal=True)
            )
        elif op == "regex":
            exprs.append(
                pl.col(col)
                .cast(pl.Utf8, strict=False)
                .str.contains(str(val), literal=False)
            )
        elif op == "range":
            rng = val or {}
            mn = rng.get("min")
            mx = rng.get("max")
            if mn is not None:
                exprs.append(c >= mn)
            if mx is not None:
                exprs.append(c <= mx)
        # normalized_contains is deferred for Phase 3 pattern support
    if exprs:
        lf = lf.filter(pl.all_horizontal(exprs))
    return lf


def build_lazy_query(
    lf: pl.LazyFrame,
    *,
    columns: Optional[List[str]] = None,
    filters: Optional[List[Dict[str, Any]]] = None,
    group_by: Optional[List[str]] = None,
    aggs: Optional[List[Dict[str, str]]] = None,
    distinct: bool = False,
    order_by: Optional[List[Dict[str, Any]]] = None,
) -> pl.LazyFrame:
    """Build a LazyFrame pipeline from structured knobs.

    Minimal implementation for Phase 1–2.
    """
    if columns:
        keep = [c for c in columns if c in lf.columns]
        if keep:
            lf = lf.select(keep)

    lf = _apply_filters(lf, filters)

    if distinct:
        lf = lf.unique()

    if group_by and aggs:
        agg_exprs = []
        for a in aggs:
            col = a.get("col")
            fn = (a.get("fn") or "sum").lower()
            if not col:
                continue
            if fn == "sum":
                agg_exprs.append(pl.col(col).sum().alias(f"{col}_sum"))
            elif fn == "avg":
                agg_exprs.append(pl.col(col).mean().alias(f"{col}_avg"))
            elif fn == "min":
                agg_exprs.append(pl.col(col).min().alias(f"{col}_min"))
            elif fn == "max":
                agg_exprs.append(pl.col(col).max().alias(f"{col}_max"))
            elif fn == "median":
                agg_exprs.append(pl.col(col).median().alias(f"{col}_median"))
            elif fn == "count":
                agg_exprs.append(pl.count().alias("count"))
            elif fn == "count_distinct":
                agg_exprs.append(pl.col(col).n_unique().alias(f"{col}_n_unique"))
        lf = lf.group_by(group_by).agg(agg_exprs)

    if order_by:
        by_cols = []
        descending = []
        for ob in order_by:
            by_cols.append(ob.get("col"))
            descending.append(bool(ob.get("desc", False)))
        lf = lf.sort(by_cols, descending=descending)

    return lf
