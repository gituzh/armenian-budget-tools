# Budget Data Testing Architecture

This directory contains a comprehensive test suite for the Armenian budget data extraction and validation system.

## Structure

### Core Configuration

- **`conftest.py`** - Shared pytest fixtures and utilities
  - Data loading helpers
  - Column mapping functions  
  - Parametrized fixtures for different data types

### Function Testing

- **`test_extraction_functions.py`** - Tests for the extraction functions themselves
  - Unit tests for utility functions
  - Row type detection testing
  - Mock data extraction testing
  - Error handling validation

### Data Validation Tests

- **`data_validation/`** - Specialized validation tests organized by data type
  - **`test_budget_law_validation.py`** - Budget law specific tests
    - Financial consistency checks
    - Non-empty CSV check
    - Program code validation
    - Grand total verification
  - **`test_spending_validation.py`** - Spending report specific tests
    - Percentage range validation
    - Logical relationship checks (period ≤ annual, etc.)
    - Cross-column consistency
    - Non-empty CSV check
  - **`test_cross_validation.py`** - Cross-file validation tests
    - Annual plans vs budget totals comparison
    - Consistency between different spending reports
    - Year-over-year structure analysis
  - **`test_data_quality.py`** - General data quality tests (if needed)

### Utilities

- **`utils/`** - Reusable test utilities
  - **`validation_helpers.py`** - Common validation functions
  - **`test_helpers.py`** - Test-specific utilities (if needed)

## Key Features

### 1. **Source Type Separation**

Tests are organized by data source type to handle different validation requirements:

- Budget laws: Basic financial consistency
- Spending reports: Additional percentage and logic validation

### 2. **Parametrized Testing**

Uses pytest fixtures to automatically run tests across all available data:

- `budget_law_data` - Only budget law files
- `spending_data` - Only spending report files  
- `all_budget_data` - All available data types

### 3. **Cross-Validation**

Advanced tests that compare:

- Spending report annual plans with budget law totals
- Consistency between different quarterly reports
- Program structure changes across years

### 4. **Flexible Column Handling**

Dynamic column detection based on source type:

- Budget laws: Single total column per level
- Spending Q1/Q12/Q123: 7 columns per level (plans, actuals, percentages)
- Spending Q1234: 4 columns per level (simplified structure)

## Running Tests

### Run all tests:

```bash
pytest tests/
```

### Run specific test categories:

```bash
# Only budget law tests
pytest tests/data_validation/test_budget_law_validation.py

# Only spending report tests  
pytest tests/data_validation/test_spending_validation.py

# Only function tests
pytest tests/test_extraction_functions.py

# Only cross-validation tests
pytest tests/data_validation/test_cross_validation.py
```

### Run tests for specific years or source types:

```bash
# Tests will automatically parametrize over available data
pytest tests/ -k "2019"
pytest tests/ -k "SPENDING_Q1"

# Show detailed messages for percentage mismatches
pytest tests/data_validation/test_spending_validation.py::test_spending_percentage_calculations -vv

# Show enriched diffs for financial consistency
pytest tests/data_validation/test_spending_validation.py::test_spending_financial_consistency -vv
```

## Validation Types

### Financial Consistency

- State body totals = sum of program totals
- Program totals = sum of subprogram totals  
- Grand total = sum of all state body totals

For spending reports, overall JSON totals are reconciled against the CSV (subprogram-level sums) with explicit tolerance constants (see Tolerances below). Failure messages include the overall value, the CSV sum, and the AMD difference.

### Spending-Specific Validation

- Percentage values in range [0, 1]
- Period plans ≤ annual plans
- Revised period plans ≤ revised annual plans
- Actual vs plan percentage calculations are correct
  - Failure messages include stored_pct, expected_pct, and absolute difference (and division-by-zero hints when applicable)

### Cross-File Validation

- Annual plans in spending reports match budget law totals
- Quarterly spending reports have consistent annual plans
- Program structures remain consistent across years

### Data Quality

- No null values in required columns
- No empty strings in text fields
- Reasonable value ranges
- Proper data types

## Tolerances

- Spending tests (`tests/data_validation/test_spending_validation.py`):
  - `SPENDING_ABS_TOL`: absolute tolerance for totals comparisons (AMD). Default: `5.0`.
  - `SPENDING_FRAC_TOL`: fractional tolerance for percentage/ratio checks. Default: `1e-3`.
  - Totals failure messages include: overall, sum, diff, tol.

- Budget Law tests (`tests/data_validation/test_budget_law_validation.py`):
  - `BUDGET_LAW_ABS_TOL`: absolute tolerance for totals. Default: `0.0` (strict after round(2)).

## Migration from Old Tests

The old monolithic test file (`test_budget_verification_OLD.py`) has been replaced with this modular structure. Key improvements:

1. **Better organization** - Tests grouped by purpose and data type
2. **Easier maintenance** - Each file has a specific focus
3. **Better error reporting** - More targeted error messages
4. **Extensibility** - Easy to add new validation types
5. **Performance** - Can run specific test subsets

## Future Enhancements

The architecture supports easy addition of:

- New source types (just add to `get_financial_columns()` and `get_percentage_columns()`)
- New validation rules (add to appropriate validation helper)
- New cross-validation checks (extend `test_cross_validation.py`)
- Performance benchmarks (add to function tests)
