# MCP Redesign

## Goals and constraints

- Reduce LLM context pressure while keeping workflows powerful and safe.
- Prefer thin, composable MCP server aligned with latest spec design principles: easy to build, composable, isolated, progressive feature negotiation.
- Default to small, schema- and intent-first interactions; escalate to large data only with explicit confirmation and pagination/handles.
- Use Polars Lazy API for performance, projection/filter pushdown, and vectorized operations.

## Target architecture (from the ground up)

- • Core execution
  - **Scan layer**: Polars `scan_csv` over `data/processed/csv`, optional schema hints to avoid expensive inference.
  - **Query planner**: Builds LazyFrame pipelines from structured knobs; validates and caps result size before materialization.
  - **Materialization manager**: Executes with row/byte caps, emits: inline JSON preview, Arrow IPC/Parquet/CSV file, or a resumable “result handle”.
- • Data catalog
  - Central catalog derived from directory scan plus `_overall.json` and per-dataset schema cards.
  - Provides typed inventory for years, source types, shapes, and “column roles” (allocated/revised/actual).
- • Result handles and pagination
  - Stateless by default; optional in-memory handle registry with TTL.
  - Every heavy tool returns a `result_handle` + `page_token` + `estimates`. Follow-up tool to fetch next page or change format.
- • Size negotiation and guardrails
  - Preflight estimator returns row/byte estimates; if above threshold, server responds with an elicitation request to confirm narrowed parameters or format switch.
  - Hard caps: `max_rows`, `max_bytes`, `max_cells`; soft caps negotiated via tool args.
- • Ambiguity and safety prompts (elicitation)
  - Pattern filters (e.g., Armenian text) trigger clarifying elicitation when matches are broad/ambiguous (“Include կրթություն?” “Exclude մասնագիտություն false positives?”).
  - Confirmations for potentially lossy ops (dedup/group/aggregation).
- • Capability surfacing
  - Tools and resources reflect the minimal operations; richer “prompts” provide schema cards, examples, and best-practice usage.
- • Transport
  - Prefer stdio; optional HTTP/HTTPS app for external clients with the same tools/resources.
- • Observability
  - Structured logs with request IDs, estimations, execution plans, and truncation decisions.

## Capability surface (tools/resources/prompts)

- • Tools (LLM-friendly knobs first, expression second)
  - `get_catalog`:
    - Parameters: `years?`, `source_types?`
    - Returns: inventory with dataset paths, row counts (approx), last_updated, sample file names.
  - `get_schema`:
    - Parameters: `year`, `source_type`
    - Returns: columns, dtypes, column roles, sample rows, shape, schema card URI.
  - `estimate_query`:
    - Parameters: `year`, `source_type`, `columns?`, `filters?`, `group_by?`, `aggs?`, `distinct?`
    - Returns: estimated rows/bytes, warnings (wide rows, cardinalities), suggested caps.
  - `query_data`:
    - Parameters: same as `estimate_query` + `order_by?`, `limit?`, `offset?`, `deduplicate?`, `null_policy?`, `format=json|csv|arrow|parquet`, `max_rows`, `max_bytes`.
    - Returns: `method=direct|file|handle`, `data|file_path|result_handle`, `page_info`, `preview`, `warnings`.
  - `query_next_page`:
    - Parameters: `result_handle`, `page_token`, `format?`
    - Returns: next page in chosen format.
  - `aggregate` (shortcut for grouped summaries):
    - Parameters: `year`, `source_type`, `group_by[]`, `aggs{col: fn}`, `filters?`, `top_n?`, `order_by?`, size knobs.
    - Returns: lightweight table, handle if large.
  - `distinct_values` (exploration):
    - Parameters: `year`, `source_type`, `column`, `limit?`, `min_count?`
    - Returns: freq table, used to build safe filters.
  - `pattern_filter` (Armenian-aware):
    - Parameters: `year`, `source_type`, `field`, `patterns[]`, `mode=contains|whole_word|normalized`, `exclude[]?`, `confirm_threshold?`
    - Behavior: may return an elicitation prompt with candidate sets to confirm inclusions/exclusions before executing.
  - `advanced_query` (opt-in):
    - Parameters: `year`, `source_type`, `polars_expr` (validated safe subset), `format`, size knobs.
    - Returns: same as `query_data`. Use when knobs insufficient.
