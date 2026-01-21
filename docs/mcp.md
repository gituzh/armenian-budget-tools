# MCP Server

> ⚠️ **DEPRECATION NOTICE**: The MCP server is currently broken and will be either fixed in a future release or removed entirely in favor of a Agent Skill implementation. This documentation is kept for reference purposes only.

This project exposes a Model Context Protocol (MCP) server that provides direct access to processed Armenian budget datasets and higher-level analysis utilities.

The server offers:

- Addressable resources via URI templates that return CSV content directly
- Tools for schema/query/aggregation/analysis, returning JSON or CSV text

## Quick Setup

### Option 1: Claude Desktop (Recommended)

1. **Clone and setup:**

   ```bash
   git clone https://github.com/gituzh/armenian-budget-tools.git
   cd armenian-budget-tools
   python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -U -e .
   ```

2. **Download and process data:**

   ```bash
   armenian-budget download --years 2019-2024 --extract
   armenian-budget process --years 2019-2024
   ```

3. **Add to Claude Desktop config:**

   **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

   **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

   ```json
   {
     "mcpServers": {
       "armenian-budget": {
         "command": "python",
         "args": ["-m", "armenian_budget.interfaces.mcp.server"],
         "cwd": "/absolute/path/to/armenian-budget-tools",
         "env": {
           "ARMENIAN_BUDGET_DATA_PATH": "/absolute/path/to/armenian-budget-tools/data/processed"
         }
       }
     }
   }
   ```

   **Note**: Use absolute paths for both `cwd` and `ARMENIAN_BUDGET_DATA_PATH`

4. **Restart Claude Desktop** - Server will start automatically

### Option 2: Command Line (Testing)

## Protocol and runtime

- Transport: stdio (default), HTTP, or HTTPS
- Runtime: Python, using `mcp`'s `FastMCP`
- Dependencies: `mcp` (required), `rapidfuzz` (optional; improves Armenian text similarity), `uvicorn` (only for HTTP/HTTPS)

## Running the server

Stdio (recommended for MCP clients):

```bash
python -c "from armenian_budget.interfaces.mcp import server; server.run()"
```

Specify a data path (root containing CSV files):

```bash
python -c "from armenian_budget.interfaces.mcp import server; server.run('data/processed')"
```

HTTP:

```bash
python -c "from armenian_budget.interfaces.mcp import server; server.run_http('data/processed', host='127.0.0.1', port=8765)"
```

HTTPS (requires certificates):

```bash
python -c "from armenian_budget.interfaces.mcp import server; server.run_https('data/processed', host='127.0.0.1', port=8765)"
```

## Data directory layout

- Default root: `data/processed`
- Processed CSVs directly in: `data/processed/`
- Expected filenames: `{year}_{SOURCE}.csv`, e.g. `2025_BUDGET_LAW.csv`, `2024_SPENDING_Q12.csv`

## Resources (CSV content)

All resources return CSV text (MIME `text/csv`).

- `budget://{year}/state-bodies-summary`
  - Returns a two-column CSV (`state_body`, `state_body_total`)
  - De-duplicated: repeated totals are collapsed per `state_body` (max)

- `budget://{year}/programs-summary`
  - Returns program totals with state body context
  - Columns: `state_body`, `program_code`, `program_name`, `program_total` (max per group)

- `budget://{year}/full-data`
  - Returns full `BUDGET_LAW` CSV for the given year

## Core tools

- `list_available_data()` → Inventory of available datasets and diagnostics
- `get_data_schema(year, source_type)` → Columns, dtypes, shape, sample
- `filter_budget_data_enhanced(year, source_type, force_file_output=False, max_rows=None, **filters)` → Returns inline `data` for small results or a temp CSV `file_path` for large ones
  - Deprecation: `filter_budget_data(...)` still exists for compatibility but will be removed; prefer `filter_budget_data_enhanced`
- `get_ministry_spending_summary(year, ministry)` → Aggregates for a ministry using the best available source for the year
- `get_dataset_overall(year?=None, source_type?=None)` → Aggregated totals from `*_overall.json` files
  - Returns: `{ "overalls": { "2019": { "BUDGET_LAW": {...}, "SPENDING_Q12": {...} } }, "years": [2019], "source_types": ["BUDGET_LAW","SPENDING_Q12"], "count": 2 }`

## Data tools (direct access and previews)

