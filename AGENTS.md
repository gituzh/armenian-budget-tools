# Repository Guidelines

**Documentation Philosophy:** Keep documentation minimal and purposeful. Document only what cannot be understood from code alone. All docs serve both humans and AI agents who need context to understand, extend, and audit the system efficiently.

## Project Structure & Module Organization

Core library lives in `src/armenian_budget/`, including ingestion parsers, CLI interfaces under `interfaces/cli`, and validations in `validation/`. Add new source-specific logic inside the matching `ingestion/` module and expose CLI entry points via `interfaces/cli/`.
Data staging uses `data/original/` for downloaded archives, `data/extracted/` for unpacked spreadsheets with discovery index at `discovery_index.json`, and `data/processed/csv/` for analyst-ready outputs. Config templates reside in `config/` (notably `config/parsers.yaml`), while notebooks and docs supporting research live in `notebooks/` and `docs/`.
Tests mirror the runtime layout: `tests/test_extraction_functions.py` for function checks, `tests/data_validation/` for dataset rules, and shared fixtures in `tests/conftest.py`. Keep helper utilities in `tests/utils/`.

## Build, Test, and Development Commands

Create a fresh virtualenv and install the project in editable mode with dev dependencies before running anything:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U -e ".[dev]"  # Installs package + pytest, pytest-cov, jupyter
```

Use the CLI to exercise the pipeline locally:

```bash
armenian-budget process --years 2023 --source-type BUDGET_LAW
```

Run the automated suite and coverage checks:

```bash
pytest -q
pytest --cov=armenian_budget
```

## Coding Style & Naming Conventions

Target Python 3.10+. Follow Black-style formatting (4-space indent, ~88 character lines) and type-hint public functions, as seen in `interfaces/cli/main.py`. Modules and functions use snake_case (`flatten_budget_excel_2025`), classes use PascalCase, and constants are UPPER_SNAKE_CASE. Log through the standard `logging` facade (configured via `colorlog`) and group CLI options in dedicated subcommands. Run `ruff check src/ tests/` and `black src/ tests/` before opening a PR.

## Testing Guidelines

Tests rely on pytest parametrization across real budget datasets. Mirror new code with targeted tests in the corresponding folder (e.g., add MTEP validations under `tests/data_validation/`). Reference fixtures from `tests/utils/` rather than hard-coding paths. For selective runs use `pytest -k spending` or call a module directly such as `pytest tests/data_validation/test_budget_law_validation.py -vv`. Maintain coverage for new pathways and adjust tolerances responsibly (`SPENDING_ABS_TOL` lives beside the validations).

## Commit & Pull Request Guidelines

Commits follow Conventional style (`feat(cli): add --source-type filter`). Keep messages scoped and descriptive; avoid mixing unrelated changes. PRs should describe motivation, summarize pipeline impacts, link any tracked issue, and attach CLI or test output snippets when behavior changes. Flag data migrations or config updates so reviewers can rerun `armenian-budget` safely.