- • Resources
  - `budget://{year}/{source_type}/schema` → JSON schema card (column roles, descriptions, examples).
  - `budget://{year}/{source_type}/catalog` → minimal inventory for that dataset.
  - `budget://{year}/{source_type}/summary` → tiny pre-aggregated summaries for safe-at-start context.
  - `budget://handle/{id}/{page}` → page streaming resource for clients that consume via URI.
- • Prompts (for startup context without tool calls)
  - `schema_cards_overview`: Short cheatsheet for column roles per source type.
  - `query_examples`: Small, LLM-optimized examples demonstrating knobs and safe flows.
  - `pattern_disambiguation_guidelines`: How to ask before including/excluding ambiguous Armenian terms.
  - `size_management_guidelines`: When to estimate, paginate, or switch formats.

## Design choices for your points (challenged and refined)

- • “Know what data is available”: Yes; via `get_catalog` and resource catalog URIs with filters. Include approximate row counts and last update.
- • “Know fields per data type (maybe without a tool)”: Agree; ship schema via MCP Prompts for baseline, plus `get_schema` for on-demand verification/samples.
- • “Filter columns, drop duplicates, by-what”: Provided in `query_data` knobs (`columns`, `distinct`, `deduplicate`, `filters` with operators: eq/in/contains/regex/range/normalized_contains).
- • “Group + aggregate”: Provide a simple `aggregate` tool for 90% cases; keep `advanced_query` with validated Polars for complex needs. Default to knobs; only use expr when needed.
- • “Pagination/limits”: Mandatory preflight `estimate_query`, required confirmation if above threshold, and result handles with paging.
- • “Pattern filtering and Armenian ambiguity”: Use `pattern_filter` with normalized matching and an elicitation loop; server proposes candidate sets and asks the user to confirm.

## Size-control and context protection

- Preflight on every non-trivial query: return `row_estimate`, `byte_estimate`, `sample_preview`, and “safe mode” alternatives (e.g., aggregated view).
- Auto-caps with deterministic behavior; exact serialization caps (e.g., 150k cells or 2 MB) before inline response; beyond that, file/handle only.
- Prefer Arrow IPC for binary paging; JSON only for previews/summaries.
- Distinct exploration tools to help the LLM narrow first, then query.

## Validation and safety

- Schema-aware validation of requested columns and functions.
- Safe subset for `polars_expr`: deny filesystem/network, restrict to expression building, timeouts, execution quotas.
- Clarifying elicitation for: broad patterns, unexpected cartesian expansions, high cardinality groupings, and lossy dedup/group operations.

## Module structure (replace monolith)

- `interfaces/mcp/server_app.py` (bootstrap, transport, registry)
- `data/catalog.py` (inventory, schema cards, caching)
- `data/roles.py` (column role maps per source type)
- `engine/scan.py` (scan_csv, schema hints)
- `engine/plan.py` (knob → LazyFrame)
- `engine/expr_validator.py` (safe Polars subset)
- `engine/materialize.py` (caps, paging, formats)
- `engine/patterns.py` (normalized match, Armenian helpers, disambiguation)
- `io/resources.py` (resource URIs emitters)
- `io/handles.py` (result handle registry with TTL)
- `observability/logs.py` (structured logging)

## Typical flows

- • Discover and narrow
  1) `get_catalog` → 2) `get_schema` → 3) `distinct_values` → 4) `estimate_query` → 5) confirm if big → 6) `query_data` first page.
- • Aggregation-first safe path
  1) `aggregate` top-k by `state_body` → 2) if needed, drill down with `query_data` + filters.
- • Ambiguous R&D request
  1) `pattern_filter` returns candidate lists → 2) elicitation to the user → 3) confirmed filter set → 4) `aggregate` or `query_data` with confirmed filters.

## Options and trade-offs

- • Results format
  - JSON: human/LLM-friendly previews only.
  - CSV: interoperable, but unsafe for very wide data; use for file outputs.
  - Parquet (preferred): compact, columnar, stable; default for large results. Arrow IPC optional/off by default due to prior issues.
- • State management
  - Stateless (recompute per page) is simplest but slower.
  - Short-lived handles with cached in-memory plan and scan context: faster, more moving parts. Default to handles with TTL and eviction.
- • Expression support
  - Knobs-only: safest and simplest for LLMs.
  - Knobs + validated Polars: best flexibility; keep behind explicit opt-in.
- • Transport
  - Stdio by default (Claude Desktop).
  - Optional HTTP/HTTPS for local apps; same tools/resources. HTTP is Phase 6 with auth, rate-limits, and download endpoints; MCP is not a BI protocol—provide an HTTP facade for BI integrations.

