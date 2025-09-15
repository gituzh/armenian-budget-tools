# Python API Reference

This document provides comprehensive reference information for the Armenian Budget Tools Python API.

## Table of Contents

- [Python API Reference](#python-api-reference)
  - [Table of Contents](#table-of-contents)
  - [Core API Functions](#core-api-functions)
    - [Data Processing Functions](#data-processing-functions)
      - [`flatten_budget_excel_2019_2024(path, source_type)`](#flatten_budget_excel_2019_2024path-source_type)
      - [`flatten_budget_excel_2025(path)`](#flatten_budget_excel_2025path)
    - [Validation Functions](#validation-functions)
      - [`validate_hierarchical_totals(data, tolerance=0.01)`](#validate_hierarchical_totalsdata-tolerance001)
      - [`validate_no_negative_amounts(data)`](#validate_no_negative_amountsdata)
    - [Data Access Functions](#data-access-functions)
      - [`discover_best_file(year, source_type)`](#discover_best_fileyear-source_type)
  - [CLI Command Reference](#cli-command-reference)
    - [Data Management Commands](#data-management-commands)
      - [`armenian-budget download`](#armenian-budget-download)
      - [`armenian-budget extract`](#armenian-budget-extract)
    - [Processing Commands](#processing-commands)
      - [`armenian-budget process`](#armenian-budget-process)
    - [Validation Commands](#validation-commands)
      - [`armenian-budget validate`](#armenian-budget-validate)
    - [Analysis Commands](#analysis-commands)
      - [`armenian-budget export`](#armenian-budget-export)
      - [`armenian-budget mcp-server`](#armenian-budget-mcp-server)
  - [MCP Server Tools](#mcp-server-tools)
    - [Data Access Tools](#data-access-tools)
      - [`list_available_data()`](#list_available_data)
      - [`get_data_schema(year, source_type)`](#get_data_schemayear-source_type)
      - [`filter_budget_data_enhanced(year, source_type, **filters)`](#filter_budget_data_enhancedyear-source_type-filters)
    - [Analysis Tools](#analysis-tools)
      - [`get_ministry_spending_summary(year, ministry)`](#get_ministry_spending_summaryyear-ministry)
      - [`get_ministry_comparison(years, ministry_pattern, metrics)`](#get_ministry_comparisonyears-ministry_pattern-metrics)
      - [`get_budget_distribution(year, groupby, top_n)`](#get_budget_distributionyear-groupby-top_n)
    - [Configuration Tools](#configuration-tools)
      - [`get_dataset_overall(year, source_type)`](#get_dataset_overallyear-source_type)
  - [Configuration Reference](#configuration-reference)
    - [Sources Configuration](#sources-configuration)
    - [Parser Configuration](#parser-configuration)
    - [Validation Configuration](#validation-configuration)
  - [Error Handling](#error-handling)
    - [Exception Types](#exception-types)
      - [`ParseError`](#parseerror)
      - [`LabelMismatchError`](#labelmismatcherror)
      - [`ValidationError`](#validationerror)
      - [`SourceNotFoundError`](#sourcenotfounderror)
    - [Error Codes](#error-codes)
  - [Type Definitions](#type-definitions)
    - [Core Types](#core-types)
      - [`SourceType`](#sourcetype)
      - [`ValidationResult`](#validationresult)
      - [`ProcessingResult`](#processingresult)
    - [Enum Types](#enum-types)
      - [`ValidationLevel`](#validationlevel)
      - [`OutputFormat`](#outputformat)

## Core API Functions

### Data Processing Functions

#### `flatten_budget_excel_2019_2024(path, source_type)`

Parse budget law or spending report Excel files from 2019-2024 format.

**Parameters:**

- `path` (str): Path to the Excel file
- `source_type` (SourceType): Type of source data (BUDGET_LAW, SPENDING_Q1, etc.)

**Returns:**

- `df` (DataFrame): Flattened subprogram-level DataFrame
- `overall` (dict): Summary totals from Excel
- `rowtype_stats` (dict): Parsing diagnostics for row types
- `statetrans_stats` (dict): Parsing diagnostics for state transitions

**Example:**

```python
from armenian_budget.ingestion.parsers import flatten_budget_excel_2019_2024, SourceType

df, overall, rowtype_stats, statetrans_stats = flatten_budget_excel_2019_2024(
    "./data/extracted/budget_laws/2023/file.xlsx",
    SourceType.BUDGET_LAW
)
```

#### `flatten_budget_excel_2025(path)`

Parse budget law Excel files from 2025 format.

**Parameters:**

- `path` (str): Path to the Excel file

**Returns:**

- `df` (DataFrame): Flattened subprogram-level DataFrame
- `overall` (float): Total budget amount
- Additional parsing diagnostics

**Example:**

```python
from armenian_budget.ingestion.parsers import flatten_budget_excel_2025

df, overall, *_ = flatten_budget_excel_2025(
    "./data/extracted/budget_laws/2025/file.xlsx"
)
```

### Validation Functions

#### `validate_hierarchical_totals(data, tolerance=0.01)`

Validate that state body totals equal the sum of program totals.

**Parameters:**

- `data` (DataFrame): Budget data to validate
- `tolerance` (float): Acceptable tolerance for sum differences

**Returns:**

- `ValidationResult`: Validation results with pass/fail status and error details

#### `validate_no_negative_amounts(data)`

Validate that budget amounts are not negative.

**Parameters:**

- `data` (DataFrame): Budget data to validate

**Returns:**

- `ValidationResult`: Validation results

### Data Access Functions

#### `discover_best_file(year, source_type)`

Automatically discover the best input file for processing.

**Parameters:**

- `year` (int): Year of data to process
- `source_type` (SourceType): Type of source data

**Returns:**

- `FileInfo`: Information about the discovered file including path and metadata

## CLI Command Reference

### Data Management Commands

#### `armenian-budget download`

Download official budget data sources.

```bash
# Download specific year and source type
armenian-budget download --year 2023 --source-type budget_law

# Download all available sources
armenian-budget download --all --update

# Download with explicit paths
armenian-budget download --years 2019-2024 \
  --original-root ./data/original \
  --extracted-root ./data/extracted \
  --extract
```

#### `armenian-budget extract`

Extract downloaded archives.

```bash
# Extract archives for specific years
armenian-budget extract --years 2019-2024

# Auto-detect available years
armenian-budget extract
```

### Processing Commands

#### `armenian-budget process`

Process budget data through the complete pipeline.

```bash
# Process all sources for a year
armenian-budget process --year 2019

# Process specific source type
armenian-budget process --year 2019 --source-type BUDGET_LAW

# Process multiple years
armenian-budget process --years 2019,2020,2021
armenian-budget process --years 2019-2021

# Process with explicit input file
armenian-budget process --year 2023 --source-type BUDGET_LAW \
  --input ./data/extracted/budget_laws/2023/file.xlsx

# Advanced processing options
armenian-budget process --year 2023 --source-type BUDGET_LAW \
  --deep-validate \
  --extracted-root ./data/extracted \
  --parsers-config ./config/parsers.yaml \
  --processed-root ./data/processed
```

### Validation Commands

#### `armenian-budget validate`

Validate processed budget data.

```bash
# Validate all processed data
armenian-budget validate --all --level strict

# Validate specific year
armenian-budget validate --year 2023 --output validation_report.json

# Validate individual CSV file
armenian-budget validate --csv ./data/processed/csv/2023_BUDGET_LAW.csv
```

### Analysis Commands

#### `armenian-budget export`

Export processed data in different formats.

```bash
# Export to Parquet format
armenian-budget export --format parquet --years 2020-2025

# Export with filters
armenian-budget export --format csv \
  --filter "state_body=Ministry of Education"
```

#### `armenian-budget mcp-server`

Start MCP server for AI-assisted analysis.

```bash
# Start with default data path
armenian-budget mcp-server --port 8000 --data-path ./data/processed

# Start HTTP server
armenian-budget mcp-server --http --host 127.0.0.1 --port 8765

# Start HTTPS server (requires certificates)
armenian-budget mcp-server --https --host 127.0.0.1 --port 8765
```

## MCP Server Tools

### Data Access Tools

#### `list_available_data()`

Return inventory of available processed datasets.

**Returns:**

```json
{
  "budget_laws": ["2019", "2020", "2021", "2022", "2023", "2024", "2025"],
  "spending_reports": { "2019": ["Q1", "Q12", "Q123", "Q1234"] },
  "formats": ["csv", "parquet"],
  "last_updated": "2024-01-15"
}
```

#### `get_data_schema(year, source_type)`

Return column names and data types for a dataset.

**Parameters:**

- `year` (int): Year of data
- `source_type` (str): Type of source data

**Returns:**

```json
{
  "columns": ["state_body", "program_code", "program_name", "subprogram_total"],
  "dtypes": {
    "state_body": "string",
    "program_code": "int64",
    "subprogram_total": "float64"
  },
  "shape": [1250, 13],
  "file_path": "/path/to/dataset.csv"
}
```

#### `filter_budget_data_enhanced(year, source_type, **filters)`

Filter budget data with flexible output options.

**Parameters:**

- `year` (int): Year of data
- `source_type` (str): Type of source data
- `force_file_output` (bool): Force file output for large results
- `max_rows` (int): Limit number of rows
- `**filters`: Column-based filters (state_body, program_codes, min_amount, etc.)

**Returns:**

- Inline data for small results or file path for large results

### Analysis Tools

#### `get_ministry_spending_summary(year, ministry)`

Get aggregated spending summary for a ministry.

**Parameters:**

- `year` (int): Year of data
- `ministry` (str): Ministry/state body name

**Returns:**

```json
{
  "ministry": "Ministry of Education",
  "year": 2023,
  "total_allocated": 45600000.0,
  "total_actual": 42100000.0,
  "execution_rate": 0.923,
  "program_count": 8,
  "subprogram_count": 34,
  "top_programs": [
    { "code": 1201, "name": "General Education", "amount": 28500000.0 },
    { "code": 1202, "name": "Higher Education", "amount": 12400000.0 }
  ]
}
```

#### `get_ministry_comparison(years, ministry_pattern, metrics)`

Compare ministry performance across years.

**Parameters:**

- `years` (List[int]): Years to compare
- `ministry_pattern` (str): Pattern to match ministry names
- `metrics` (List[str]): Metrics to compare (allocated, actual, etc.)

#### `get_budget_distribution(year, groupby, top_n)`

Get budget distribution analysis.

**Parameters:**

- `year` (int): Year of data
- `groupby` (str): Grouping column (state_body, program, etc.)
- `top_n` (int): Number of top items to return

### Configuration Tools

#### `get_dataset_overall(year, source_type)`

Get overall totals from processed datasets.

**Parameters:**

- `year` (int, optional): Specific year or null for all
- `source_type` (str, optional): Specific source type or null for all

**Returns:**

```json
{
  "overalls": {
    "2019": {
      "BUDGET_LAW": { "total_budget": 1234567890.0 },
      "SPENDING_Q12": {
        "total_annual_plan": 1234567890.0,
        "total_rev_annual_plan": 1234567890.0,
        "total_actual": 1150000000.0,
        "total_actual_vs_rev_annual_plan": 0.93
      }
    }
  },
  "years": [2019],
  "source_types": ["BUDGET_LAW", "SPENDING_Q12"],
  "count": 2
}
```

## Configuration Reference

### Sources Configuration

Configuration file: `config/sources.yaml`

```yaml
sources:
  - name: "2025_budget_law"
    year: 2025
    source_type: "budget_law"
    url: "https://www.gov.am/files/docs/4850.zip"
    file_format: "zip"
    description: "2025 State Budget Law attachments"

  - name: "2024_spending_q12"
    year: 2024
    source_type: "spending_q12"
    url: "https://minfin.am/website/images/files/72393188f3b5505559d18a66a6a6b89ffdfc829a433af986e6cf72b369d86751.rar"
    file_format: "rar"
    description: "2024 Q1-Q2 Spending Report"
```

### Parser Configuration

Configuration file: `config/parsers.yaml`

```yaml
# Global patterns
patterns:
  budget_law: "ծրագիր.*միջոցառում"
  spending: "ծրագիր.*միջոցառում"

# Year-specific overrides
overrides:
  "2025":
    budget_law: "extended.*pattern"
```

### Validation Configuration

Configuration file: `config/validation_rules.yaml`

```yaml
rules:
  hierarchical_tolerance: 0.01
  execution_rate_bounds: [0.0, 2.0]
  negative_amount_check: true
  cross_year_consistency: true
```

## Error Handling

### Exception Types

#### `ParseError`

Raised when Excel file parsing fails.

```python
try:
    df, overall, *_ = flatten_budget_excel_2019_2024(path, source_type)
except ParseError as e:
    print(f"Parsing failed: {e}")
```

#### `LabelMismatchError`

Raised when expected Armenian text labels are not found.

```python
try:
    # Processing logic
except LabelMismatchError as e:
    print(f"Label mismatch: {e}")
    print("Try adjusting tolerance in config/parsers.yaml")
```

#### `ValidationError`

Raised when business rule validation fails.

```python
try:
    result = validate_hierarchical_totals(data)
    if not result.passed:
        print(f"Validation errors: {result.errors}")
except ValidationError as e:
    print(f"Validation failed: {e}")
```

#### `SourceNotFoundError`

Raised when required data source files are not found.

### Error Codes

| Code | Description        | Resolution                                 |
| ---- | ------------------ | ------------------------------------------ |
| 1    | Parse error        | Check file format and path                 |
| 2    | Validation failure | Review validation report                   |
| 3    | IO/config error    | Check file permissions and configuration   |
| 4    | Network error      | Check internet connection and URL validity |

## Type Definitions

### Core Types

#### `SourceType`

```python
class SourceType(str, Enum):
    BUDGET_LAW = "budget_law"
    SPENDING_Q1 = "spending_q1"
    SPENDING_Q12 = "spending_q12"
    SPENDING_Q123 = "spending_q123"
    SPENDING_Q1234 = "spending_q1234"
```

#### `ValidationResult`

```python
@dataclass
class ValidationResult:
    passed: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
```

#### `ProcessingResult`

```python
@dataclass
class ProcessingResult:
    success: bool
    records_processed: int
    output_files: List[str] = field(default_factory=list)
    validation_result: Optional[ValidationResult] = None
    processing_time: Optional[float] = None
```

### Enum Types

#### `ValidationLevel`

```python
class ValidationLevel(str, Enum):
    STRICT = "strict"
    LENIENT = "lenient"
    MINIMAL = "minimal"
```

#### `OutputFormat`

```python
class OutputFormat(str, Enum):
    CSV = "csv"
    PARQUET = "parquet"
    JSON = "json"
```
