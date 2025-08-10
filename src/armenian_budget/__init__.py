"""Armenian Budget Tools (v0.2.0) — minimal package for CLI and validation.

This package intentionally reuses the existing parser functions from the
`budget` package (under `src/budget-am/budget`). In v0.1 we provide a minimal
CLI (process, validate) that operates on CSV outputs.
"""

__all__ = [
    "__version__",
]

__version__ = "0.2.0"

# Expose sources subpackage for downstream imports like
# `from armenian_budget.sources.registry import SourceRegistry`
from . import sources  # noqa: F401