## Dataframe library policy (Polars-first)

- Use Polars Lazy for all scanning, filtering, grouping, and materialization paths.
- Prefer Polars for output formats (write_csv, write_parquet). Keep pandas only for legacy utilities temporarily.
- Deprecation path: replace pandas-based tools with Polars equivalents for non-legacy utilities by Phase 3.1; avoid pandas in new code.

## Migration strategy (incremental)

- Phase 1: Introduce new modules; add `get_catalog`, `get_schema`, `distinct_values`; enforce preflight estimation and caps on legacy heavy tools.
- Phase 2: Implement `estimate_query` and `query_data` (knobs-based planner), with strict size caps; previews as JSON only. No Arrow IPC.
- Phase 3: Add `pattern_filter` with elicitation loop and Armenian normalization; migrate YAML patterns into `engine/patterns.py` conventions.
- Phase 3.1: Spec catch-up and compatibility bridge
  - Do NOT introduce result handles yet (reserved for Phase 4).
  - Add optional resource URIs for large outputs (alongside temporary `file_path` for compatibility).
  - Implement `pattern_filter` confirmed mode returning a `filter_token` consumable by the planner.
  - Extend planner with `normalized_contains` and token-based matching helpers.
  - Add `aggregate` tool (group_by/aggs shortcut) with the same size knobs and outputs as `query_data`.
  - Enforce preflight policy on large queries; return elicitation prompts when over caps.
  - Expose `budget://{year}/{source_type}/catalog|schema|summary` resources.
  - Populate `last_modified_iso` in catalog entries.
  - Add structured logs with request IDs and decision breadcrumbs (estimate, caps, truncation).
- Phase 4: Introduce short-lived result handles + `query_next_page`; file outputs default Parquet (CSV fallback). Deprecate legacy heavy endpoints.
- Phase 5: Add `advanced_query` (validated Polars subset) for complex pipelines.
- Phase 6: Add HTTP/HTTPS façade with auth, rate-limits, and download endpoints; keep stdio as first-class.

## Decisions from Q/A

- Clients: Claude Desktop now; HTTP/HTTPS in Phase 6 as an auth‑enabled facade (not BI over MCP).
- Formats: Parquet preferred for large results; CSV fallback; Arrow IPC optional and off by default.
- Sizing: Catalog returns `row_count_approx` and `file_size_bytes`; `estimate_query` provides `byte_estimate`. No char counts needed.
- State: Short‑lived result handles/paging cache are acceptable (introduced in Phase 4).
- Pattern disambiguation: Default Balanced; Strict/Permissive modes available; elicit on ambiguity.
- Advanced Polars: Phase 5 feature.
- Security (future public server): TLS, JWT/OIDC, RBAC, rate‑limits, CORS allow‑list, timeouts, audit logs.
- Schema cards: Persist `{dataset}.schema.json`; CLI will emit/validate cards during processing.

## Short summary

- Proposed an MCP-aligned, thin, composable server with a catalog, schema cards, a knob-based query planner over Polars Lazy, strict preflight estimation, result handles with paging, and elicitation for ambiguous Armenian pattern filters. Heavy outputs default to Arrow/Parquet or paged handles; JSON is for previews and summaries. Provides both simple aggregation and optional validated Polars expressions. Outlined modules, flows, options, and a phased migration path.

## API surface contract (tools/resources)

- get_catalog
  - Inputs: `years?: List[int]`, `source_types?: List[str]`
  - Output: `datasets: [{year:int, source_type:str, path:str, row_count_approx:int, file_size_bytes:int, last_modified_iso:str}]`, `total:int`, `diagnostics?: {...}`

- get_schema
  - Inputs: `year:int`, `source_type:str`
  - Output: `columns: List[str]`, `dtypes: {col:str}`, `roles: {allocated?:str, revised?:str, actual?:str, execution_rate?:str}`, `shape: [rows:int|"approx", cols:int]`, `sample_rows: List[Record] (<=5)`, `schema_uri?: str`, `file_path?: str`

- distinct_values
  - Inputs: `year:int`, `source_type:str`, `column:str`, `limit?:int`, `min_count?:int`
  - Output: `values: [{value:any, count:int}]`, sorted by `count` desc, truncated to `limit`

