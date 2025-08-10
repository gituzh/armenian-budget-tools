# Armenian State Budget Processor

A Python tool for processing and analyzing Armenian State Budget articles, converting them into easily analyzable CSV format.

## Overview

This tool helps process Armenian State Budget Excel files and converts them into structured CSV files, making it easier to analyze budget data. It's designed to handle the specific format of Armenian State Budget documents and extract relevant information into a clean, tabular format.

## Parsing architecture and API

The parsing layer lives under `src/armenian_budget/ingestion/parsers/` and follows the repository architecture in `docs/architecture.md`.

- Modules
  - `parsers/_common.py`: Shared types and helpers used by all parsers
    - `ProcessingState`, `RowType`
    - `is_numeric`, `normalize_str`
    - `get_expected_columns(source_type)`, `get_column_mappings(source_type, prefix)`
    - `sort_columns_by_excel_order(mappings)`
  - `parsers/excel_2019_2024.py`: Parser for 2019–2024 Excel format
    - `flatten_budget_excel_2019_2024(path, source_type)`
  - `parsers/excel_2025.py`: Parser for 2025 Excel format
    - `flatten_budget_excel_2025(path)`
  - `parsers/__init__.py`: Public API re-exports for convenient imports
  - `core/enums.py`: `SourceType` enum shared across the package

- Source types (`SourceType`)
  - `BUDGET_LAW` — 2019–2025
  - `SPENDING_Q1`, `SPENDING_Q12`, `SPENDING_Q123`, `SPENDING_Q1234` — 2019–2024 (when available)

- Public API (programmatic use)

```python
from armenian_budget.ingestion.parsers import (
    flatten_budget_excel_2019_2024,
    flatten_budget_excel_2025,
    SourceType,
)

# Budget law example (2019–2024 format)
df, overall, rowtype_stats, statetrans_stats = flatten_budget_excel_2019_2024(
    "./data/extracted/budget_laws/2023/file.xlsx", SourceType.BUDGET_LAW
)

# Spending Q1 example
df, overall, *_ = flatten_budget_excel_2019_2024(
    "./data/extracted/spending_reports/2019/Q1/file.xlsx", SourceType.SPENDING_Q1
)

# Budget law 2025 format
df, overall, *_ = flatten_budget_excel_2025(
    "./data/extracted/budget_laws/2025/file.xlsx"
)

# Notes:
# - df: flattened subprogram-level DataFrame with dynamic columns based on source_type
# - overall: dict with grand/overall totals (e.g., {"overall_total": 123.45})
# - rowtype_stats, statetrans_stats: parsing diagnostics (enum-keyed dicts)
```

- CLI integration
  - The CLI `process` command uses these functions directly; discovery runs automatically when `--input` is not provided.
  - `--auto` is deprecated and kept only for backward compatibility.
  - Examples are in the Usage section; both manual `--input` and automatic discovery are supported.

- Output columns by source type (subprogram grain)
  - `BUDGET_LAW`: totals only
    - `subprogram_total` (+ `program_total`, `state_body_total` propagated into rows)
  - `SPENDING_Q1`, `SPENDING_Q12`, `SPENDING_Q123`:
    - plans: `*_annual_plan`, `*_rev_annual_plan`, `*_period_plan`, `*_rev_period_plan`
    - actuals: `*_actual`
    - percentages: `*_actual_vs_rev_annual_plan`, `*_actual_vs_rev_period_plan`
  - `SPENDING_Q1234`:
    - plans: `*_annual_plan`, `*_rev_annual_plan`
    - actuals: `*_actual`
  - Column prefixes are role-based per level: `state_body_`, `program_`, `subprogram_`.

- Column mapping helpers (no normalization enforced)
  - Use `get_column_mappings(source_type, prefix)` to derive the expected measure columns for a level.
  - Examples:
    - `get_column_mappings(SourceType.BUDGET_LAW, "subprogram_") -> {"subprogram_total": 3}`
    - `get_column_mappings(SourceType.SPENDING_Q1, "program_") -> {"program_annual_plan": 3, ...}`

- Format differences handled
  - 2019–2024: four primary columns drive the state machine; program/subprogram detail labels are validated
  - 2025: layout changes (e.g., totals in column 6, `program_code_ext` parsed from dashed code)

- Error handling and logging
  - The parsers log detailed progress including row type detection and state transitions when verbose logging is enabled.
  - Certain structural violations (e.g., missing labels) cause an immediate exit for strictness.

