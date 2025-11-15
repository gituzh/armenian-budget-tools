# Validation Implementation Plan

> **Status:** Work in progress
> **Purpose:** Track validation system implementation step-by-step
> **Note:** This is a temporary implementation doc (underscore prefix). Delete after completion.

## Current State

**After Phase 7:**

- ✅ `validation/config.py` - Tolerance constants and severity rules
- ✅ `validation/models.py` - CheckResult, ValidationReport, to_markdown()
- ✅ `validation/checks/__init__.py` - ValidationCheck protocol
- ✅ `core/schemas.py` - Field definitions per source type (amounts, percentages, all fields)
- ✅ `validation/checks/required_fields.py` - Required fields check
- ✅ `validation/checks/empty_identifiers.py` - Empty identifier check
- ✅ `validation/checks/missing_financial_data.py` - Missing financial data check
- ✅ `validation/checks/hierarchical_totals.py` - Hierarchical totals check
- ✅ `validation/checks/negative_totals.py` - Negative totals check (all warnings)
- ✅ `validation/checks/period_vs_annual.py` - Period vs annual plan check
- ✅ `validation/checks/negative_percentages.py` - Negative percentages check
- ✅ `validation/checks/execution_exceeds_100.py` - Execution >100% check
- ✅ `validation/checks/percentage_calculation.py` - Percentage calculation check
- ✅ `validation/registry.py` - Check orchestration with ALL_CHECKS list and run_validation()
- ✅ `validation/__init__.py` - Public API exports (run_validation, print_report)
- ✅ CLI integration - `armenian-budget validate --csv` with --report flag
- ✅ Markdown report generation (grouped format)
- ✅ Old code deleted (`runner.py`, `financial.py`)
- ✅ Performance optimizations applied (55% faster)
- ✅ Redundancy cleanup - removed detect_source_type(), run_validation() accepts source_type param

**Implemented:**

- ✅ Clean module architecture
- ✅ Centralized configuration (tolerances, severity)
- ✅ Data models with helper methods
- ✅ Check interface protocol
- ✅ Core structural checks (required fields, empty IDs, missing financial data)
- ✅ Hierarchical and financial checks (hierarchical totals, negative totals)
- ✅ Spending-specific checks (period vs annual, negative percentages, execution >100%, percentage calculations)
- ✅ Check registry and runner (run_validation, print_report)
- ✅ CLI validation command (`--csv` flag)
- ✅ Markdown report generation (grouped format)
- ✅ Redundancy cleanup (removed detect_source_type)

**Still Missing:**

- ❌ Phase 7.1 C, D: Restructured reports, JSON format
- ❌ Unit and integration tests (Phase 8)
- ❌ Developer guide documentation updates (Phase 9)

**Notes:**
- Phases 3-7 tested on real 2019 and 2023 SPENDING_Q1 data
- BUDGET_LAW tolerance adjusted to 1.0 AMD to handle floating-point precision from parsers
- All negative totals are warnings (simpler than source-specific rules)
- Bug fixes applied: field existence checks in period_vs_annual.py and percentage_calculation.py
- Code simplification: empty_identifiers.py refactored to use loop (40% reduction)
- CLI validation command now uses --years/--source-type, consistent with other commands.

## Target Architecture

```bash
src/armenian_budget/validation/
├── __init__.py          # Public API exports
├── config.py            # Constants: tolerances, severity rules
├── models.py            # CheckResult, ValidationReport, detect_source_type(), to_markdown()
├── registry.py          # Check orchestration and runner
└── checks/              # Individual validation checks
    ├── __init__.py
    ├── required_fields.py
    ├── empty_identifiers.py
    ├── hierarchical_totals.py
    ├── negative_totals.py
    ├── missing_financial_data.py
    ├── period_vs_annual.py
    ├── negative_percentages.py
    ├── execution_exceeds_100.py
    └── percentage_calculation.py
```

**Design Principles:**