- `preview_dataset(year, source_type, sample_size=10)`
  - Returns: `sample_data`, `schema`, `total_rows`, `unique_state_bodies`, `memory_usage_mb`

- `stream_budget_data(year, chunk_size=1000, offset=0, filters=None)`
  - Efficient chunked reads
  - If filters are absent, uses `skiprows`/`nrows` windowing
  - With filters, streams in larger chunks and applies vectorized filtering
  - Returns: `data` and `chunk_info {offset,size,total_rows,has_more}`

- `get_budget_visualization_data(year, view_type, output_format='json')`
  - `view_type`: `state-bodies` or `programs`
  - `output_format`: `json` or `csv`
  - Returns JSON records or `csv_content` for the chosen view

Example enhanced filtering call (with payload safeguards):

```json
{"tool": "filter_budget_data_enhanced", "params": {"year": 2025, "source_type": "BUDGET_LAW", "state_body": "Education", "min_amount": 1000000, "max_rows": 500, "force_file_output": false, "max_inline_bytes": 200000, "columns": ["state_body","program_code","program_name","program_total"], "text_truncate_len": 300}}
```

Example overall totals call:

```json
{"tool": "get_dataset_overall", "params": {"year": null, "source_type": null}}
```

## Analysis and aggregates

- `get_ministry_comparison(years, ministry_pattern, metrics=['allocated','actual'])`
  - Per-year allocated/actual and a simple `trend_analysis` between consecutive years

- `get_budget_distribution(year, groupby='state_body', top_n=20)`
  - Pie-chart-ready summary from de-duplicated state body totals

- Program lineage, similarity, and pattern tools:
  - `find_program_across_years_robust(reference_year, reference_program_code, search_years, ...)`
  - `search_programs_by_similarity(target_name, target_description?, years?, ministry_filter?, min_similarity=0.6)`
  - `trace_program_lineage(starting_program, search_years, confidence_threshold=0.8)`
  - `detect_program_patterns(pattern_type|custom, years, custom_keywords?, confidence_threshold=0.7)`
  - `register_program_equivalency(equivalency_map, description?)`, `get_program_equivalencies()`

- Cross-dataset utilities:
  - `bulk_filter_multiple_datasets(filters, years, source_types=['BUDGET_LAW'])` → combined temp CSV
  - `extract_rd_budget_robust(years, confidence_threshold=0.8, include_manual_mappings=True, return_details=False)`
  - `search_programs_by_similarity(..., max_per_year=50, force_file_output=false, max_inline_bytes=200000)`
  - `detect_program_patterns(..., max_per_year=50, force_file_output=false, max_inline_bytes=200000)`

## Filtering semantics (used by multiple tools)

Filters are vectorized and apply when the corresponding columns exist:

- `state_body`: case-insensitive substring match on `state_body`
- `program_codes`: list of integers matched against `program_code`
- `min_amount`: numeric threshold on a measure column chosen from the source type

Behavioral notes (enhanced filtering):

- If the filesystem is writable and the result is large, the server returns a temp CSV `file_path` under `data/processed/tmp/`.
- You can force file output regardless of size by setting `force_file_output=true`.
- To limit payloads, set `max_rows` (applies to both inline data and file output).

Measure columns by source type (common cases):

- `BUDGET_LAW`: `subprogram_total` for allocations
- `SPENDING_*`: `subprogram_annual_plan`, `subprogram_rev_annual_plan`, `subprogram_actual`, `subprogram_actual_vs_rev_annual_plan`

## Filesystem considerations

- The server detects read-only filesystems and will return data directly in-memory
- When writable and large outputs are produced, temp CSVs are saved under `data/processed/tmp/`

## Typical URIs and calls

Resource reads (CSV text):

```text
budget://2025/state-bodies-summary
budget://2025/programs-summary
budget://2025/full-data
```

Example tool calls (parameters shown conceptually):

```json
{"tool": "preview_dataset", "params": {"year": 2025, "source_type": "BUDGET_LAW", "sample_size": 5}}
{"tool": "stream_budget_data", "params": {"year": 2025, "chunk_size": 500, "offset": 0}}
{"tool": "get_budget_visualization_data", "params": {"year": 2025, "view_type": "state-bodies", "output_format": "csv"}}
{"tool": "get_dataset_overall", "params": {"year": 2025, "source_type": "BUDGET_LAW"}}
```

## Notes

- All examples assume relative project paths and the default processed data layout.
- For HTTP/HTTPS usage, ensure `uvicorn` is installed.