- Discovery integration
  - The discovery step (`armenian_budget.ingestion.discovery.discover_best_file`) finds the best candidate workbook under `data/extracted/...` using `config/parsers.yaml` patterns.
  - The CLI `process --auto` calls discovery first, then passes the path to the appropriate parser based on year and source type.

- Backward compatibility
  - New code should import from `armenian_budget.ingestion.parsers`.
  - Legacy imports via `from budget import ...` are being phased out. Update to the new import path for reliability.

### Maintainers: extending/adjusting parsers

- Add or adjust label tolerance and patterns via `config/parsers.yaml` for discovery.
- For 2019–2024 shape changes:
  - Update `_detect_row_type_2019_2024`, `_collect_details_2019_2024`, or `_common.py` helpers as needed.
  - Keep `get_column_mappings` aligned with real column positions per source type.
- For 2025+
  - Extend `excel_2025.py` (or add new year-specific module if the format changes materially).
- Prefer vectorized operations; avoid row-by-row loops in the main data path.

## Features

- Process Armenian State Budget Excel files
- Flatten multi-level budget structure into a single table
- Extract state body, program, and subprogram information
- Generate easily analyzable CSV datasets
- Support for different budget years

## Requirements

- Python 3.10 or higher
- Required Python packages (see `requirements.txt`)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/gituzh/budget-am.git
cd budget-am
```

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
# or
.\venv\Scripts\activate  # On Windows
```

1. Install the required packages (dev install):

```bash
pip install -U -e .
```

## Extraction prerequisites (for spending reports)

Spending report archives are distributed as `.rar` files. Extraction is optional but recommended to process files.

- Default extractor: `unar`
- Fallback extractor: `unrar`
- If neither is available, downloads still succeed but extraction is skipped with a warning.

Install `unar` (recommended):

- macOS (Homebrew):

```bash
brew install unar
```

- Ubuntu/Debian:

```bash
sudo apt update && sudo apt install -y unar
```

- Arch Linux:

```bash
sudo pacman -S unar
```

Optional fallback (`unrar`):

- macOS (Homebrew):

```bash
brew install unrar
```

- Ubuntu/Debian:

```bash
sudo apt update && sudo apt install -y unrar || sudo apt install -y unrar-free
```

Verify installation:

```bash
unar --version  # preferred
# or
unrar
```

Extraction behavior:

- Spending archives extract to `data/extracted/spending_reports/{year}/Q*/{archive_name}`
- Existing non-empty target directories are left untouched (no overwrite)
- To re-extract, delete the target directory first, then re-run with `--extract`

## Usage

Legacy script (backward compatible):

```bash
python extract_budget_articles.py
```

Prefer the CLI for new workflows. Outputs default to `./data/processed/csv`.

CLI (download and extract) — URLs configured in `config/sources.yaml`:

```bash
armenian-budget download --years 2019-2024 --extract
```

- `--extract` will use `unar` by default, `unrar` as fallback
- If neither extractor is available, you will see a warning and archives will remain under `data/original/spending_reports/{year}`

Extract separately (without downloading again):

```bash
armenian-budget extract --years 2019-2024
# or auto-detect available years from data/original
armenian-budget extract
```

Process datasets (CSV + overall JSON):

```bash
# All sources for a year (defaults: output → ./data/processed/csv, discovery if no --input)
armenian-budget process --year 2019

# Single source type
armenian-budget process --year 2019 --source-type BUDGET_LAW

# Multiple years (comma-separated or range)
armenian-budget process --years 2019,2020,2021
armenian-budget process --years 2019-2021

# Explicit input (requires single --year and --source-type)
armenian-budget process --year 2023 --source-type BUDGET_LAW \
  --input ./data/extracted/budget_laws/2023/file.xlsx

# Advanced discovery knobs
armenian-budget process --year 2023 --source-type BUDGET_LAW \
  --deep-validate --dest-root ./data --parsers-config ./config/parsers.yaml

# Logging: show only warnings and errors
armenian-budget --warnings-only process --year 2023

# Logging: show only errors
armenian-budget --errors-only process --year 2023

# Save end-of-run report to JSON
armenian-budget process --years 2019-2025 \
  --report-json ./data/processed/processing_report.json

# Example report JSON (truncated)
[
  {"year": 2024, "source": "SPENDING_Q1234", "status": "FAIL", "reason": "discovery: No .xls/.xlsx candidates found for 2024 SPENDING_Q1234 under [...]"},
  {"year": 2025, "source": "BUDGET_LAW", "status": "OK", "reason": ""}
]
```

Process defaults and behavior:

