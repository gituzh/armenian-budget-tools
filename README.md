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
    - [Quick Reference](#quick-reference)
  - [Complete column reference](#complete-column-reference)
    - [Quick Column Overview](#quick-column-overview)
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
- What it does: Parses and validates Armenian state budget laws (2019–2025), spending reports (Q1/Q12/Q123/Q1234, 2019–2024 when available), and MTEP (mid‑term expenditure program, 2024 format), producing clean CSVs for analysis.
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
# overall contains total budget amount (float)
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

Create or edit `~/Library/Application Support/Claude/claude_desktop_config.json` with absolute paths:

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

# MTEP (2024 format)
armenian-budget process --year 2024 --source-type MTEP

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
# overall: summary totals from Excel (float for budget, dict for spending)
# rowtype_stats/statetrans_stats: parsing diagnostics
# See docs/data_schemas.md for detailed overall totals documentation
```

### Parse spending report

```python
from armenian_budget.ingestion.parsers import flatten_budget_excel_2019_2024, SourceType

df, overall, *_ = flatten_budget_excel_2019_2024(
    "./data/extracted/spending_reports/2019/Q1/file.xlsx", SourceType.SPENDING_Q1
)
# overall contains summary totals (annual plan, actual, execution rates)
```

### Parse budget law (2025)

```python
from armenian_budget.ingestion.parsers import flatten_budget_excel_2025

df, overall, *_ = flatten_budget_excel_2025(
    "./data/extracted/budget_laws/2025/file.xlsx"
)
# overall contains total budget amount (float)
```

### Discover input programmatically (optional)

```python
from armenian_budget.ingestion.discovery import discover_best_file
from armenian_budget.ingestion.parsers import flatten_budget_excel_2019_2024, SourceType

best = discover_best_file(year=2023, source_type=SourceType.BUDGET_LAW)
df, overall, *_ = flatten_budget_excel_2019_2024(best.path, SourceType.BUDGET_LAW)
# overall contains total budget amount (float)
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

For comprehensive information about data sources, schemas, and processing, see [`docs/data_schemas.md`](docs/data_schemas.md).

### Quick Reference

**Data roots:**

- `data/original`: downloaded archives
- `data/extracted`: unarchived source files
- `data/processed/csv`: processed outputs

**Dataset types:**

- `BUDGET_LAW`: Annual budget allocations (currently parses program summary)
- `SPENDING_Q1/Q12/Q123/Q1234`: Quarterly/half-year/annual spending reports

**Data structure:**
Each row represents one **subprogram** with aggregated totals from parent levels (program → state body) in a flattened structure for easy analysis.

**Key columns by source type:**

**BUDGET_LAW:**

- `subprogram_total`: allocated amount for subprogram
- `program_total`: total for program
- `state_body_total`: total for state body

**SPENDING reports:**

- `*_annual_plan`: original annual allocation
- `*_rev_annual_plan`: revised annual plan
- `*_actual`: actual spending year-to-date
- `*_actual_vs_rev_annual_plan`: execution rate vs revised annual plan (%)

_Note: `_`represents`state*body*`, `program*`, or `subprogram*` prefixes. For complete column reference and detailed schemas, see [`docs/data_schemas.md`](docs/data_schemas.md).\*"

## Complete column reference

For the complete column reference with detailed schemas, examples, and year-specific variations, see [`docs/data_schemas.md`](docs/data_schemas.md).

### Quick Column Overview

**Common columns (all source types):**
`state_body`, `program_code`, `program_name`, `program_goal`, `program_result_desc`, `subprogram_code`, `subprogram_name`, `subprogram_desc`, `subprogram_type`

**BUDGET_LAW key columns:**
`state_body_total`, `program_total`, `subprogram_total`

**SPENDING reports key columns:**
`*_annual_plan`, `*_rev_annual_plan`, `*_actual`, `*_actual_vs_rev_annual_plan`

_Note: Detailed CSV schemas and complete column definitions are available in [`docs/data_schemas.md`](docs/data_schemas.md)._

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
