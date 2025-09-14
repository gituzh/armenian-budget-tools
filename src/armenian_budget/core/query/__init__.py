"""Core query engine public API (skeleton).

Exposes minimal functions used by MCP and CLI layers. Implementations are
provided in sibling modules. This package centralizes data discovery,
schema roles, and query planning over Polars LazyFrames.
"""

from .catalog import list_datasets, get_dataset_schema
from .roles import get_column_roles
from .scan import scan_dataset
from .plan import build_lazy_query
from .materialize import estimate_result_size, materialize_result, distinct_values
from .patterns import normalize_armenian_text, build_pattern_candidates

__all__ = [
    "list_datasets",
    "get_dataset_schema",
    "get_column_roles",
    "scan_dataset",
    "build_lazy_query",
    "estimate_result_size",
    "materialize_result",
    "distinct_values",
    "normalize_armenian_text",
    "build_pattern_candidates",
]
