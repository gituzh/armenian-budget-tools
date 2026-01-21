<!-- markdownlint-disable MD024 -->
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2026-01-21

### Added

- Add MTEP (Mid-Term Expenditure Program) support
  - New `SourceType.MTEP` for 3-year expenditure plans
  - FSM-based parser for MTEP Excel files
  - 2024 MTEP data included in processed data
- Extend data coverage through 2026
  - 2024 Q1234 spending report
  - 2025 Q1, Q12, Q123 spending reports
  - 2026 budget law (final and draft versions)
  - Budget laws for 2021-2025 (previously missing)
- Overhaul validation system
  - Modular check-based architecture with 10 specialized checks: `empty_identifiers`, `execution_exceeds_100`, `hierarchical_structure_sanity`, `hierarchical_totals`, `missing_financial_data`, `negative_percentages`, `negative_totals`, `percentage_calculation`, `period_vs_annual`, `required_fields`
  - Registry-based validation framework with structured result models
  - Configurable tolerances: `SPENDING_ABS_TOL = 5.0` AMD, `BUDGET_LAW_ABS_TOL = 0.0`
  - Support for negative annual plan values in spending validation
- Add field schema system
  - Centralized field definitions for all source types
  - Column role mappings for consistent data access
  - Required field specifications for CSV and JSON outputs
- Enhance CLI
  - Multi-year `validate` command with `--report` (Markdown) and `--report-json` flags
  - `--source-type` filter for `download` and `validate` commands (optional in validate)
  - Standardized `--years` flag across all commands (removed `--year`)
  - Improved error handling and exit codes
- Add documentation
  - `docs/developer_guide.md` - API reference and implementation patterns
  - `docs/data_schemas.md` - Column specifications and schemas
  - `docs/validation.md` - Validation usage guide and check reference
  - `docs/validation_known_issues.md` - Source data anomalies tracking
- Add citation support
  - Structured metadata in `CITATION.cff` for academic use
- Add funding links
  - GitHub Sponsors integration with donation badges
- Enhance parser support
  - Extended 2025 parser for spending reports with improved Armenian text handling

### Changed

- BREAKING: Move processed data from `data/processed/csv/` to `data/processed/`
  - MCP server and CLI automatically use new location
  - Old `csv/` directory has placeholder file for users with bookmarks
- BREAKING: Change validation API from file-based to year/source-type based
  - `run_validation()` now accepts `year` and `source_type` instead of file paths
  - Returns structured `ValidationResult` objects instead of boolean/list tuples
- Standardize CLI on `--years` across all commands (remove `--year` single-year flag)
- Use relative paths (filenames only) in validation reports for portability
- Downgrade spending validation period vs annual subprogram violations from error to warning
- Restructure documentation for clarity (simplify `architecture.md`, `prd.md`, `roadmap.md`)
- Update `CLAUDE.md` with code quality principles and documentation governance
- Restructure tests: `tests/data_validation/` → `tests/validation/` with modular check tests; add `tests/parser/`
- Move dev dependencies from `requirements.txt` to `pyproject.toml`

### Fixed

- Fix CLI `validate` command exit codes for invalid source types
- Fix CLI `extract` command now supports all source types (was only spending reports)
- Improve percentage calculation comparison robustness in validation
- Fix SSL handshake failure for minfin.am downloads

## [0.3.0] - 2025-08-24

### Added

- Add tests for non-empty budget law files (module: `tests.data_validation.test_budget_law_validation`)
- Add tests for spending consistency and non-empty datasets (module: `tests.data_validation.test_spending_validation`)
- Add MCP documentation (file: `docs/mcp.md`)

### Fixed

- Fix parser patterns and refresh discovery index (modules: `config.parsers.yaml`, `data.extracted.discovery_index.json`)

### Changed

- Improve MCP server (module: `armenian_budget.interfaces.mcp.server`)
- Update `README.md` and tests README
- Update `.gitignore`

## [0.2.0] - 2025-08-11

### Added

- Add CLI `armenian-budget` with commands: `process`, `validate`, `download`, `extract`, `discover`, `mcp-server` (module: `armenian_budget.interfaces.cli`)
- Add minimal MCP server with tools: `list_available_data`, `get_data_schema`, `filter_budget_data`, `find_program_across_years_robust`, `search_programs_by_similarity`, `trace_program_lineage`, `register_program_equivalency`, `get_program_equivalencies`, `detect_program_patterns`, `bulk_filter_multiple_datasets`, `extract_rd_budget_robust`, `get_ministry_spending_summary` (module: `armenian_budget.interfaces.mcp.server`)
- Add FSM-based Excel parsers: 2019–2025 budget laws and 2019–2024 spending reports (modules: `armenian_budget.ingestion.parsers.excel_2019_2024`, `excel_2025`)
- Add documentation: `docs/architecture.md`, `docs/prd.md`, `docs/roadmap.md`
- Add test suite: add tests for spending reports, budget laws, and parsing

### Changed

- Move CSV output location to `data/processed/csv`
- Update project name to `armenian-budget-tools` and refresh dependencies (add `mcp`)
- Enhance `README.md` with structure and comprehensive instructions

### Fixed

- Correct extracted files parsing

## [0.1.0] - 2025-03-26

### Added

- Initial release: add standalone script `extract_budget_articles.py` to extract 2025 budget articles; include sample output under `output/2025/`

[Unreleased]: <https://github.com/gituzh/budget-am/compare/0.4.0...HEAD>
[0.4.0]: <https://github.com/gituzh/budget-am/compare/0.3.0...0.4.0>
[0.3.0]: <https://github.com/gituzh/budget-am/compare/0.2.0...0.3.0>
[0.2.0]: <https://github.com/gituzh/budget-am/compare/0.1.0...0.2.0>
[0.1.0]: <https://github.com/gituzh/budget-am/releases/tag/0.1.0>
