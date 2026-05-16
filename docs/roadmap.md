# Roadmap — Armenian Budget Tools

This roadmap is pragmatic and incremental. Each milestone should be shippable and keep current functionality working.

> **Note:** For released changes, see [CHANGELOG.md](../CHANGELOG.md). This roadmap keeps the recently completed milestone visible briefly, then focuses on upcoming work.

## Recently Completed

## Milestone v0.5.1 — 2026 Q1 Spending Release

**Focus:** Package the first 2026 spending execution report and align release metadata
for a patch release.

### Features

- Add 2026 Q1 spending outputs under `data/processed`.
- Add the 2026 Q1 spending source registry entry, checksum, and discovery metadata.
- Refresh README, citation metadata, data schema docs, developer examples, and generated
  documentation notes for the new partial-year 2026 spending coverage.
- Refresh the R&D docs example to use 2025 full-year spending actuals and clearly
  label 2026 Q1 spending as partial-year.
- Release package version `0.5.1`.

### Exit Criteria

- `2026_SPENDING_Q1.csv` and companion overall/validation sidecars are packaged.
- Data availability tooling reports the 2026 Q1 spending dataset.
- Version metadata, changelog, and roadmap are aligned for release.

## Milestone v0.5.0 — Source Discovery, GDP Context, and Release Artifacts

**Focus:** Improve source maintenance, add GDP denominator context, and make release
artifacts easier to audit and package

### Features

- **MinFin source discovery utilities**:
  - Add `armenian-budget minfin-spending-reports`
  - Add `armenian-budget minfin-budget`
  - Support year filters and spending quarter filters
  - Support flat JSON output for downloadable files via `--downloads-only`
  - Keep live source listing separate from `config/sources.yaml` updates

- **GDP indicator extraction and reporting**:
  - Add `armenian-budget gdp-extract` for budget law and full-year spending sources
  - Write `{year}_{BUDGET_LAW|SPENDING_Q1234}_GDP.json` snapshots
  - Add `armenian-budget gdp-report` for HTML review of available snapshots
  - Include processed GDP snapshots for currently supported budget and spending years

- **Source registry and download auditability**:
  - Support multi-file source definitions in `config/sources.yaml`
  - Support explicit local archive filenames in source definitions
  - Change `download --force` to re-fetch and replace only when content differs
  - Track SHA-256 checksums for downloaded archives
  - Preserve changed same-URL archives under `.revisions/`
  - Record checksum history in `config/checksum_history.yaml`

- **Data and packaging updates**:
  - Add 2025 full-year spending outputs
  - Fix 2025 full-year spending parsing for actuals and execution percentages
  - Add release artifact builder for data and analysis-skill bundles
  - Extend the repo-owned analysis skill with GDP artifact awareness

- **Interface cleanup**:
  - Remove the legacy MCP server module, CLI command, dependency, and docs
  - Keep the repo-owned analysis skill as the primary AI-facing workflow

### Exit Criteria

- CLI lists spending report and budget files advertised on minfin.am
- Tests cover HTML extraction and CLI JSON output without live network calls
- GDP snapshots can be extracted and reviewed in an HTML report
- Download checksum changes are archived and recorded reproducibly
- Release data and skill artifacts can be built from a single script
- Legacy MCP entry points and docs are removed
- README, developer guide, and data schema docs cover the new commands and artifacts

### CLI Examples

```bash
armenian-budget minfin-spending-reports --years 2025
armenian-budget minfin-spending-reports --years 2025 --quarter Q1234 --downloads-only
armenian-budget minfin-budget --years 2026 --downloads-only
armenian-budget gdp-extract --years 2021-2026 --source-type BUDGET_LAW
armenian-budget gdp-report
```

## Upcoming

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
- Consider translating key user-facing docs (data_schemas.md, validation.md)

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
