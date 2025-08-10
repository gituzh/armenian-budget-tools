# Product Requirements Document (PRD) — Armenian Budget Tools

## 1. Overview

Armenian Budget Tools is an open-source toolkit to fetch, parse, normalize, validate, store, and analyze Armenian state budget laws and spending reports. It exposes a clean Python API, a user-friendly CLI, and an MCP server to enable AI-assisted queries.

- **Repository**: `budget-am`
- **Python package (proposed)**: `armenian-budget-tools`
- **Import namespace**: `armenian_budget`

## 2. Goals and Non-goals

- **Goals**
  - Robustly parse 2019–2025 budget laws and spending Excel reports; provide a column registry utility for cross-dataset analysis without forcing a single schema.
  - Provide reusable validations for hierarchical totals, percentage ranges, and spending logic.
  - Offer both CSV and Parquet outputs with metadata and lineage.
  - Simple CLI and Python API for processing and validation.
  - Basic MCP server tools for AI access to processed data (inventory, schema, filter, summaries).

- **Non-goals (v1)**
  - Historical PDF parsing and OCR.
  - Advanced analytics beyond summaries/trends.
  - Fully automated source downloading for all years (start with minimal/manual sources).

## 3. Users and Use Cases

- **Data analysts / researchers**: Batch processing, validate data integrity, export Parquet for analysis.
- **Journalists / civic tech**: Inspect specific ministries/programs across years; validate claims.
- **Developers**: Integrate via Python API into pipelines; programmatic filters.
- **AI agents (MCP)**: List datasets, inspect schemas, filter by criteria, summarize a ministry.

### Primary Use Cases
- **Parse & normalize** a year’s budget law into a consistent schema.
- **Validate** hierarchical totals and spending relationships; produce a report.
- **Export** CSV/Parquet for downstream analysis and BI tools.
- **Filter** processed data by ministry/program and hand to AI or notebooks.

## 4. Scope (v1)

- **Formats**: Excel-based budget laws (2019–2025) and spending reports (Q1, Q12, Q123, Q1234) for available years. No PDFs in v1.
- **Common Core (optional)**: When requested, add derived columns `allocated_amount`, `revised_amount`, `actual_amount`, `execution_rate`, and harmonized identifiers for analysis convenience, while preserving all original source columns unchanged.
- **Validations**:
  - Hierarchical totals consistency (state body = sum(programs) = sum(subprograms)).
  - Percentage ranges [0, 1]; basic spending logic (period ≤ annual; revised constraints).
  - Cross-source: spending annual plans match budget law totals (same year).
  - Cross-year: structural checks (names/codes drift warnings).
- **Storage**: CSV and Parquet; write processing metadata (checksums, version, timestamps).
- **Interfaces**:
  - CLI: `process`, `validate`, `export`, `status`.
  - Python API: module functions mirroring CLI operations.
  - MCP (phase 2 minimal): dataset inventory, schema, filter, ministry summary.

## 5. Non-functional Requirements

- **Performance**: Process a typical year file within ~60–120s on a laptop; vectorized operations using pandas.
- **Reliability**: Deterministic outputs; clear typed errors; no `sys.exit` in library code.
- **Observability**: Human-readable logs in v1; JSON-structured logs arrive in v0.5. Validation reports emitted as files.
- **Compatibility**: Python 3.10+; macOS and Linux supported in v1; Windows can be considered later.
- **Data precision**: Use float64 for DataFrame operations; compare numerics with tolerances (e.g., absolute diff ≤ 0.01) or rounding to 2 decimals where domain-appropriate. Use Decimal only at boundaries if needed.
- **Security**: No arbitrary code execution; checksums and file provenance recorded.

## 6. Column roles and identifiers (v0.1)

At subprogram grain unless unavailable. Key fields:
- **Identifiers**: `year`, `source_type`, `source_file`
- **Hierarchy**: `state_body`, `state_body_code?`, `program_code`, `program_name`, `subprogram_code`, `subprogram_name`
- **Financials**: `allocated_amount?`, `revised_amount?`, `actual_amount?`, `period_amount?`, `execution_rate?`
- **Program metadata**: `program_goal?`, `program_result_description?`, `subprogram_description?`, `subprogram_type?`
- **Lineage**: `raw_columns`/`metadata` with original column names and checksum

We maintain all original source columns. For convenience, a column registry utility exposes which columns represent the following roles per dataset:

- allocated (e.g., budget law: `subprogram_total`; spending: `subprogram_annual_plan`)
- revised (spending: `subprogram_rev_annual_plan`)
- actual (spending: `subprogram_actual`)
- execution_rate (spending: `subprogram_actual_vs_rev_annual_plan` when present)

## 7. Functional Requirements

- **Ingestion/Parsing**
  - Excel parser for 2019–2024 and separate logic for 2025 format.
  - Configurable label detection and tolerant normalization for Armenian text.
  - Typed exceptions for schema/label mismatches; no abrupt exits.

- **Column registry**
  - Provide a helper to fetch role→column mappings for a dataset; leave data unchanged.

- **Validation**
  - Reusable functions returning `ValidationResult {passed, errors[], warnings[]}`.
  - Levels: `strict` (fail on errors), `lenient` (log and continue).

- **Storage**
  - Write CSV and Parquet in `data/processed/{csv,parquet}`; maintain `metadata.json` with provenance.

- **CLI**
  - `process --year 2023 --source-type budget_law --input path.xlsx --out data/processed [--strict]`
  - `validate --year 2023 --source-type budget_law [--report out.json]`
  - `export --format parquet --years 2019-2025 [--filter state_body=...]`
  - `status` shows available processed datasets and last updated times.

- **Python API**
  - `process_file(...)`, `validate_dataset(...)`, `export_datasets(...)`, `list_available_data(...)`.

- **MCP (Phase 2)**
  - Tools: `list_available_data`, `get_data_schema`, `filter_budget_data`, `get_ministry_spending_summary`.

## 8. Error Handling & Exit Codes

- Library raises typed exceptions (`ParseError`, `LabelMismatchError`, `ValidationError`).
- CLI maps to exit codes: `0` success, `1` parse error, `2` validation failure, `3` IO/config.

## 9. Deliverables & Acceptance Criteria

- Processors for 2019–2025 budget laws; spending where available.
- CSV and Parquet outputs for processed datasets; validation reports written to disk.
- Validation module extracted from tests; all tests green.
- CLI commands operational with helpful logs and exit codes.
- Minimal MCP server with Phase 1 tools.

## 10. Decisions Answered

- v1 formats: Excel only, 2019–2025 budget laws and spending (Q1/Q12/Q123/Q1234 where available). No PDFs.
- Platform: macOS and Linux supported in v1.
- File sizes: assume small; no special performance handling required initially.
- No normalization in v1; use column registry for roles.
- Performance stack: pandas-only in v1.
