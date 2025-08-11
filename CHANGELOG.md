<!-- markdownlint-disable MD024 -->
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-08-11

### Added

- Add CLI `armenian-budget` with commands: `process`, `validate`, `download`, `extract`, `discover`, `mcp-server` (module: `armenian_budget.interfaces.cli`)
- Add minimal MCP server with tools: `list_available_data`, `get_data_schema`, `filter_budget_data`, `get_ministry_spending_summary`, `search_programs_by_similarity`, `detect_program_patterns`, `bulk_filter_multiple_datasets`, `extract_rd_budget_robust` (module: `armenian_budget.interfaces.mcp.server`)
- Add Excel parsers: 2019–2025 budget laws and 2019–2024 spending reports (FSM-based) (modules: `armenian_budget.ingestion.parsers.excel_2019_2024`, `excel_2025`)
- Add documentation: `docs/architecture.md`, `docs/prd.md`, `docs/roadmap.md`
- Add test suite: add tests for spending reports, budget laws, and parsing

### Fixed

- Correct extracted files parsing

### Changed

- Move CSV output location to `data/processed/csv`
- Update project name to `armenian-budget-tools` and refresh dependencies (add `mcp`)
- Enhance README (add "Program Code Extended" column notes, testing instructions, and venv setup)

## [0.1.0] - 2025-03-26

### Added

- Initial release: add standalone script `extract_budget_articles.py` to extract 2025 budget articles; include sample output under `output/2025/`

[Unreleased]: <https://github.com/gituzh/budget-am/compare/0.2.0...HEAD>
[0.2.0]: <https://github.com/gituzh/budget-am/compare/0.1.0...0.2.0>
[0.1.0]: <https://github.com/gituzh/budget-am/releases/tag/0.1.0>
