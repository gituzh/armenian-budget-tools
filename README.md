# Armenian State Budget Tools

Parse, validate, and analyze Armenian state budget laws and spending reports. Outputs clean, analysis-ready CSVs.

## Table of Contents

- [Armenian State Budget Tools](#armenian-state-budget-tools)
  - [Table of Contents](#table-of-contents)
  - [At a glance](#at-a-glance)
  - [Quickstart](#quickstart)
    - [Analysts (Excel/BI)](#analysts-excelbi)
    - [CLI users](#cli-users)
    - [Python API](#python-api)
    - [MCP server](#mcp-server)
  - [Installation](#installation)
  - [Usage — CLI](#usage--cli)
    - [Data setup: download, extract, discover](#data-setup-download-extract-discover)
    - [Process datasets](#process-datasets)
    - [Validate outputs](#validate-outputs)
    - [Defaults and behavior](#defaults-and-behavior)
    - [Logging filters (optional)](#logging-filters-optional)
    - [Provenance and integrity](#provenance-and-integrity)
  - [Usage — Python API](#usage--python-api)
    - [Parse budget law (2019–2024)](#parse-budget-law-20192024)
    - [Parse spending report](#parse-spending-report)
    - [Parse budget law (2025)](#parse-budget-law-2025)
    - [Discover input programmatically (optional)](#discover-input-programmatically-optional)
  - [Configuration](#configuration)
  - [Data locations and column roles](#data-locations-and-column-roles)
  - [Troubleshooting](#troubleshooting)
  - [Known issues](#known-issues)
  - [Contributing](#contributing)
  - [Testing](#testing)
  - [Changelog](#changelog)
  - [License](#license)
  - [Further reading](#further-reading)

## At a glance

- Who it’s for:
  - Analysts using Excel/BI
  - Developers/data scientists using Python/Wolfram
  - Auditors who need source traceability
  - Users who prefer AI‑assisted analysis via the MCP server
- What it does: Parses and validates Armenian state budget laws (2019–2025) and spending reports (Q1/Q12/Q123/Q1234, 2019–2024 when available), producing clean CSVs for analysis.
- Where outputs go:
  - `data/original` (downloaded)
  - `data/extracted` (unarchived)
  - `data/processed/csv` (results)
  - Optional end‑of‑run JSON report and recorded checksums for provenance
- Why trust it: Deterministic, validation‑first processing with clear warnings vs errors, tolerance‑aware checks, discovery index for input selection, and traceability to original files.

## Quickstart

### Analysts (Excel/BI)

- Open [processed CSVs](./data/processed/csv/) directly in your tool of choice.
- Example paths: `./data/processed/csv/2023_BUDGET_LAW.csv`, `./data/processed/csv/2021_SPENDING_Q12.csv`
- For schema/columns, see [Data locations and column roles](#data-locations-and-column-roles).

### CLI users

1. Create and activate a virtual environment, then install the package.

```bash
python -m venv venv
source venv/bin/activate
pip install -U -e .
```

1. Process a year (uses discovery when inputs exist under `./data/extracted`).

```bash
armenian-budget process --year 2023
```

1. Find outputs in `./data/processed/csv`.

- Need to fetch and extract official files first? See [Usage — CLI](#usage--cli).

### Python API

After installation and venv activation, use the parsers directly:

```python
from armenian_budget.ingestion.parsers import (
    flatten_budget_excel_2019_2024,
    flatten_budget_excel_2025,
    SourceType,
)

# Budget law (2019–2024 format)
df, overall, *_ = flatten_budget_excel_2019_2024(
    "./data/extracted/budget_laws/2023/file.xlsx", SourceType.BUDGET_LAW
)
```

- More examples: see [Usage — Python API](#usage--python-api).

### MCP server

1. Create and activate a virtual environment, then install the package.

```bash
python -m venv venv
source venv/bin/activate
pip install -U -e .
```

1. Claude Desktop (local stdio) — add a server configuration.

Create or edit `"~/Library/Application Support/Claude/claude_desktop_config.json"` with absolute paths:

```json
{
  "mcpServers": {
    "budget-am": {
      "command": "/absolute/path/to/repo/venv/bin/armenian-budget",
      "args": [
        "mcp-server",
        "--data-path",
        "/absolute/path/to/repo/data/processed"
      ],
      "env": {}
    }
  }
}
```

1. Restart Claude Desktop, start a new chat, and use the tools (e.g., “Run tool list_available_data”).

1. Optional: run the server directly from a shell.

```bash
armenian-budget mcp-server --data-path ./data/processed
```

- More: see `docs/mcp.md` for resources, tools, and HTTP/HTTPS options.

#### New query tooling (safe-by-default)

- Use these tools to explore and query without overwhelming the LLM context:
  - `get_catalog(years?, source_types?)` → inventory with approximate row counts and file sizes
  - `get_schema(year, source_type)` → columns, dtypes, roles, shape, and sample rows
  - `distinct_values(year, source_type, column, limit?, min_count?)` → frequent values for building filters
  - `estimate_query(year, source_type, columns?, filters?, group_by?, aggs?, distinct?)` → row/byte estimate and tiny preview
  - `query_data(year, source_type, ..., output_format='json'|'csv'|'parquet', limit?, offset?, max_rows?, max_bytes?)` → inline JSON for small results; otherwise a temp file path (Parquet preferred, CSV fallback)

- Size/format policy:
  - JSON is only for previews and small results (caps enforced).
  - Large results are written to `data/processed/tmp` as Parquet by default (CSV fallback) and returned as a file path.
  - Pagination/handles will be added in a later phase; for now, use `limit`/`offset`.

- Deprecations:
  - Heavy tools that previously streamed large JSON may be internally routed through the new estimator and capped; prefer the new query tools.
- More integration details and HTTPS setup: see [Further reading](#further-reading).

## Installation

Requirements:

- Python 3.10+
- macOS/Linux supported; Windows best‑effort
- Optional (for spending report extraction): `unar` recommended, `unrar` fallback

1. Clone the repository.

```bash
git clone https://github.com/gituzh/budget-am.git
cd budget-am
```

1. Create and activate a virtual environment.

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# On Windows: .\\venv\\Scripts\\activate
```

1. Install in editable mode.

```bash
pip install -U -e .
```

1. Verify the CLI entrypoint.

```bash
armenian-budget --help | head -n 5
```

Optional extractors (for `.rar` archives used by spending reports):

- macOS (Homebrew):

```bash
brew install unar  # preferred
brew install unrar # optional fallback
```

- Ubuntu/Debian:

```bash
sudo apt update && sudo apt install -y unar
sudo apt install -y unrar || sudo apt install -y unrar-free
```

- Arch Linux:

```bash
sudo pacman -S unar
```

## Usage — CLI

### Data setup: download, extract, discover

- Download official sources configured in `config/sources.yaml` and extract archives when available.

```bash
# Download and extract for a range of years
armenian-budget download --years 2019-2024 --extract
# With explicit roots
armenian-budget download --years 2019-2024 --original-root ./data/original --extracted-root ./data/extracted --extract

# Extract only (if files already exist under data/original)
armenian-budget extract --years 2019-2024
armenian-budget extract  # auto-detect available years

# Build/refresh discovery index (maps year/source → best workbook)
armenian-budget discover --years 2019-2024 --extracted-root ./data/extracted --parsers-config ./config/parsers.yaml
```

### Process datasets

```bash
# All sources for a year (outputs → ./data/processed/csv)
armenian-budget process --year 2019

# Single source type
armenian-budget process --year 2019 --source-type BUDGET_LAW

# Multiple years (comma-separated or range)
armenian-budget process --years 2019,2020,2021
armenian-budget process --years 2019-2021

# Explicit input (requires single --year and --source-type). When --input is provided,
# discovery is bypassed and --extracted-root is ignored.
armenian-budget process --year 2023 --source-type BUDGET_LAW \
  --input ./data/extracted/budget_laws/2023/file.xlsx

# Advanced discovery knobs
armenian-budget process --year 2023 --source-type BUDGET_LAW \
  --deep-validate --extracted-root ./data/extracted --parsers-config ./config/parsers.yaml \
  --processed-root ./data/processed
```

### Validate outputs

```bash
# Minimal checks for a produced CSV
armenian-budget validate --csv ./data/processed/csv/2023_BUDGET_LAW.csv
```

Note: Validation via the CLI is currently minimal and not fully implemented. For comprehensive data checks, run the test suite with pytest (see [Testing](#testing)).

### Defaults and behavior

- Processed outputs default root: `./data/processed` (CSV under `csv/`). Override with `--processed-root`.
- When `--source-type` is omitted, all supported source types are processed
- When `--input` is omitted, discovery is automatic (uses `--extracted-root`, default `./data/extracted`).
- When `--input` is provided, `--extracted-root` is ignored for discovery.
- `--auto` is deprecated; do not use (kept for backward compatibility)
- End-of-run report: prints statuses; save with `--report-json <path>`

### Logging filters (optional)

```bash
armenian-budget --warnings-only process --year 2023
armenian-budget --errors-only process --year 2023
```

### Provenance and integrity

- Discovery index: `<extracted-root>/discovery_index.json` (maps year/source → input path)
- Checksums: recorded in `./config/checksums.yaml` after downloads
- End-of-run processing report (optional): `--report-json ./data/processed/processing_report.json`

## Usage — Python API

All examples assume the project is installed in a virtual environment.

### Parse budget law (2019–2024)

```python
from armenian_budget.ingestion.parsers import (
    flatten_budget_excel_2019_2024,
    SourceType,
)

df, overall, rowtype_stats, statetrans_stats = flatten_budget_excel_2019_2024(
    "./data/extracted/budget_laws/2023/file.xlsx", SourceType.BUDGET_LAW
)

# df: flattened subprogram-level DataFrame
# overall: dict with overall totals (e.g., {"overall_total": 123.45})
# rowtype_stats/statetrans_stats: parsing diagnostics
```

### Parse spending report

```python
from armenian_budget.ingestion.parsers import flatten_budget_excel_2019_2024, SourceType

df, overall, *_ = flatten_budget_excel_2019_2024(
    "./data/extracted/spending_reports/2019/Q1/file.xlsx", SourceType.SPENDING_Q1
)
```

### Parse budget law (2025)

```python
from armenian_budget.ingestion.parsers import flatten_budget_excel_2025

df, overall, *_ = flatten_budget_excel_2025(
    "./data/extracted/budget_laws/2025/file.xlsx"
)
```

### Discover input programmatically (optional)

```python
from armenian_budget.ingestion.discovery import discover_best_file
from armenian_budget.ingestion.parsers import flatten_budget_excel_2019_2024, SourceType

best = discover_best_file(year=2023, source_type=SourceType.BUDGET_LAW)
df, overall, *_ = flatten_budget_excel_2019_2024(best.path, SourceType.BUDGET_LAW)
```

For column roles and structures by source type, see [Data locations and column roles](#data-locations-and-column-roles).

## Configuration

- `config/sources.yaml`: official sources and URLs
  - `file_format` optionally overrides extension inferred from URL
  - Quarter subfolders (Q1/Q12/Q123/Q1234) are derived from `source_type`
- `config/parsers.yaml`: discovery patterns and optional per-year overrides
  - Pattern precedence: exact `year/quarter` > exact `year` > global
  - Use `--deep-validate` during discover/process for stricter matching
- `config/program_patterns.yaml`: keyword patterns consumed by MCP tools
- `config/program_equivalencies.yaml`: manual cross-year program mappings used by MCP tools
- `config/checksums.yaml`: recorded SHA-256 for downloads

## Data locations and column roles

Data roots:

- `data/original`: downloaded files
- `data/extracted`: unarchived workbooks
- `data/processed/csv`: processed outputs

Dataset types (source types):

- `BUDGET_LAW`: Annual appropriations from the official budget law. Represents planned allocations for the full fiscal year at subprogram level (the legal baseline before any in‑year revisions).
- `SPENDING_Q1`: Year‑to‑date execution after the first quarter (Q1). Includes the original plan, any in‑year revised plan as of Q1, and actual execution to date.
- `SPENDING_Q12`: Year‑to‑date execution after the second quarter (Q1–Q2, half‑year).
- `SPENDING_Q123`: Year‑to‑date execution after the third quarter (Q1–Q3).
- `SPENDING_Q1234`: Final year‑end execution (Q1–Q4). Often reflects the final revised plan and the actuals for the full year.

Column roles by source type (subprogram grain):

- BUDGET_LAW: allocated → `subprogram_total`
- SPENDING_Q1, SPENDING_Q12, SPENDING_Q123:
  - allocated → `subprogram_annual_plan`
  - revised → `subprogram_rev_annual_plan`
  - actual → `subprogram_actual`
  - execution_rate → `subprogram_actual_vs_rev_annual_plan`
- SPENDING_Q1234:
  - allocated → `subprogram_annual_plan`
  - revised → `subprogram_rev_annual_plan`
  - actual → `subprogram_actual`

## Troubleshooting

- Discovery finds nothing: ensure archives are extracted under `./data/extracted/...`; try `--force-discover` or `--deep-validate`.
- Extractor missing: install `unar` (preferred) or `unrar`; see Installation.
- Wrong `--year`/`--input` combo: explicit `--input` requires a single `--year` and `--source-type`.
- Checksum mismatch on download: the partial file is removed and retried; verify URL and network.
- Validation failures: see which rule failed; for full checks run [Testing](#testing).
- MCP can’t see data: confirm `--data-path ./data/processed` and that CSVs exist.

## Known issues

- Some automated tests are currently failing. This may reflect intentional behavior changes or data edge cases, but requires review. Track failures using `pytest -q -k <pattern>` and prioritize by impact.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Testing

Always use the project venv.

```bash
source venv/bin/activate
pytest -q                 # run all tests
pytest -q -k spending     # run spending tests only
pytest --cov=.            # coverage
```

Comprehensive data validations currently live in the test suite. Use these tests for full checks until the CLI `validate` command is expanded.

For test structure, fixtures, and tips, see `tests/README.md`.

## Changelog

See `CHANGELOG.md` for recent updates.

## License

MIT License — see `LICENSE`.

## Further reading

- Architecture: `docs/architecture.md`
- MCP server: `docs/mcp.md`
- Product Requirements: `docs/prd.md`
- Roadmap: `docs/roadmap.md`