- Output directory default: `./data/processed/csv` (override with `--out`)
- If `--source-type` is omitted, all supported source types are processed
- If `--input` is omitted, discovery is automatic
- If `--input` is provided: require a single `--year` and a single `--source-type`
- `--auto` is deprecated; do not use (kept for backward compatibility)
- End-of-run report: prints `YYYY SOURCE: OK` or `YYYY SOURCE: FAIL (reason)`; save with `--report-json <path>`
- Global flags are passed before the subcommand, e.g. `armenian-budget --warnings-only process --year 2023`

Validate a produced CSV (minimal checks):

```bash
armenian-budget validate --csv ./data/processed/csv/2023_BUDGET_LAW.csv
```

Downloader and checksums:

- Files are saved to:
  - Spending: `data/original/spending_reports/{year}/Q*/<file>`
  - Budget laws: `data/original/budget_laws/{year}/<file>`
- After each successful download, SHA-256 is recorded to `config/checksums.yaml` with fields: `name, year, source_type, url, checksum, checksum_updated_at` (UTC ISO).
- If a checksum is specified in config for a URL, the `.part` file is verified before moving into place. On mismatch, the `.part` is deleted and an error is logged.
- Unchanged files do not produce duplicate checksum entries; the "checksums recorded" count will be 0 when nothing changed.

Sources configuration notes (`config/sources.yaml`):

- `file_format` is optional and overrides the extension inferred from the URL when provided.
- Quarter subfolders (Q1/Q12/Q123/Q1234) are derived from `source_type`.

### Discovery (config-driven)

Automatically find the correct workbook inside extracted archives and cache the mapping so you don’t maintain file paths manually.

- Index location: `data/extracted/discovery_index.json`
- Key format: `"{year}/{source_type}"`, e.g. `"2019/spending_q1234"`
- Default behavior: no parsing; picks best-scored match by regex and file heuristics
- Optional: `--deep-validate` to probe-parse top candidates (slower)

Config patterns (`config/parsers.yaml`):

```yaml
parsers:
  budget_law:
    search:
      global:
        regex: "(?i)(?=.*ծրագիր)(?=.*միջոցառում).*\\.(xlsx|xls)$"

  spending:
    search:
      global:
        regex: "(?i)(?=.*ծրագիր)(?=.*միջոցառում).*\\.(xlsx|xls)$"
      by_year:
        "2019":
          regex: "(?i)(?=.*crag)(?=.*mij).*\\.(xlsx|xls)$"
        "2019/Q1234":
          regex: "(?i)(?=.*ծրագ)(?=.*միջոց).*\\.(xlsx|xls)$"
```

Pattern precedence:

- Exact year + quarter (e.g., `2019/Q1234`) > exact year (e.g., `2019`) > global

Search roots:

- Budget laws: `data/extracted/budget_laws/{year}/**/*.{xls,xlsx}`
- Spending: `data/extracted/spending_reports/{year}/{Q*}/**/*.{xls,xlsx}`

CLI usage:

```bash
# Build/refresh the index (no parsing by default)
armenian-budget discover --years 2019-2024 --dest-root ./data --parsers-config ./config/parsers.yaml

# Force re-discovery even if cached
armenian-budget discover --years 2019 --force-discover

# Validate candidates by briefly parsing (slower, optional)
armenian-budget discover --years 2019 --deep-validate

# Process using the discovered input automatically (no --auto needed)
armenian-budget process \
  --year 2023 --source-type BUDGET_LAW \
  --dest-root ./data --parsers-config ./config/parsers.yaml

# Manual override always works
armenian-budget process --year 2023 --source-type BUDGET_LAW \
  --input ./data/extracted/budget_laws/2023/file.xlsx
```

Index entry example:

```json
{
  "2019/spending_q1234": {
    "path": "data/extracted/spending_reports/2019/Q1234/...xlsx",
    "matched_by": "2019/Q1234",
    "pattern": "(?i)(?=.*ծրագ)(?=.*միջոց).*\\.(xlsx|xls)$",
    "mtime": 1587480062.0,
    "size": 497381,
    "checksum": "sha256:...",
    "discovered_at": "2025-01-15T10:21:33Z"
  }
}
```

Troubleshooting:

- If nothing is found, ensure you have extracted archives into `data/extracted/...`
- Adjust regex patterns in `config/parsers.yaml` (use `--force-discover` after changes)
- Use `--deep-validate` for stricter matching when filenames are ambiguous

Run the minimal MCP server (stdio):

```bash
armenian-budget mcp-server --data-path ./data/processed
```