- **config.py** = All tunable constants (tolerances, severity rules)
- **registry.py** = Check discovery and execution logic
- **checks/*.py** = Individual check implementations (one check = one file)
- **Each check** = Self-contained, imports config for rules
- **Code quality** = Clear, succinct, comprehensive docstrings (Google style), no bloat
- **Ground-up redesign** = No backward compatibility with old validation code

## Implementation Phases

### Phase 1: Architecture Setup ✅

- [x] Delete old `validation/runner.py` and `validation/financial.py`
- [x] Create `validation/config.py` with tolerance constants and severity rules
- [x] Create `validation/models.py` with CheckResult and ValidationReport dataclasses
- [x] Create `validation/checks/__init__.py` directory
- [x] Define base check protocol/interface in `validation/checks/__init__.py`
- [x] Update `validation/__init__.py` to export new public API
- [x] Performance fixes applied (module-level constants, single-pass filtering)

**Completion Criteria:** Clean module structure, old code deleted ✅

### Phase 2: Source Type Detection ✅

- [x] Add `detect_source_type(csv_path: Path) -> SourceType` to core/utils.py (shared utility)
- [x] Export SourceType and detect_source_type from validation module for convenience

**Completion Criteria:** Can reliably identify Budget Law vs Spending vs MTEP from filename, minimal API surface ✅

### Phase 3: Core Structural Checks ✅

- [x] Implement `checks/required_fields.py` (complete schema from data_schemas.md)
- [x] Implement `checks/empty_identifiers.py` (with source-specific severity)
- [x] Implement `checks/missing_financial_data.py` (NEW - check nulls in all financial fields)
- [x] Create `core/schemas.py` for centralized field definitions
- [x] Tested on real 2019/2026 data - all passing, failure detection working

**Completion Criteria:** Required fields, empty IDs, missing data checks implemented (registry integration in Phase 6) ✅

### Phase 4: Hierarchical & Financial Checks ✅

- [x] Add `get_amount_fields()` to core/schemas.py (amounts only, excludes percentages)
- [x] Implement `checks/hierarchical_totals.py` (source-specific tolerances)
  - [x] Check overall JSON vs state body sums
  - [x] Check state body vs program sums
  - [x] Check program vs subprogram sums
- [x] Implement `checks/negative_totals.py` (all warnings for all levels)
  - [x] Check overall JSON
  - [x] Check state body, program, subprogram CSV rows
- [x] Tested on real 2019 SPENDING_Q1 (all hierarchical checks pass with 5.0 tolerance)
- [x] Detected real negative values in 2019 data (warnings at all levels)

**Completion Criteria:** Hierarchical and negative checks implemented (registry integration in Phase 6) ✅

**Notes:**

- BUDGET_LAW tolerance set to 1.0 AMD to handle floating-point precision from parsers
- All negative totals are warnings (all source types, all levels) - negatives may be legitimate budget corrections/adjustments, simpler to review all as warnings

### Phase 5: Spending-Specific Checks ✅

- [x] Add `get_percentage_fields()` to core/schemas.py
- [x] Implement `checks/period_vs_annual.py` (Q1/Q12/Q123 only)
  - [x] period_plan ≤ annual_plan
  - [x] rev_period_plan ≤ rev_annual_plan
- [x] Implement `checks/negative_percentages.py` (hierarchy-specific severity)
- [x] Implement `checks/execution_exceeds_100.py` (warning-level check)
- [x] Implement `checks/percentage_calculation.py` (all hierarchy levels, 0.1% tolerance)
  - [x] actual_vs_rev_annual_plan = actual / rev_annual_plan
  - [x] actual_vs_rev_period_plan = actual / rev_period_plan (Q1/Q12/Q123)
- [x] Tested on real 2019 SPENDING_Q1 data

**Completion Criteria:** All spending checks implemented (registry integration in Phase 6) ✅

**Test Results:**

*2019 SPENDING_Q1* (42 passed, 5 failed - 1 error, 4 warnings):

- Period ≤ Annual: 2 violations at subprogram level
- Negative Percentages: All passed
- Execution > 100%: 4 instances at subprogram level (warnings)
- Percentage Calculation: All passed

*2023 SPENDING_Q1* (41 passed, 6 failed - 2 errors, 4 warnings):

- Period ≤ Annual: 12 violations at program level, 6 at subprogram level
- Negative Totals: 30 negative program values, 5 negative subprogram values (warnings)
- Execution > 100%: 10 instances at program level, 3 at subprogram level (warnings)
- All other checks: Passed

**Bug Fixes Applied:**

- Fixed `period_vs_annual.py`: Added field existence checks to avoid masking missing fields with `.get(field, 0)` default
- Fixed `percentage_calculation.py`: Check all three fields (percentage, numerator, denominator) exist before calculation
- Refactored `empty_identifiers.py`: Use loop instead of repetition (~40% code reduction)

### Phase 6: Registry and Runner ✅

- [x] Create `validation/registry.py` with ALL_CHECKS list
- [x] Implement `run_validation()` function
  - [x] Filter checks by source type
  - [x] Execute all applicable checks
  - [x] Aggregate results into ValidationReport
- [x] Implement `print_report()` function for console output
- [x] Update CLI `cmd_validate()` to use new registry
- [x] Update `validation/__init__.py` to export run_validation and print_report
- [x] Tested on real 2019 and 2023 SPENDING_Q1 data

**Completion Criteria:** CLI validates CSV using new check registry ✅

**Test Results:**

*2019 SPENDING_Q1* (47 total checks, 42 passed, 5 failed):

- 2 errors: period_vs_annual violations at subprogram level
- 12 warnings: negative totals (state_body, program, subprogram), execution >100% at subprogram level

*2023 SPENDING_Q1* (47 total checks, 41 passed, 6 failed):

- 18 errors: period_vs_annual violations at program (12) and subprogram (6) levels
- 48 warnings: negative totals (35 total), execution >100% (13 total)

### Phase 7: Report Generation ✅

- [x] Add `ValidationReport.to_markdown() -> str` method to models.py (~108 lines)
  - [x] Format: check status (✅/❌/⚠️), counts, failure details
  - [x] Include summary section (total errors, warnings)
  - [x] Header with file info and timestamp
  - [x] Grouped by pass/fail status for easy scanning
  - [x] Footer with link to docs/validation.md
- [x] Update CLI `cmd_validate()` to accept `--report` flag
  - [x] `--report` (default location: {csv_path}_validation.md)
  - [x] `--report path/to/custom.md` (custom path)
  - [x] Call `report.to_markdown()` to generate content
  - [x] Create parent directories if needed
  - [x] Log output path
- [x] Update CLI help text and argument parser (nargs="?", const=True)
- [x] Tested on real 2019 and 2023 SPENDING_Q1 data

**Completion Criteria:** `armenian-budget validate --csv X.csv --report` creates Markdown file ✅

**Test Results:**

*Default Location Test* (2019_SPENDING_Q1.csv):

- Created: `data/processed/csv/2019_SPENDING_Q1_validation.md`
- Format: Clean markdown with emoji indicators, proper sections
- Size: ~1KB for report with 47 checks (42 passed, 5 failed)

*Custom Location Test* (2023_SPENDING_Q1.csv):

- Created: `/tmp/test_validation_report.md`
- Format: Same clean structure
- Size: ~1.8KB for report with 47 checks (41 passed, 6 failed)

*Console-Only Test* (no --report flag):

- Console output works as before
- No markdown file created (backward compatible)

### Phase 7.1: Corrective Updates

**Issues Identified:**

1. CLI argument inconsistency: `--csv` doesn't match other commands (`--years`, `--source-type`)
2. Markdown report groups checks and mixes warnings/errors - need separate sections
3. Missing JSON report format

**Changes Required:**

**A. Refactor `run_validation()` signature: ✅**

- [x] Change from `(df, csv_path, source_type)` to `(year: int, source_type: SourceType, processed_root: Path)`
- [x] Construct paths internally, load CSV and JSON internally
- [x] Update docstring and examples

**B. Update CLI: ✅**

- [x] Replace `--csv` with `--years`, `--source-type`, `--processed-root`
- [x] Use `_parse_years_arg()` for year parsing
- [x] Loop over years, call `run_validation(year, source_type, processed_root)` for each
- [x] Remove CSV loading (now in run_validation)

**C. Restructure `ValidationReport.to_markdown()`:**

- [ ] Create three separate sections: Passed, Warnings, Errors
- [ ] List each CheckResult individually (not grouped by check_id)
- [ ] For failed checks, display all messages showing entity names and values (not just "X rows")

**D. Add `ValidationReport.to_json()`:**

- [ ] Add `--report-json` flag support
- [ ] Mirror markdown structure (metadata, summary, passed_checks, warnings, errors)

**E. Update `validation/__init__.py`: ✅**

- [x] Update usage example with new run_validation signature

**Documentation:** See docs/validation.md, README.md, CLAUDE.md for CLI syntax and report formats (already updated in docs-only phase).

**Completion Criteria:**

- CLI accepts --years/--source-type (not --csv), consistent with process/download/discover commands
- Markdown reports have three sections (Passed/Warnings/Errors), checks listed individually
- JSON reports available with --report-json flag
- Tested on 2019 and 2023 data

### Phase 8: Testing and Validation

**A. Unit Tests for Validation System (Phases 1-5):**

- [ ] Create `tests/validation/` directory
- [ ] `test_schemas.py`: Test get_required_fields(), get_financial_fields(), get_amount_fields(), get_percentage_fields() for all source types
- [ ] `test_config.py`: Test get_tolerance_for_source(), get_severity()
- [ ] `test_required_fields_check.py`: Unit test with missing/present fields (synthetic data)
- [ ] `test_empty_identifiers_check.py`: Unit test with empty/non-empty identifiers (synthetic data)
- [ ] `test_missing_financial_data_check.py`: Unit test with null/non-null values (synthetic data)
- [ ] `test_hierarchical_totals_check.py`: Unit test with correct/incorrect sums (synthetic data)
- [ ] `test_negative_totals_check.py`: Unit test with positive/negative values (synthetic data)
- [ ] `test_period_vs_annual_check.py`: Unit test with period vs annual violations (synthetic data)
- [ ] `test_negative_percentages_check.py`: Unit test with negative/positive percentages (synthetic data)
- [ ] `test_execution_exceeds_100_check.py`: Unit test with execution >100% (synthetic data)
- [ ] `test_percentage_calculation_check.py`: Unit test with correct/incorrect calculations (synthetic data)
- [ ] `test_all_checks_integration.py`: Integration test running all checks on real data using existing fixtures

**B. Tests for Registry and Runner (Phase 6):**

- [ ] `test_registry.py`: Test check filtering by source type, run_validation() execution, ValidationReport aggregation

**C. Tests for Report Generation (Phase 7):**

- [ ] `test_report.py`: Test to_markdown() format, summary sections, error/warning counts

**D. CLI Integration Tests:**

- [ ] Test `armenian-budget validate --years X --source-type Y` command execution
- [ ] Test `--report` and `--report-json` flags create files correctly
- [ ] Test CLI error handling (missing files, invalid source types)

**E. Delete Redundant Old Validation Tests:**

- [ ] Delete redundant tests from `tests/data_validation/test_spending_validation.py`:
  - Delete: test_spending_financial_consistency, test_spending_data_quality, test_spending_percentage_ranges, test_spending_logical_relationships
  - Delete: test_spending_has_all_required_columns, test_spending_percentage_calculations, test_spending_no_negative_percentages
  - Delete: test_spending_revised_vs_original_plans, test_spending_overall_matches_csv
  - Delete: test_spending_actual_vs_plans_reasonableness, test_spending_quarterly_progression (warning-only tests)
  - Keep: test_spending_csv_non_empty (parser test - to be reviewed)
- [ ] Delete redundant tests from `tests/data_validation/test_budget_law_validation.py`:
  - Delete: test_budget_law_financial_consistency, test_budget_law_data_quality
  - Delete: test_budget_law_grand_total_consistency, test_budget_law_no_negative_totals
  - Keep: test_budget_law_csv_non_empty, test_budget_law_program_codes_and_names_match, test_budget_law_program_distribution, test_budget_law_program_codes_format (parser tests - to be reviewed)
- [ ] Delete redundant tests from `tests/data_validation/test_mtep_validation.py`:
  - Delete: test_mtep_rollups_and_required_columns, test_mtep_overall_matches_csv, test_mtep_no_negative_totals
  - Keep: test_mtep_csv_non_empty, test_mtep_program_codes_integer, test_mtep_program_codes_and_names_match (parser tests - to be reviewed)
- [ ] Delete `tests/utils/validation_helpers.py` entirely

**F. Review and Decide on Remaining Parser Tests:**

- [ ] Review csv_non_empty tests (3 tests across files): Decide if these should move to `tests/parser/` or stay/delete
- [ ] Review program_codes tests (5 tests): Decide if these should become validation checks or stay as parser tests
- [ ] Review program_distribution test: Consider if this should become a validation check
- [ ] If any become validation checks: Add corresponding pytest tests

**G. Test Coverage and Quality:**

- [ ] Validate test coverage >= 80% for validation module
- [ ] Update `tests/conftest.py` fixtures if needed
- [ ] Run full test suite and ensure all tests pass

**Test Approach:**

- Unit tests use synthetic DataFrames (3-10 rows) following pattern from test_mtep_validation.py:22-62
- Integration tests use existing fixtures (all_budget_data, spending_data, budget_law_data)

**Completion Criteria:** All validation code has tests, old redundant tests deleted, remaining tests reviewed and relocated appropriately, test coverage maintained

### Phase 9: Documentation and Cleanup

- [ ] Update `docs/developer_guide.md` validation section
  - [ ] New architecture (config, registry, checks)
  - [ ] How to add new checks
  - [ ] How to tune severity/tolerances
- [ ] Verify all docstrings follow Google Python style guide
- [ ] Code review for clarity and succinctness
- [ ] Delete `_validation_impl.md` (this file)

**Completion Criteria:** Documentation matches implementation, code is clean and well-documented

## Progress Tracking

**Started:** 2025-10-27
**Current Phase:** Phase 7.1 (Corrective Updates)
**Completed Phases:** Phase 1 ✅, Phase 2 ✅, Phase 3 ✅, Phase 4 ✅, Phase 5 ✅, Phase 6 ✅, Phase 7 ✅
**Blockers:** None

## Architecture Decisions Log

### Decision 1: No YAML Configuration (2025-10-27)

**Rationale:** Tolerances and severity rules as Python constants in `config.py` (not YAML):

- Simpler to maintain
- Version controlled
- Type-safe, IDE support
- Can externalize later if needed
- Matches incremental evolution principle

### Decision 2: Centralized Severity Config (2025-10-27)

**Rationale:** All severity rules in `config.py`, imported by checks:

- Easy to tune based on real validation results
- Single file shows all rules at once
- Better for workflow: run validation → open config.py → adjust rules → commit

### Decision 3: One Check Per File (2025-10-27)

**Rationale:** Each validation check in separate `checks/*.py` file:

- Clear separation of concerns
- Easy to test in isolation
- Matches validation.md structure (one section per check type)
- Easier to review and maintain

### Decision 4: Ground-Up Redesign (2025-10-27)

**Rationale:** No backward compatibility with old validation code:

- Delete old `runner.py` and `financial.py` immediately (Phase 1)
- Design clean interfaces from scratch
- Focus on clarity and succinctness over migration path
- Comprehensive docstrings (Google Python style guide)
- No bloat, no legacy patterns

### Decision 5: Minimal API Surface (2025-10-27)

**Rationale:** Keep validation module minimal and focused:

- Source type detection via filename parsing (no JSON modification needed)
- Report generation as method on ValidationReport (no separate report.py file)
- Remove `get_passed_checks()` from public API (inline in summary())
- Each utility lives where it's most relevant (detect_source_type in models.py)

**Benefits:**

- Fewer files to maintain (14 vs 15 - removed report.py)
- Clearer responsibility (models.py owns all data model logic)
- No unnecessary parser modifications
- Simpler for users (fewer imports, methods on objects)

### Decision 6: All Negative Totals as Warnings (2025-10-31)

**Rationale:** Treat all negative totals as warnings (all source types, all hierarchy levels):

- Negative values can represent legitimate budget corrections or adjustments in any context (not just spending reports)
- Simpler implementation: single severity rule instead of source-type-specific logic
- Easier to maintain: no special cases or conditional severity mapping
- Better user experience: consistent behavior across all data types

**Benefits:**

- Simpler code in `config.py` (single `NEGATIVE_TOTALS_SEVERITY` dict)
- No source-type-aware severity logic needed in checks
- Consistent messaging: all negatives flagged for review, none treated as critical errors
- Real-world validated: 2019 data shows negatives occur and may be legitimate

**Implementation:** See Phase 4 notes for details.

## Notes

- Source type detection needs to work before hierarchy-specific checks
- Test with real 2019-2025 data as each phase completes
- Markdown report format should match validation.md structure for consistency
- Every function/class needs comprehensive docstring
- Keep code succinct: prefer simple, clear logic over complex abstractions
