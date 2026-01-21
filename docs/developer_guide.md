# Developer Guide

> **When to read this:** Contributors and AI agents working with this codebase. This guide provides essential patterns, references to actual code, and API signatures.
>
> **Documentation Philosophy:** This guide is minimal and purposeful—covering only patterns and context that cannot be understood from reading the code alone. For design decisions, see `architecture.md`.

## Quick Setup

```bash
git clone https://github.com/gituzh/armenian-budget-tools.git
cd armenian-budget-tools
python -m venv .venv && source .venv/bin/activate
pip install -U -e ".[dev]"  # Installs package + pytest, pytest-cov, jupyter
pytest -q  # Verify setup
```

## Project Structure

Actual source organization:

```text
src/armenian_budget/
├── core/
│   ├── enums.py              # SourceType enum
│   ├── schemas.py            # Field definitions per source type
│   ├── utils.py              # Shared utilities (filename parsing)
│   └── query/                # MCP query engine
├── ingestion/
│   ├── parsers/
│   │   ├── _common.py        # ProcessingState, RowType enums
│   │   ├── excel_2019_2024.py
│   │   ├── excel_2025.py
│   │   └── excel_mtep.py     # MTEP parser (2-level hierarchy, JSON overall)
│   └── discovery.py          # File discovery
├── interfaces/
│   ├── cli/main.py           # CLI entrypoint
│   └── mcp/server.py         # MCP server
├── sources/
│   ├── registry.py           # Source URLs
│   ├── downloader.py
│   └── organizer.py
└── validation/
    ├── financial.py          # Production validation logic
    └── runner.py             # Validation orchestration

config/
├── sources.yaml              # Official source URLs and metadata
├── parsers.yaml              # Parser patterns and discovery rules
├── program_patterns.yaml     # Keyword patterns for MCP tools
└── checksums.yaml            # SHA-256 hashes for integrity verification

tests/
├── unit/
├── integration/
└── data_validation/
```

## Parser Implementation

### Understanding the State Machine

See `src/armenian_budget/ingestion/parsers/_common.py`:

- `ProcessingState` enum: INIT → READY → STATE_BODY → PROGRAM → SUBPROGRAM
- `RowType` enum: GRAND_TOTAL, STATE_BODY_HEADER, PROGRAM_HEADER, etc.

### Parser Examples

**Standard 3-level hierarchy (budget law, spending):**

- `excel_2019_2024.py` - State body → Program → Subprogram
- `excel_2025.py` - Same structure, extended program codes

**Different structure (MTEP):**

- `excel_mtep.py` - Only 2 levels (state body → program), no subprograms
- Returns JSON overall with `plan_years` array
- Different column names (y0/y1/y2 suffixes)

### Adding a New Source Type

**Example: MTEP was added with these steps:**

1. **Add to enum** (`core/enums.py`):

```python
class SourceType(str, Enum):
    # ... existing types ...
    MTEP = "MTEP"
```

2. **Create parser** (if new format needed):

```python
# src/armenian_budget/ingestion/parsers/excel_mtep.py
def flatten_mtep_excel(excel_file_path: str, *, year: int) -> tuple[pd.DataFrame, Dict, Dict, Dict]:
    # Custom row detection for MTEP format
    # Different column structure (y0, y1, y2)
    # Returns different overall format (JSON with plan_years)
```

3. **Update discovery** (`config/parsers.yaml`):

```yaml
mtep_patterns:
  - "միջնաժամկետ.*ծախսերի.*ծրագիր"
```

4. **Add tests** (`tests/`):

```python
def test_mtep_parsing(sample_mtep_file):
    df, overall, *_ = flatten_mtep_excel(sample_mtep_file, year=2024)
    assert len(df) > 0
    assert "plan_years" in overall
```

**Key insight:** If your data has a different structure (like MTEP), create a separate parser. Don't force it into existing parsers.

## Validation Framework

Production validation system with check registry, configurable tolerances, and structured reporting.

### Architecture

Four modules in `src/armenian_budget/validation/`:

- `config.py` - Tolerance constants (BUDGET_LAW_ABS_TOL=1.0, SPENDING_ABS_TOL=2000.0, MTEP_ABS_TOL=0.5) and severity rules
- `models.py` - CheckResult and ValidationReport dataclasses
- `registry.py` - Check orchestration via ALL_CHECKS list
- `checks/` - Individual check implementations (11 checks)

### Adding New Checks

1. Create `validation/checks/my_check.py` - see `hierarchical_structure_sanity.py` for pattern
2. Add severity config to `validation/config.py` _SEVERITY_MAP
3. Register in `validation/registry.py` ALL_CHECKS list
4. Write tests in `tests/validation/test_my_check.py`
5. Document in `docs/validation.md` and developer_guide.md

**Check interface** (convention-based, duck-typed):

- `validate(df, overall, source_type) -> List[CheckResult]` - run validation logic
- `applies_to_source_type(source_type) -> bool` - filter by data type

**Example:** See `validation/checks/hierarchical_totals.py` for multi-level check pattern.

### Configuration

```python
from armenian_budget.validation.config import get_tolerance_for_source, get_severity

tolerance = get_tolerance_for_source(SourceType.BUDGET_LAW)  # 1.0 AMD
severity = get_severity("hierarchical_totals", "program")    # "error"
```