- estimate_query
  - Inputs: `year:int`, `source_type:str`, `columns?: List[str]`, `filters?: [{col, op: eq|neq|in|contains|regex|range|normalized_contains, value:any|[any]|{min,max}}]`, `group_by?: List[str]`, `aggs?: [{col:str, fn: sum|avg|min|max|median|count|count_distinct}]`, `distinct?: bool`
  - Output: `row_estimate:int`, `byte_estimate:int`, `preview: List[Record] (<=5)`, `warnings: List[str]`, `suggested_caps: {max_rows:int, max_bytes:int}`

- query_data
  - Inputs: all `estimate_query` inputs plus `order_by?: [{col:str, desc?:bool}]`, `limit?:int`, `offset?:int`, `deduplicate?:bool`, `null_policy?: 'drop'|'keep'`, `output_format?: 'json'|'csv'|'parquet'`, `max_rows?:int`, `max_bytes?:int`
  - Output (one of):
    - Direct: `{method:'direct', data: List[Record] (<= limit and caps), row_count:int, page_info?: {offset:int, size:int, has_more:bool}, warnings?:[]}`
    - File: `{method:'file', resource_uri:str, row_count:int, format:'csv'|'parquet', preview: List[Record] (<=10), file_path?:str}`
    - Handle: `{method:'handle', result_handle:str, page_info:{page_token:str, size:int, has_more:bool}, preview: List[Record]}`

- query_next_page
  - Inputs: `result_handle:str`, `page_token:str`, `format?: 'json'|'csv'|'parquet'`
  - Output: same shape as `query_data` result for the chosen method (direct/file), with next `page_token` if `has_more`

- aggregate
  - Inputs: `year:int`, `source_type:str`, `group_by: List[str]`, `aggs: [{col, fn}]`, `filters?:[...]`, `top_n?:int`, `order_by?:[...]`, `format?:'json'|'csv'|'parquet'`, caps as in `query_data`
  - Output: small table inline (JSON) when under caps; otherwise file/handle with same contract as `query_data`

- pattern_filter
  - Inputs: `year:int`, `source_type:str`, `field:str`, `patterns: List[str]`, `mode: 'strict'|'balanced'|'permissive'`, `exclude?: List[str]`, `confirm_threshold?: float`
  - Output:
    - Elicitation: `{status:'needs_confirmation', candidates:{include:[str], exclude:[str]}, question:str, notes?:str}`
    - Ready filter: `{status:'confirmed', filter_token:{col, op:'normalized_contains'|'regex'|'in', value}, diagnostics?:{matched:int}}`
    - Or directly: same contract as `query_data` if `execute: true` is supported later

- advanced_query (Phase 5)
  - Inputs: `year:int`, `source_type:str`, `polars_expr:str` (validated subset), `output_format?:'json'|'csv'|'parquet'`, caps as in `query_data`
  - Output: as in `query_data`

Resources

- `budget://{year}/{source_type}/schema` → JSON schema card; `application/json`
- `budget://{year}/{source_type}/catalog` → minimal dataset inventory for that pair; `application/json`
- `budget://{year}/{source_type}/summary` → pre-aggregated small summaries; `application/json`
- `budget://handle/{id}/{page}` → streamed page content; defaults to `text/csv` or `application/octet-stream` for Parquet

Common behaviors

- Size caps: default `max_cells`, `max_rows`, `max_bytes` enforced before inline JSON. If exceeded, switch to file or handle automatically with a warning.
- Result handles: short-lived (TTL, e.g., 10–30 minutes), evicted LRU; deterministic paging over a consistent snapshot.
- Formats: JSON for previews/summaries; Parquet preferred for files; CSV as fallback; Arrow IPC optional/disabled by default.

## Large result delivery options (and IPC stance)

- JSON: previews only (small slices, summaries). Never used for large tables.
- Parquet: default for file outputs and handles; compact, columnar, fast to page/scan.
- CSV: fallback for interoperability; larger on disk; good for quick manual inspection.
- Arrow IPC: optional and off by default given prior issues; can be enabled per-deployment if needed.
- Pagination: heavy queries return a `result_handle` plus `page_token`; clients fetch pages via `query_next_page` or `budget://handle/{id}/{page}`.

## MCP compliance policy (spec-aligned outputs)

- Tools must return plain JSON; for large results, prefer returning a resource URI or a result handle instead of raw file paths.
- Resource-first: expose `budget://...` URIs for downloadable artifacts and paged results. Include small `preview` inline.
- Compatibility window:
  - Phase 3.1: allow both `resource_uri` (preferred) and `file_path` (legacy).
  - Phase 4: introduce result handles; keep `resource_uri` and handles; start deprecating `file_path`.
  - Phase 5+: remove `file_path` from new outputs.
