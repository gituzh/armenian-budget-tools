# Roadmap — Armenian Budget Tools

This roadmap is pragmatic and incremental. Each milestone should be shippable and keep current functionality working.

## Milestone v0.1 — Structure + CLI MVP (Weeks 1–2)

- **Repo structure**: create `src/armenian_budget/{parsers,validation,storage,cli,utils,core}`
- **Parser migration**: move existing Excel parsers (2019–2024, 2025) into `parsers/` as-is
- **Error handling**: replace `sys.exit` with typed exceptions
- **Validation**: extract from `tests/utils/validation_helpers.py` → `validation/financial.py`
- **Column registry**: utility mapping measure roles to dataset columns (allocated/revised/actual/% when present)
- **Storage**: write CSV only (defer Parquet and metadata.json)
- **CLI**: `armenian-budget process|validate` (minimal)
- **CI**: GitHub Actions for tests + lint; add pre-commit (ruff/black)

Exit criteria:

- All existing tests pass with imports updated
- CLI can process 1 year and validate successfully

Suggested steps:

```bash
# 1. Create new folder structure
mkdir -p src/armenian_budget/{core,ingestion/parsers,validation,storage,cli,utils}

# 2. Move existing parser code and split by year
mv src/budget-am/budget/__init__.py src/armenian_budget/ingestion/parsers/
# Split the large __init__.py into excel_2019_2024.py and excel_2025.py

# 3. Extract validation logic from tests
cp tests/utils/validation_helpers.py src/armenian_budget/validation/financial.py

# 4. Move current data to new structure  
mkdir -p data/{original,extracted,processed}
mv raw_data/* data/original/
mv output/* data/processed/csv/
```

## Milestone v0.2 — Validation & DX (Weeks 3–4)

- **Validation**: add cross-source and cross-year checks (previously in tests)
- **Logging**: human-friendly logs in v0.2; JSON logs deferred until v0.5
- **Docs**: `architecture.md`, `prd.md`, `roadmap.md` updated and linked from README
- **Packaging**: PEP 621 metadata, console scripts

Exit criteria:

- Deterministic processing with saved validation report (human-readable)

CLI tasks:

```bash
armenian-budget process --year 2023
armenian-budget validate --all
```

## Milestone v0.3 — MCP Phase 1 (Weeks 5–6)

- **MCP server**: implement tools
  - `list_available_data`
  - `get_data_schema`
  - `filter_budget_data`
  - `get_ministry_spending_summary`

Exit criteria:

- Basic AI chat flows can discover data, inspect schema, and get filtered CSV/Parquet paths

Server tasks:

```bash
armenian-budget mcp-server --port 8000
# Test prompts: "What data do you have available?", "Show the schema for 2023 budget law"
```

## Milestone v0.4 — Source Management + Config (Weeks 7–8)

- **Registry**: minimal `config/sources.yaml` with known URLs
- **Downloader**: optional download + extract (zip, rar) with graceful errors
- **Discovery**: file discovery under `data/{original,extracted}`
- **Parser config**: externalize parser label/column configs → `config/parsers.yaml`; add label tolerance in config

Exit criteria:

- `armenian-budget download --year 2025` fetches and organizes files or gives a clear instruction to provide local files
- Users can configure label tolerance via YAML

## Milestone v0.5 — Quality & Insights (Weeks 9–10)

- **Analytics**: simple trends/anomaly detectors (warnings, not hard errors)
- **JSON logs**: structured logging and machine-readable validation reports
- **Telemetry**: anonymized, opt-in MCP request telemetry to identify common analytics
- **Docs & examples**: notebooks and examples for typical analyses
- **Stability**: tighten types, error messages, and performance of hot paths

Exit criteria:

- Example notebooks run end-to-end on processed Parquet

## Backlog / Stretch

- PDF parsing for historical years
- Multilingual field names (EN/AM) and harmonization helpers
- Common Core normalization (optional, non-destructive)
- Integer luma representation (dram subunits) to avoid rounding issues
- Analytics module informed by telemetry (if adopted)
- Web/API service for hosted access
- Extended MCP analytics tools

## Risks & Mitigations

- **Excel format drift**: Parameterize with YAML and tolerant label matching
- **Large files**: Prefer Parquet-first workflows; revisit engine choices later if needed
- **RAR extraction on Windows**: Document prerequisites; allow manual placement of extracted files
- **Data quality issues**: Make validations configurable; default to warn where domain allows
