# Roadmap — Armenian Budget Tools

This roadmap is pragmatic and incremental. Each milestone should be shippable and keep current functionality working.

> **Note:** For completed releases, see [CHANGELOG.md](../CHANGELOG.md). This roadmap focuses on upcoming milestones.

## Milestone v0.4.0 — MTEP + Validation Refactor + Documentation

**Focus:** Complete MTEP integration, separate validation from tests, improve documentation governance

### Features

- **MTEP data type**: Complete integration of Medium-Term Expenditure Program (MTEP) data
  - 2-level hierarchy (state body → program, no subprograms)
  - Multi-year planning horizon (y0, y1, y2 columns)
  - JSON overall format with `plan_years` array
  - Validation rules specific to MTEP structure
  - Update `config/sources.yaml` with complete MTEP URLs

- **Validation/Tests separation**: Move production validation logic out of `tests/` into `validation/`
  - Extract reusable validation functions from test utilities
  - Create `validation/runner.py` for orchestration
  - Maintain test coverage while separating concerns
  - Update imports across codebase

- **Documentation improvements**:
  - Formalize documentation governance (see `CLAUDE.md`)
  - Enhance `developer_guide.md` with MTEP examples
  - Update `data_schemas.md` with MTEP column specifications
  - Ensure all docs reflect actual codebase structure

### Exit Criteria

- MTEP data processes end-to-end with validation
- All production validation logic in `src/armenian_budget/validation/`
- Tests use validation module, not duplicated logic
- Documentation accurately reflects codebase (verified with actual files)

### CLI Examples

```bash
# Download MTEP sources
armenian-budget download --years 2024 --source-type mtep

# Extract archives
armenian-budget extract --years 2024 --source-type mtep

# Parse MTEP data
armenian-budget parse --years 2024 --source-type MTEP

# Validate MTEP output
armenian-budget validate --csv data/processed/2024_MTEP.csv
```

## Milestone v0.5.0 — MCP Server Redesign

**Focus:** Simplified, more powerful MCP server with flexible query engine

### Features

- **Simplified architecture**:
  - Reduce number of specialized tools (consolidate similar functionality)
  - Improve query planning and execution
  - Better separation between resource and tool APIs

- **More flexible tools**:
  - Generic query interface with composable filters
  - Support for cross-year and cross-source queries
  - Aggregation and grouping capabilities
  - Time-series analysis primitives

- **Improved result handling**:
  - Smart inline vs file path decision logic
  - Configurable size thresholds
  - Streaming support for large results
  - Better error messages and diagnostics

- **Enhanced query engine**:
  - Declarative query planning
  - Optimized execution strategies
  - Caching for repeated queries
  - Performance monitoring

### Exit Criteria

- MCP server supports all previous use cases with fewer, more powerful tools
- Query performance improved (benchmarked)
- Example notebooks demonstrate new capabilities

### API Examples

```python
# New unified query interface
mcp_client.query(
    years=range(2019, 2025),
    source_types=["BUDGET_LAW", "SPENDING_Q1234"],
    filters={"state_body": "Ministry of Education"},
    aggregations={"sum": "allocated_amount"},
    group_by=["year"]
)
```

## Milestone v0.6.0 — Government Target Metrics

**Focus:** Add government performance target metrics as new data type

### Features

- **New data type**: `GOVERNMENT_TARGETS`
  - Annual performance targets by ministry/program
  - Actual achievement metrics
  - Target vs actual comparison analytics

- **Parser implementation**:
  - Excel parser for government target reports
  - Handle target-specific column structures
  - Extract both quantitative and qualitative metrics
  - Support multi-year target tracking

- **Integration**:
  - Add to existing pipeline (`parse`, `validate`, `download`)
  - Cross-reference with budget allocations
  - Enable budget vs performance analysis

- **Analytics**:
  - Target achievement rates
  - Budget efficiency metrics (spending vs target achievement)
  - Trend analysis across years
  - Anomaly detection for underperforming programs

### Exit Criteria

- Government target data processes end-to-end
- Validation rules for target metrics implemented
- MCP tools support target queries
- Example analysis: budget allocation vs target achievement

### Use Cases

```bash
# Parse government targets
armenian-budget parse --years 2023 --source-type GOVERNMENT_TARGETS

# Analyze budget efficiency
armenian-budget analyze --years 2023 --metric budget-efficiency \
  --compare BUDGET_LAW GOVERNMENT_TARGETS
```