- Preflight is a server policy (not required by MCP): enforce estimator + elicitation for potentially large queries.
- Prompts should provide minimal startup context (schema cards overview, query examples, size guidelines) without requiring an initial tool call.

## Error handling policy

- Expected errors: return structured JSON with fields `error` (string), `code` (stable identifier), `hint` (optional), `diagnostics` (optional small object). Example codes: `dataset_not_found`, `invalid_column`, `oversize_result`, `unsupported_format`.
- Unexpected/internal errors: raise exceptions; let the MCP framework surface them as tool errors while logging details server-side.
- All tools should avoid partial successes without explicit warnings; include `warnings: []` for non-fatal notices.

## Armenian pattern disambiguation modes

- Strict
  - Whole-word + normalized matching; excludes broad stems; high precision, lower recall.
  - Always elicits confirmation on overlapping or ministry‑crossing matches.
- Balanced (default)
  - Normalized token windows with heuristics to avoid false positives (e.g., "գիտություն" vs "մասնագիտություն").
  - Elicitation triggered on wide match sets, cross‑ministry leakage, or low confidence.
- Permissive
  - Substring matching; maximal recall; elicit only when match set is extremely broad.

## Notes on catalog/schema sizing fields

- `get_catalog` should include `row_count_approx` and `file_size_bytes`. Character counts are not necessary; for very wide columns, `estimate_query` returns `byte_estimate` computed from selected columns.

## Legacy tools/resources migration plan

- Keep (core, first-class): `get_catalog`, `get_schema`, `distinct_values`, `estimate_query`, `query_data`, `pattern_filter`, `get_dataset_overall`.
- Add (new core): `aggregate`, `query_next_page`.
- Refactor for core alignment:
  - `bulk_filter_multiple_datasets`: reimplement via planner, return resource URI/handle for large results.
  - Resources `budget://{year}/state-bodies-summary`, `budget://{year}/programs-summary`: keep as curated summaries; consider aliasing under `budget://{year}/summary/*`.
  - Resource `budget://{year}/full-data`: keep for now, but document risks; consider renaming to `budget://{year}/{source_type}/full` and enforcing caps/handles for delivery.
- Deprecate in favor of `aggregate` once available (announce deprecation window):
  - `get_budget_visualization_data`, `get_budget_distribution`.
- Move to "analysis" plugin/server (Phase 6) or keep as optional tools, refactored to reuse core scan/plan:
  - `get_ministry_comparison`, `find_program_across_years_robust`, `search_programs_by_similarity`, `trace_program_lineage`, `detect_program_patterns`.
  - If kept in this server, update outputs to use resource URIs/handles for large payloads.
- Admin/config tools (keep, with improved error handling):
  - `register_program_equivalency`, `get_program_equivalencies`.

Open questions to resolve in Phase 3.D (decision checkpoint):

- Should analysis tools live in a separate MCP server for composability and minimal surface, or remain here behind an "analysis" capability flag?
- Do we retain `budget://{year}/full-data` as a resource long-term, or gate it strictly behind handles/paging only?
- What is the exact retention/TTL for result handles given typical client workflows?

## Server metadata and versions

- Surface server name/version and MCP spec version via FastMCP metadata (tooling typically reads this on connect). If needed, add a lightweight `get_server_info` tool returning `{name, version, spec_version, capabilities}` for clients lacking metadata access.
- Use capability flags for optional surfaces (e.g., `analysis_tools`, `handles_available`). Toggle as phases progress.

### Migration schedule by phase

- Phase 3.1
  - Refactor `bulk_filter_multiple_datasets` to planner; return `resource_uri` for large results (keep `file_path`).
  - Keep summaries resources; add `budget://{year}/{source_type}/catalog|schema` resources.
  - Begin deprecating `get_budget_visualization_data`/`get_budget_distribution` (announce).
- Phase 4
  - Introduce handles + `query_next_page`. Add `budget://handle/{id}/{page}` resources.
  - Switch all large outputs to `resource_uri`/handles. Mark `file_path` as deprecated.
  - Decide whether to move analysis tools to a separate server; if staying, update outputs to resource/handle.
- Phase 5
  - Remove `file_path` from new outputs. Implement `advanced_query`.
  - Finalize analysis tools placement and capability flags.

## TODOs

Ask "are there any other action items in the redesign plan that seem to be skipped in the phases?"
