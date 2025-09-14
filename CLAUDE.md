# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Installation and Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install in editable mode
pip install -U -e .

# Verify installation
armenian-budget --help
```

### Testing

```bash
# Run all tests
pytest -q

# Run specific test categories
pytest -q -k spending                    # Spending report tests only
pytest -q -k budget_law                  # Budget law tests only
pytest tests/data_validation/            # Data validation tests only

# Run with coverage
pytest --cov=.

# Show detailed test output for debugging
pytest -vv tests/data_validation/test_spending_validation.py::test_spending_percentage_calculations
```

### Data Processing

```bash
# Process all sources for a year
armenian-budget process --year 2023

# Process specific source type
armenian-budget process --year 2023 --source-type BUDGET_LAW

# Process multiple years
armenian-budget process --years 2019-2024

# Download and extract official sources
armenian-budget download --years 2019-2024 --extract

# Extract already downloaded archives
armenian-budget extract --years 2019-2024

# Build discovery index
armenian-budget discover --years 2019-2024
```

### MCP Server

```bash
# Run MCP server (stdio for Claude Desktop)
armenian-budget mcp-server --data-path ./data/processed

# Run HTTP server for testing
armenian-budget mcp-server --port 8000 --data-path ./data/processed
```

## Architecture Overview

### Core Components

- **`src/armenian_budget/ingestion/`** - Data parsing and extraction
  - `parsers/excel_2019_2024.py` - Parser for 2019-2024 format Excel files
  - `parsers/excel_2025.py` - Parser for 2025 format Excel files
  - `discovery.py` - Automatic file discovery in data directories
- **`src/armenian_budget/core/`** - Core data models and query engine
  - `enums.py` - Source types and validation levels
  - `query/` - Query planning and execution system for MCP
- **`src/armenian_budget/sources/`** - Data source management
  - `downloader.py` - Download official budget files
  - `registry.py` - Source URL and metadata management
- **`src/armenian_budget/interfaces/`** - User interfaces
  - `cli/main.py` - Command-line interface
  - `mcp/server.py` - MCP server for AI assistant integration

### Data Flow

1. **Original sources** (`data/original/`) - Downloaded files from official sources
2. **Extracted data** (`data/extracted/`) - Unarchived Excel files ready for parsing
3. **Processed data** (`data/processed/csv/`) - Clean CSVs produced by parsers
4. **Discovery index** (`data/extracted/discovery_index.json`) - Maps year/source to best file

### Source Types

- `BUDGET_LAW` - Annual budget laws (planned allocations)
- `SPENDING_Q1/Q12/Q123/Q1234` - Quarterly spending reports (actual vs planned)

Each source type has different column structures and validation requirements.

### Parser Architecture

The parsing system uses a state machine approach to handle complex Excel layouts:

- Detects row types (header, data, totals, transitions)
- Extracts hierarchical data (state body → program → subprogram)
- Handles year-specific format differences (2025 vs 2019-2024)
- Produces consistent columnar output with financial measures

### Validation System

Tests are organized by data type and validation purpose:

- **Financial consistency**: Hierarchical totals must sum correctly
- **Spending-specific**: Percentages, period ≤ annual plans, execution rates
- **Cross-validation**: Compare spending reports with budget laws
- **Data quality**: No nulls, proper ranges, correct data types

Validation tolerances are configurable:

- `SPENDING_ABS_TOL = 5.0` (AMD) for spending report totals
- `BUDGET_LAW_ABS_TOL = 0.0` for budget law totals (strict)

## Key Configuration Files

- **`config/sources.yaml`** - Official source URLs and metadata
- **`config/parsers.yaml`** - Parser configurations by year/quarter
- **`pyproject.toml`** - Package metadata and dependencies
- **`tests/conftest.py`** - Shared test fixtures and utilities

## Development Guidelines

### Parser Development

- Always handle both 2019-2024 and 2025 formats
- Use the existing state machine pattern for row type detection
- Test with real data files, not just synthetic examples
- Add proper docstrings following Google Python style guide

### Testing Requirements

- All new parsers must have validation tests
- Use parametrized fixtures from `tests/conftest.py`
- Include both unit tests and integration tests
- Maintain test tolerances for financial comparisons

### MCP Tool Development

- Follow the query engine pattern in `src/armenian_budget/core/query/`
- Return structured data for small results, file paths for large ones
- Implement size limits and pagination support
- Add proper error handling and user feedback

### Configuration Management

- Use YAML configuration files for flexibility
- Support year-specific overrides in parser configs
- Maintain checksum verification for downloaded sources
- Use discovery patterns to handle file naming variations

## File Naming Conventions

### Data Files

- Processed CSV: `{year}_{SOURCE_TYPE}.csv` (e.g., `2023_BUDGET_LAW.csv`)
- Overall JSON: `{year}_{SOURCE_TYPE}_overall.json`
- Discovery index: `discovery_index.json` in extracted root

### Test Files

- Validation tests: `test_{type}_validation.py`
- Function tests: `test_{module}_functions.py`
- Use parametrized fixtures for cross-year testing

## Important Implementation Details

### Discovery System

The discovery system automatically finds the best Excel file for each year/source combination:

- Scans `data/extracted/` directories
- Uses pattern matching from `config/parsers.yaml`
- Supports exact year/quarter matches and fallback patterns
- Caches results in `discovery_index.json`

### Error Handling

- Use warnings for data quality issues that don't prevent processing
- Use errors for structural problems that block parsing
- Provide clear context in error messages (file, sheet, row)
- Support tolerance-based comparisons for financial validation

### Column Role System

Different source types have different column meanings:

- Budget Law: `subprogram_total` (allocated amount)
- Spending Q1/Q12/Q123: `subprogram_annual_plan`, `subprogram_rev_annual_plan`, `subprogram_actual`
- Use the column registry pattern to map roles consistently

## Documentation Governance

### Always-maintained docs

- README: `README.md`
- Product requirements: `docs/prd.md`
- Architecture: `docs/architecture.md`
- Roadmap: `docs/roadmap.md`
- MCP server: `docs/mcp.md`

### Impact → required documentation updates

- **CLI commands, flags, entrypoints**
  - Impacted paths: `src/armenian_budget/interfaces/cli/**`, `pyproject.toml` ([project.scripts])
  - Update: README sections "Quickstart → CLI users", "Usage — CLI", "Installation", "Troubleshooting"

- **Python API** (public functions, parameters, return values, exceptions)
  - Impacted paths: `src/armenian_budget/**` where exported/public APIs change, especially `ingestion/parsers/**`, `interfaces/api/**`, `__init__.py` exports
  - Update: README "Usage — Python API" examples; add/remove imports and function signatures

- **MCP server tools, resources, runtime**
  - Impacted paths: `src/armenian_budget/interfaces/mcp/**`
  - Update: `docs/mcp.md` (tools list, parameters, return shapes) and README "MCP server" section

- **Output schema or column roles** (names added/removed/renamed, role mapping changes)
  - Impacted paths: `ingestion/parsers/**`, `core/query/**`, `validation/**`
  - Update: README "Data locations and column roles" and "Complete column reference"

- **Data locations, filenames, directory layout**
  - Impacted paths: storage/output code, file naming conventions, `data/**`, `processed/**`
  - Update: README "At a glance" (Where outputs go), "Usage — CLI" output notes

- **Configuration semantics** (YAML files, flags, precedence)
  - Impacted paths: `config/*.yaml`, config loaders, discovery behavior
  - Update: README "Configuration"; document new/changed keys and precedence

- **Validation rules/behavior and guarantees**
  - Impacted paths: `src/armenian_budget/validation/**`, tolerance changes
  - Update: `docs/architecture.md` (validation modules) and README "Validate outputs" notes

- **Architectural structure and responsibilities**
  - Impacted: module moves/renames, new subsystems, interface boundaries
  - Update: `docs/architecture.md` diagrams/sections and cross-links from README

### Assistant workflow expectations

- When making any impacted code change, produce matching documentation edits in the same PR
- If a change touches multiple areas (e.g., CLI + schema), update all relevant docs
- When modifying MCP tools, update both `docs/mcp.md` (detailed) and README (quickstart) consistently
- If columns or roles change, regenerate README column reference snippets

### Authoring and style rules

- Prefer relative paths in docs and examples (avoid absolute local paths)
- Use editable installation in examples: `pip install -U -e .` and explicitly activate the project venv
- Keep names consistent: repository `budget-am`, package `armenian-budget-tools`, import namespace `armenian_budget`, CLI entrypoint `armenian-budget`
- Keep examples runnable; validate CLI examples against current flags

## Release Process

This project follows semantic versioning with automated release workflows defined in `.cursor/rules/`. The release process includes:

- Branch management (release branches, hotfix branches)
- Automated changelog updates with current date
- Version consistency across `pyproject.toml` and `__init__.py`
- Proper git tagging and branch merging