See `validation/config.py` for all tolerance constants and severity maps.

### Validation vs Tests

**Validation** = Production code in `src/armenian_budget/validation/`

- Runs during data processing and on-demand
- Returns structured CheckResult and ValidationReport objects
- Configurable via config.py

**Tests** = Development verification in `tests/`

- Uses pytest framework
- Verifies both parsers AND validation logic

## Testing

```bash
# Run all tests
pytest

# Specific categories
pytest tests/unit/
pytest tests/integration/
pytest tests/data_validation/

# With coverage
pytest --cov=armenian_budget --cov-report=html

# Specific patterns
pytest -k budget_law
pytest -k spending
```

## CLI Reference

```bash
# Download and extract
armenian-budget download --years 2019-2024 --extract

# Process
armenian-budget process --years 2023
armenian-budget process --years 2023 --source-type BUDGET_LAW

# Validate (all source types or specific one)
armenian-budget validate --years 2023
armenian-budget validate --years 2023 --source-type BUDGET_LAW

# MCP server
armenian-budget mcp-server --data-path ./data/processed
```

## Python API Reference

> **Note:** The Python API is for internal library use only. The public interfaces are CLI and MCP server. This section documents internal functions for contributors and developers extending the system.

### Parsing

```python
from armenian_budget.ingestion.parsers import (
    flatten_budget_excel_2019_2024,
    flatten_budget_excel_2025,
    flatten_mtep_excel,
    SourceType
)

# Budget law 2019-2024
df, overall, rowtype_stats, statetrans_stats = flatten_budget_excel_2019_2024(
    path, SourceType.BUDGET_LAW
)

# MTEP
df, overall, rowtype_stats, statetrans_stats = flatten_mtep_excel(
    path, year=2024
)
# overall is Dict with "plan_years", "overall_total_y0", etc.
```

### Validation

**Run validation:**

```python
from armenian_budget.validation.registry import run_validation, print_report
from armenian_budget.core.enums import SourceType
from pathlib import Path

report = run_validation(year=2023, source_type=SourceType.BUDGET_LAW,
                       processed_root=Path("data/processed"))
print_report(report)  # Console output
```

**Check results:**

```python
if report.has_errors():
    errors = report.get_failed_checks(severity="error")
    # Process errors...
```

**Generate reports:**

```python
Path("report.md").write_text(report.to_markdown())
Path("report.json").write_text(report.to_json())
```

**Access config:**

```python
from armenian_budget.validation.config import get_tolerance_for_source, get_severity

tol = get_tolerance_for_source(SourceType.BUDGET_LAW)  # 1.0
sev = get_severity("hierarchical_totals", "program")   # "error"
```

See `validation/models.py` for ValidationReport methods, `validation/config.py` for all constants.

### Discovery

```python
from armenian_budget.ingestion.discovery import discover_best_file
from armenian_budget.core.enums import SourceType

file_info = discover_best_file(year=2023, source_type=SourceType.BUDGET_LAW)
```

## Common Development Tasks

### Debugging Parser Issues

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run parser with diagnostics
df, overall, rowtype_stats, statetrans_stats = flatten_budget_excel_2019_2024(path, source_type)

# Check row type distribution
print("Row types:", rowtype_stats)
print("State transitions:", statetrans_stats)
```

**Common issues:**

- Label mismatch → Adjust tolerance in `config/parsers.yaml`
- Missing columns → Check source type and year
- Hierarchical totals fail → Inspect `overall` vs row sums

## Code Quality

**Style:**

- Google Python Style Guide
- Docstrings for all public functions
- Type hints for parameters and returns
- Max line length: 100 characters

**Before committing:**

```bash
ruff check src/
black src/
pytest
```

## Contributing

**Branch naming:**

- `feature/add-new-parser`
- `bugfix/fix-label-matching`
- `docs/update-guide`

**PR checklist:**

- [ ] Tests pass (`pytest`)
- [ ] Code formatted (`ruff`, `black`)
- [ ] Docstrings updated
- [ ] Relevant docs updated (see CLAUDE.md for impact mapping)

**Documentation updates required when:**

- Architecture change → Update `architechture.md`
- Roadmap change → Update `roadmap.md`
- CLI commands change → Update README + this guide
- Python API changes → Update this guide
- Data schemas change → Update `data_schemas.md`
- MCP tools change → Update `mcp.md`

See `CLAUDE.md` for complete documentation governance and impact mapping.

## Type Definitions

```python
from armenian_budget.core.enums import SourceType

class SourceType(str, Enum):
    BUDGET_LAW = "BUDGET_LAW"
    SPENDING_Q1 = "SPENDING_Q1"
    SPENDING_Q12 = "SPENDING_Q12"
    SPENDING_Q123 = "SPENDING_Q123"
    SPENDING_Q1234 = "SPENDING_Q1234"
    MTEP = "MTEP"
```

---

**For detailed architecture** → See [`architecture.md`](architecture.md)
**For data schemas** → See [`data_schemas.md`](data_schemas.md)
**For MCP integration** → See [`mcp.md`](mcp.md)