## Milestone v0.7.0 — CLI Redesign

**Focus:** Clean Unix philosophy with single-responsibility commands + convenient meta-command

### Features

- **Pure Unix-style individual commands**:
  - Rename `process` → `parse` (clearer naming for the parsing step)
  - Remove `--extract` flag from `download` command
  - Each command does one thing well: `download`, `extract`, `discover`, `parse`, `validate`
  - Clear separation of concerns with no flag proliferation

- **Meta-command for full pipeline**:
  - Add new `process` command that runs the full workflow: download → extract → discover → parse
  - Support `--skip-*` flags for partial workflows (e.g., `--skip-validate`)
  - Support `--from-step` for resuming from a specific point
  - Fail fast with clear error messages

- **Improved user experience**:
  - Better error handling for missing/corrupted archives
  - Progress reporting for downloads and extraction
  - Clear logging showing which step is running
  - Helpful suggestions when commands fail

- **Documentation updates**:
  - Document both individual commands (for flexibility) and meta-command (for convenience)
  - Add workflow examples to README
  - Update all CLI examples across docs

### Exit Criteria

- All individual commands follow single-responsibility principle
- Meta `process` command works end-to-end for common workflows
- Error messages provide actionable guidance
- Documentation clearly explains both approaches

### CLI Examples

```bash
# Individual commands (Unix philosophy - maximum control)
armenian-budget download --years 2023-2024
armenian-budget extract --years 2023-2024
armenian-budget discover --years 2023-2024
armenian-budget parse --years 2023-2024
armenian-budget validate --csv data/processed/2023_BUDGET_LAW.csv

# Meta-command (convenience - common workflow)
armenian-budget process --years 2023-2024                    # full pipeline
armenian-budget process --years 2023 --skip-validate         # skip validation
armenian-budget process --years 2023 --source-type mtep      # MTEP only
armenian-budget process --years 2023 --from-step extract     # resume from extract
```

## Backlog / Stretch

**Data Sources:**

- Budget draft support with version tagging system
  - Optional version tag in `config/sources.yaml` (e.g., `version: "draft"`, `version: "first_reading"`)
  - Missing version tag defaults to "final"
  - Version suffix in output files: `{year}_{SOURCE_TYPE}_{version}.csv` (e.g., `2026_BUDGET_LAW_draft.csv`)
  - Supports multiple versions per year (draft, first reading, second reading, final)
  - Backup archive URLs for versions that may be deleted from minfin.am after final adoption
- PDF parsing for historical years (2017-2018)
- OCR integration with quality scoring
- Additional data types (procurement, grants, debt)

**Analytics & Insights:**

- Advanced analytics module (trends, anomalies, forecasting)
- JSON structured logging and machine-readable reports
- Opt-in telemetry to identify common use cases
- Example notebooks and typical analysis templates

**Normalization & Compatibility:**

- Multilingual field names (EN/AM) and harmonization helpers
- Common Core normalization (optional, non-destructive)
- Integer representation for exact arithmetic (dram subunits)
- Cross-year program tracking and identifier harmonization

**Infrastructure:**

- Web/API service for hosted access

**Documentation:**

- Armenian README translation (README.hy.md)
- Consider translating key user-facing docs (data_schemas.md, mcp.md)

## Risks & Mitigations

**Technical Risks:**

- **Excel format drift**: Parameterized parsers with YAML configs and tolerant label matching; version detection logic
- **Performance degradation**: Profile critical paths; optimize with vectorization; consider Parquet/DuckDB for large datasets
- **Dependency conflicts**: Pin critical dependencies; test across Python 3.10-3.12; maintain compatibility matrix

**Data Quality Risks:**

- **Source data errors**: Configurable validation levels (strict/lenient); clear error reporting with file/row context
- **Missing or incomplete data**: Graceful degradation; document data availability per year/source; provide fallback strategies
- **Cross-source inconsistencies**: Cross-validation warnings; manual review workflow; document known issues

**Operational Risks:**

- **Archive extraction failures**: Support manual file placement; document prerequisites per platform; checksum verification
- **URL changes**: Monitor official sources; maintain fallback URLs; version source registry
- **Breaking changes**: Semantic versioning; deprecation warnings; migration guides; maintain backward compatibility

**Mitigation Strategy:**

- Extensive test coverage with real data
- Configuration-driven design for flexibility
- Clear error messages with remediation steps
- Regular validation against official sources