Run over HTTP (for Claude Desktop custom connector):

```bash
armenian-budget mcp-server --data-path ./data/processed --host 127.0.0.1 --port 8765
```

Run over HTTPS (Claude often requires TLS for remote connectors):

```bash
# 1) Generate a local dev cert (one-time):
brew install mkcert && mkcert -install
mkdir -p config/certs && cd config/certs && mkcert localhost && cd -

# This creates config/certs/localhost.pem and config/certs/localhost-key.pem

# 2) Start HTTPS server
armenian-budget mcp-server --data-path ./data/processed \
  --host 127.0.0.1 --port 8765 --https \
  --certfile config/certs/localhost.pem --keyfile config/certs/localhost-key.pem
```

## Testing

To run the test suite:

```bash
pytest
```

For more detailed test output, you can use:

```bash
pytest -v
```

To run tests with coverage report:

```bash
pytest --cov=.
```

### Test the MCP server

- Smoke test via Python (optional):

```bash
python - <<'PY'
import asyncio
from armenian_budget.interfaces.mcp import server as srv

async def main():
    inv = await srv.list_available_data()
    print('inventory keys:', sorted(inv.keys()))
    schema = await srv.get_data_schema(2023, 'BUDGET_LAW')
    print('schema cols:', len(schema['columns']))
    path = await srv.filter_budget_data(2023, 'BUDGET_LAW', min_amount=1.0)
    print('filtered path exists:', __import__('os').path.exists(path))
asyncio.run(main())
PY
```

- Run with MCP Inspector (recommended):
  - Requires Node.js. Launch the inspector and point it at this server command.

```bash
npx @modelcontextprotocol/inspector
# Add a server → Command: ./venv/bin/armenian-budget
# Args: mcp-server --data-path ./data/processed
```

You should see the tools listed:

- list_available_data
- get_data_schema
- filter_budget_data
- get_ministry_spending_summary
- find_program_across_years_robust
- search_programs_by_similarity
- trace_program_lineage
- register_program_equivalency
- get_program_equivalencies
- detect_program_patterns
- bulk_filter_multiple_datasets
- extract_rd_budget_robust

Key notes:

- `detect_program_patterns` loads patterns from YAML only (no hardcoded defaults). See Configuration below.
- `register_program_equivalency` persists manual mappings to YAML; `get_program_equivalencies` reads them.
- `extract_rd_budget_robust` aggregates R&D across ministries using pattern matching, lineage and manual mappings with confidence flags.

## Validation rules and behavior

- Financial totals consistency:
  - Budget Law: strict equality across hierarchy (state_body = sum(programs) = sum(subprograms)).
  - Spending reports: supports multi-section state bodies; compares sum of distinct state-body totals to de-duplicated program totals and subprogram sums; small absolute tolerance applied.
- Logical relationships (Spending):
  - period_plan ≤ annual_plan; if revised columns exist and satisfy rev_period ≤ rev_annual, violations are warnings; negatives also downgraded to warnings.
  - rev_period_plan ≤ rev_annual_plan: errors for non-negative values; warnings when negatives present.
- Percentage ranges:
  - Negative percentages: errors.
  - >1 (overspend): warnings with examples.
- Percentage calculations (Spending):
  - actual_vs_rev_annual_plan should equal actual / rev_annual_plan. Detailed failures list offending rows with identifiers and numbers.
- Data quality:
  - Missing required columns and nulls: errors.
  - Negative financial values: warnings with examples (except state body totals in Budget Law which fail).

## Run tests

Always use the project venv.

```bash
source venv/bin/activate  # macOS/Linux
pytest -q                 # run all tests
pytest -q -k spending     # run spending tests
```

## Documentation

- Architecture: `docs/architecture.md`
- Product Requirements: `docs/prd.md`
- Roadmap: `docs/roadmap.md`

### Configuration for MCP advanced tools

- Program pattern definitions (consumed by `detect_program_patterns`):
  - File: `config/program_patterns.yaml`
  - Structure:

```yaml
patterns:
  research:
    keywords: ["գիտական", "հետազոտ", "փորձակոնստրուկտոր", "ինովա", "տեխնոլոգ"]
    required_keywords: ["գիտական", "հետազոտ"]
    exclude_keywords: ["կրթական", "հիմնական"]
  education:
    keywords: ["կրթություն", "ուսում", "դպրոց", "համալսարան"]
    required_keywords: ["կրթություն"]
    exclude_keywords: []
```

