<!-- markdownlint-disable MD024 -->
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Comprehensive data validation system with 10+ validation checks (module: `armenian_budget.validation`)
  - Hierarchical totals consistency
  - Financial data completeness
  - Support for negative annual plan values in spending validation
  - Execution rate verification (≤100%)
  - Period vs annual plan comparisons
  - Required fields validation
- CLI `validate` command with multi-year support and flexible reporting (module: `armenian_budget.interfaces.cli.main`)
  - `--report` flag for Markdown validation reports
  - `--report-json` flag for JSON validation reports
  - Optional custom directory path for validation reports (via `--report` and `--report-json` flags)
- Extended data coverage through 2026 (includes 2024 MTEP, 2025 Q123 spending, 2026 budget, configurations, processed data)
- Validation reports with row-level details and context
- Documentation: `docs/validation.md` for validation usage guide
- Documentation: `docs/validation_known_issues.md` tracking source data anomalies (split state bodies from government reorganizations, formatting inconsistencies)

### Changed

- **BREAKING**: Processed data now written to `data/processed/` instead of `data/processed/csv/`
  - CSV files, overall JSON files, and validation reports now stored directly in `data/processed/`
  - MCP server and CLI automatically use new location
  - Old `csv/` directory preserved with placeholder file for GitHub users with bookmarks
- CLI standardized on `--years` across all commands (removed `--year`)
- Updated `CLAUDE.md` with code quality principles (clarity, simplicity, performance)
- Validation tolerances: `SPENDING_ABS_TOL = 5.0` AMD, `BUDGET_LAW_ABS_TOL = 0.0`
- Spending validation: period vs annual subprogram violations downgraded from error to warning
- Validation reports now use relative paths (filenames only) for portability
- Internal refactoring: renamed `_processed_csv_dir()` → `_processed_data_dir()` and `csv_dir` → `data_dir` variables where appropriate

### Fixed

- CLI `validate` command exit code handling for invalid source types
- CLI `extract` command to support all source types (budget laws, MTEP, spending reports) instead of only spending reports
- Percentage calculation comparison robustness in validation checks

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

[Unreleased]: <https://github.com/gituzh/budget-am/compare/0.3.0...HEAD>
[0.3.0]: <https://github.com/gituzh/budget-am/compare/0.2.0...0.3.0>
[0.2.0]: <https://github.com/gituzh/budget-am/compare/0.1.0...0.2.0>
[0.1.0]: <https://github.com/gituzh/budget-am/releases/tag/0.1.0>
