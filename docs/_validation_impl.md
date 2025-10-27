# Validation Implementation Plan

> **Status:** Work in progress
> **Purpose:** Track validation system implementation step-by-step
> **Note:** This is a temporary implementation doc (underscore prefix). Delete after completion.

## Current State

**Existing (Early Draft):**

- `validation/financial.py` - Basic validation functions (165 lines)
- `validation/runner.py` - Orchestration with CheckResult/ValidationReport (424 lines)
- CLI integration at `interfaces/cli/main.py:323-338` (console summary only)

**What Works:**

- ✅ Basic hierarchical totals check
- ✅ Percentage range validation (0-1)
- ✅ Period ≤ annual plan checks
- ✅ Negative totals detection
- ✅ Console output via `print_report()`

**What's Missing:**

- ❌ Source type detection (Budget Law vs Spending vs MTEP)
- ❌ Complete validation checks per validation.md spec
- ❌ Hierarchy-level-specific severity
- ❌ Overall JSON validation
- ❌ Markdown report generation
- ❌ CLI --report flag support

## Target Architecture

```bash
src/armenian_budget/validation/
├── __init__.py          # Public API exports
├── config.py            # Constants: tolerances, severity rules
├── registry.py          # Check orchestration and runner
├── models.py            # CheckResult, ValidationReport
├── report.py            # Markdown report generation
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

**Completion Criteria:** Clean module structure, old code deleted ✅

### Phase 2: Source Type Detection

- [ ] Add `source_type` field to overall JSON during processing
- [ ] Create `detect_source_type()` function (fallback to filename parsing)
- [ ] Update ValidationReport to store source_type
- [ ] Add SourceType import to validation module

**Completion Criteria:** Can reliably identify Budget Law vs Spending vs MTEP

### Phase 3: Core Structural Checks

- [ ] Implement `checks/required_fields.py` (complete schema from data_schemas.md)
- [ ] Implement `checks/empty_identifiers.py` (with source-specific severity)
- [ ] Implement `checks/missing_financial_data.py` (NEW - check nulls in all financial fields)
- [ ] Update registry to run these checks

**Completion Criteria:** Required fields, empty IDs, missing data checks pass on test data

### Phase 4: Hierarchical & Financial Checks

- [ ] Implement `checks/hierarchical_totals.py` (source-specific tolerances)
  - [ ] Check overall JSON vs state body sums
  - [ ] Check state body vs program sums
  - [ ] Check program vs subprogram sums
- [ ] Implement `checks/negative_totals.py` (with hierarchy-level severity)
  - [ ] Check overall JSON
  - [ ] Check state body, program, subprogram CSV rows
- [ ] Update registry to run these checks

**Completion Criteria:** Hierarchical and negative checks work across all hierarchy levels

### Phase 5: Spending-Specific Checks

- [ ] Implement `checks/period_vs_annual.py`
  - [ ] period_plan ≤ annual_plan
  - [ ] rev_period_plan ≤ rev_annual_plan
- [ ] Implement `checks/negative_percentages.py` (hierarchy-specific severity)
- [ ] Implement `checks/execution_exceeds_100.py` (warning-level check)
- [ ] Implement `checks/percentage_calculation.py` (all hierarchy levels)
  - [ ] actual_vs_rev_annual_plan = actual / rev_annual_plan
  - [ ] actual_vs_rev_period_plan = actual / rev_period_plan
- [ ] Update registry to conditionally run on spending sources only

**Completion Criteria:** All spending checks pass on Q1/Q12/Q123/Q1234 test data

### Phase 6: Registry and Runner

- [ ] Create `validation/registry.py` with ALL_CHECKS list
- [ ] Implement `run_validation()` function
  - [ ] Filter checks by source type
  - [ ] Execute all applicable checks
  - [ ] Aggregate results into ValidationReport
- [ ] Update CLI to use new registry

**Completion Criteria:** CLI validates CSV using new check registry

### Phase 7: Report Generation

- [ ] Create `validation/report.py`
  - [ ] `generate_markdown_report(ValidationReport) -> str`
  - [ ] Format: check status (✅/❌/⚠️), counts, failure details
  - [ ] Include summary section (total errors, warnings)
- [ ] Update CLI `cmd_validate()` to accept `--report` flag
  - [ ] `--report` (default location: {csv_path}_validation.md)
  - [ ] `--report path/to/custom.md` (custom path)
- [ ] Update CLI help text and argument parser

**Completion Criteria:** `armenian-budget validate --csv X.csv --report` creates Markdown file

### Phase 8: Testing and Validation

- [ ] Add unit tests for each check in `checks/`
- [ ] Add integration tests using real 2023/2024 data
- [ ] Validate against validation.md spec (all checks implemented)
- [ ] Update `tests/conftest.py` fixtures if needed
- [ ] Update/replace existing validation tests (no backward compat needed)

**Completion Criteria:** All tests pass, coverage maintained

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
**Current Phase:** Phase 2
**Completed Phases:** Phase 1 ✅
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

## Notes

- Source type detection needs to work before hierarchy-specific checks
- Test with real 2019-2025 data as each phase completes
- Markdown report format should match validation.md structure for consistency
- Every function/class needs comprehensive docstring
- Keep code succinct: prefer simple, clear logic over complex abstractions