- Manual program equivalency mappings (used by `register_program_equivalency`, read by `get_program_equivalencies` and `extract_rd_budget_robust`):
  - File: `config/program_equivalencies.yaml`
  - Structure (example):

```yaml
equivalencies:
  rd_research:
    description: "Manual equivalency for MinESCS R&D lineage"
    created_at: "2025-02-01T12:00:00Z"
    mappings:
      - {year: 2019, ministry: "ԿԳՄՍ", program_code: 1162}
      - {year: 2021, ministry: "ԿԳՄՍ", program_code: 1163}
```

### Example MCP calls (Inspector)

In MCP Inspector, try:

```json
{"tool": "detect_program_patterns", "params": {"pattern_type": "research", "years": [2021,2022,2023], "confidence_threshold": 0.75}}
```

```json
{"tool": "find_program_across_years_robust", "params": {"reference_year": 2019, "reference_program_code": 1162, "search_years": [2020,2021,2022,2023,2024]}}
```

```json
{"tool": "extract_rd_budget_robust", "params": {"years": [2019,2020,2021,2022,2023,2024,2025], "return_details": true}}
```

### MCP tools (brief reference)

- list_available_data: Inventory and diagnostics of processed datasets
- get_data_schema: Columns, dtypes, shape, file path for a dataset
- filter_budget_data: Filter a dataset; returns path to a temporary CSV
- get_ministry_spending_summary: Aggregates and top programs for a ministry
- find_program_across_years_robust: Multi-signal program matching across years
- search_programs_by_similarity: Fuzzy search on Armenian name/goal/description
- trace_program_lineage: Build a timeline of a program’s evolution with confidence
- register_program_equivalency: Save manual cross-year mappings (YAML)
- get_program_equivalencies: Read manual mappings (YAML)
- detect_program_patterns: YAML-driven keyword pattern detection across years
- bulk_filter_multiple_datasets: Apply filters over many years/types; combine to CSV
- extract_rd_budget_robust: End-to-end R&D budget extraction with confidence flags

## MCP integration (Claude Desktop and ChatGPT)

- Claude Desktop (macOS):
  - Option A: Local process (stdio) via config file — Create or edit `~/Library/Application Support/Claude/claude_desktop_config.json` with:

```json
{
  "mcpServers": {
    "budget-am": {
      "command": "./venv/bin/armenian-budget",
      "args": [
        "mcp-server",
        "--data-path",
        "./data/processed"
      ],
      "env": {}
    }
  }
}
```

- Restart Claude Desktop. In a new chat, the `budget-am` tools will be available. Ask things like: “Run tool list_available_data”, “Show schema for 2023 budget law”, “Filter 2023 budget law for Ministry of Education with min amount 1e6”.

- Option B: Remote connector (HTTP) — Use Claude’s “Add custom connector” and set:
  - Name: budget-am
  - Remote MCP server URL: `https://127.0.0.1:8765`
  - First, start the server: `armenian-budget mcp-server --data-path ./data/processed --host 127.0.0.1 --port 8765 --https`

- ChatGPT: The web app does not natively support local MCP servers. You can use the official MCP Inspector to proxy interactions during development, or third-party MCP bridges when available. ChatGPT Desktop (if/when it supports MCP) can be configured similarly by spawning the same command.

## Changelog (recent)

- Added minimal MCP server with tools: `list_available_data`, `get_data_schema`, `filter_budget_data`, `get_ministry_spending_summary`.
- New CLI command: `armenian-budget mcp-server`.
- Enhanced CLI: `download`, `extract`, `discover`, `process`, `validate` (with `--deep-validate` for discovery/process auto).
- Dependencies updated: added `mcp` (Python SDK).
- Checksums now recorded to `config/checksums.yaml` during downloads.

## Output Format

The generated CSV files will contain the following columns:

- State Body (Պետական մարմին)
- State Body Total (Ընդամենը պետական մարմնի համար)
- Program Code (Ծրագրի կոդ)
- Program Code Extended (Ծրագրի կոդ երկարացված)
- Program Name (Ծրագրի անվանում)
- Program Goal (Ծրագրի նպատակ)
- Program Result Description (Ծրագրի արդյունքի նկարագրություն)
- Program Total (Ընդամենը ծրագրի համար)
- Subprogram Code (Ենթածրագրի կոդ)
- Subprogram Name (Ենթածրագրի անվանում)
- Subprogram Description (Ենթածրագրի նկարագրություն)
- Subprogram Type (Ենթածրագրի տեսակ)
- Subprogram Total (Ընդամենը ենթածրագրի համար)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
