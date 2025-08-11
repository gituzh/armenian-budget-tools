# Armenian Budget Analysis Tool - Revised Architecture & Roadmap

## 1. Enhanced Repository Structure

```tree
budget-am/
├── src/
│   ├── armenian_budget/
│   │   ├── core/                   # Core data models and schemas
│   │   │   ├── models.py           # Pydantic models for budget data
│   │   │   ├── schemas.py          # JSON schemas for validation
│   │   │   └── enums.py            # Source types, validation levels
│   │   ├── sources/                # Data source management & download
│   │   │   ├── registry.py         # Official source URLs and metadata
│   │   │   ├── downloader.py       # Download and extract files
│   │   │   ├── organizer.py        # Structure files in data/ folders
│   │   │   └── sources.yaml        # Source definitions with URLs
│   │   ├── ingestion/              # Data extraction and parsing
│   │   │   ├── parsers/            # Format-specific parsers
│   │   │   │   ├── base.py         # Abstract parser interface
│   │   │   │   ├── excel_2019_2024.py  # Your existing logic
│   │   │   │   ├── excel_2025.py   # Your existing logic
│   │   │   │   └── pdf_parser.py   # For historical PDF formats
│   │   │   ├── discovery.py        # Auto-discover files in data/
│   │   │   └── pipeline.py         # Orchestration logic
│   │   ├── validation/             # Reusable business rule validation
│   │   │   ├── financial.py        # Financial consistency (from your tests)
│   │   │   ├── structural.py       # Data structure validation
│   │   │   ├── cross_temporal.py   # Cross-year consistency checks
│   │   │   └── rules.yaml          # Configurable validation rules
│   │   ├── transform/              # Future (post v1): cross-year normalization utilities
│   │   │   ├── normalizer.py       # Optional Common Core view (future)
│   │   │   ├── harmonizer.py       # Standardize field names/values (future)
│   │   │   └── schema_mapper.py    # Year-to-year mappings (future)
│   │   ├── storage/                # Persistence layer
│   │   │   ├── backends/
│   │   │   │   ├── csv.py          # Your current CSV output
│   │   │   │   └── parquet.py      # Efficient columnar storage
│   │   │   ├── repository.py       # Data access layer
│   │   │   └── metadata.py         # Track file versions, checksums
│   │   ├── analysis/               # Analytical tools (future)
│   │   │   ├── trends.py           # Spending trend analysis
│   │   │   ├── anomalies.py        # Outlier detection
│   │   │   └── comparisons.py      # Cross-ministry/year comparisons
│   │   ├── interfaces/             # User-facing interfaces
│   │   │   ├── cli/                # Command-line interface
│   │   │   │   ├── commands/       # CLI command modules
│   │   │   │   └── main.py         # CLI entry point
│   │   │   ├── api/                # Python API (core functions)
│   │   │   └── mcp/                # MCP server implementation
│   │   └── utils/                  # Shared utilities
│   │       ├── logging.py
│   │       ├── config.py
│   │       └── helpers.py
├── config/                        # Configuration files
│   ├── sources.yaml               # Official source URLs and metadata
│   ├── parsers.yaml               # Parser configurations by year
│   └── validation_rules.yaml      # Business validation rules
├── data/                          # Organized data directory
│   ├── original/                  # Downloaded files (replaces raw_data)
│   │   ├── budget_laws/           # Original downloaded archives
│   │   └── spending_reports/      # Original downloaded files
│   ├── extracted/                 # Unarchived source files  
│   │   ├── budget_laws/           # .xlsx, .pdf files ready for parsing
│   │   └── spending_reports/      # Organized by year/quarter
│   ├── processed/                 # Normalized data (replaces output)
│   │   ├── csv/                   # Your current CSV format
│   │   ├── parquet/               # Efficient format for large datasets
│   │   └── metadata.json          # Processing history, checksums
│   └── analysis/                  # Analysis outputs (future)
│       └── reports/
├── tests/                         # Your existing test structure enhanced
│   ├── unit/                      # Test individual functions
│   ├── integration/               # Test full pipeline components  
│   ├── validation/                # Import + test validation functions
│   └── data/                      # Test fixtures and sample data
├── docs/                          # Documentation for agents and users
│   ├── architecture.md            # This document
│   ├── api_reference.md           # Python API documentation  
│   ├── mcp_tools.md               # MCP tool descriptions
│   ├── data_schemas.md            # Data format documentation
│   └── examples/                  # Usage examples
└── scripts/                       # Utility scripts
    ├── migrate_current_data.py    # Move your existing files to new structure
    └── bootstrap.py               # Initial setup and data download
```

Note on naming conventions:

- GitHub repository name: `budget-am`
- Python package name (for pip): `armenian-budget-tools` (proposed)
- Import namespace: `armenian_budget`

## 2. Data Source Management (future)

```python
# src/armenian_budget/sources/registry.py
from typing import Dict, List, Optional
from pydantic import BaseModel, HttpUrl
from pathlib import Path

class SourceDefinition(BaseModel):
    """Definition of an official budget data source"""
    name: str
    year: int
    source_type: str  # "budget_law", "spending_q1", etc.
    url: HttpUrl
    file_format: str  # "xlsx", "zip", "rar", "pdf"
    checksum: Optional[str] = None
    description: str
    
class SourceRegistry:
    """Manages official data source URLs and metadata"""
    
    def __init__(self, sources_file: Path):
        self.sources = self._load_sources(sources_file)
    
    async def download_all(self, force: bool = False) -> Dict[str, bool]:
        """Download all registered sources"""
        results = {}
        for source in self.sources:
            results[source.name] = await self._download_source(source, force)
        return results
    
    async def download_year(self, year: int, force: bool = False) -> Dict[str, bool]:
        """Download all sources for a specific year"""
        year_sources = [s for s in self.sources if s.year == year]
        results = {}
        for source in year_sources:
            results[source.name] = await self._download_source(source, force)
        return results
```

```yaml
# config/sources.yaml - Official source URLs (examples you provided)
sources:
  - name: "2025_budget_law"
    year: 2025
    source_type: "budget_law"
    url: "https://www.gov.am/files/docs/4850.zip"  # You'll provide actual URL
    file_format: "zip"
    description: "2025 State Budget Law attachments"
    
  - name: "2024_spending_q12"
    year: 2024
    source_type: "spending_q12"
    url: "https://minfin.am/website/images/files/72393188f3b5505559d18a66a6a6b89ffdfc829a433af986e6cf72b369d86751.rar"
    file_format: "rar"
    description: "2024 Q1-Q2 Spending Report"
    
  - name: "2023_budget_law"
    year: 2023
    source_type: "budget_law"
    url: "https://minfin.am/website/images/website/copy_1_1.1.ORENQI%20HAVELVACNER.rar"
    file_format: "rar"
    description: "2023 State Budget Law attachments"
    
  - name: "2019_spending_q1"
    year: 2019
    source_type: "spending_q1"
    url: "https://www.minfin.am/files/reports/2019-q1.rar"  # Example URL
    file_format: "rar"
    description: "2019 Q1 Spending Report"
```

## 3. Test vs Validation Separation Principles

### `src/validation/` - Reusable Business Logic

```python
# src/armenian_budget/validation/financial.py
def validate_hierarchical_totals(data: pd.DataFrame, tolerance: float = 0.01) -> ValidationResult:
    """Validate that state body totals = sum of program totals"""
    # Pure business logic, no test framework dependencies
    errors = []
    for state_body in data["state_body"].unique():
        # ... validation logic
    return ValidationResult(passed=len(errors)==0, errors=errors)

def validate_no_negative_amounts(data: pd.DataFrame) -> ValidationResult:
    """Business rule: budget amounts should not be negative"""
    # Reusable across different contexts
```

### `tests/validation/` - Test Validation Functions

```python
# tests/validation/test_financial_validation.py
import pytest
from armenian_budget.validation.financial import validate_hierarchical_totals

def test_hierarchical_totals_with_valid_data(sample_budget_data):
    """Test that validation passes with correct data"""
    result = validate_hierarchical_totals(sample_budget_data.df)
    assert result.passed
    assert len(result.errors) == 0

def test_hierarchical_totals_detects_mismatches():
    """Test that validation catches actual problems"""
    # Create deliberately broken test data
    broken_data = create_broken_test_data()
    result = validate_hierarchical_totals(broken_data)
    assert not result.passed
    assert "mismatch" in result.errors[0].lower()
```

**Validation Types:**

- **Parse-time validation**: Schema, required fields, data types → in `ingestion/`
- **Business rule validation**: Financial consistency, logical relationships → in `validation/`
- **Cross-file validation**: Temporal consistency, cross-references → in `validation/cross_temporal.py`
- **Test-specific validation**: Test data setup, fixtures → stay in `tests/`

## 4. Column Registry (v0.1) and future normalization

```python
# src/armenian_budget/utils/column_registry.py
from typing import Dict
from armenian_budget.core.enums import SourceType

def get_measure_columns(source_type: SourceType) -> Dict[str, str]:
    """Return measure roles for a dataset without rewriting schemas.

    Roles: allocated, revised, actual, execution_rate (if present as a column).
    """
    if source_type == SourceType.BUDGET_LAW:
        return {"allocated": "subprogram_total"}
    if source_type in {SourceType.SPENDING_Q1, SourceType.SPENDING_Q12, SourceType.SPENDING_Q123}:
        return {
            "allocated": "subprogram_annual_plan",
            "revised": "subprogram_rev_annual_plan",
            "actual": "subprogram_actual",
            "execution_rate": "subprogram_actual_vs_rev_annual_plan",
        }
    if source_type == SourceType.SPENDING_Q1234:
        return {
            "allocated": "subprogram_annual_plan",
            "revised": "subprogram_rev_annual_plan",
            "actual": "subprogram_actual",
        }
    return {}
```

Notes:

- v0.1 provides this registry only; it avoids forcing datasets into a single schema.
- Cross-year comparability remains limited (totals, ministries with caveats).
- Future (post v1): a non-destructive Common Core normalization may be added if useful in practice.

## 5. MCP Server Strategy - Progressive Enhancement

### Phase 1: Basic Data Access Tools

```python
# src/armenian_budget/interfaces/mcp/server.py
@tool("list_available_data")
async def list_available_data() -> Dict:
    """Return what processed data files are currently available"""
    return {
        "budget_laws": ["2019", "2020", "2021", "2022", "2023", "2024", "2025"],
        "spending_reports": {"2019": ["Q1", "Q12", "Q123", "Q1234"]},
        "formats": ["csv", "parquet"],
        "last_updated": "2024-01-15"
    }

@tool("get_data_schema")  
async def get_data_schema(year: int, source_type: str) -> Dict:
    """Return column names and data types for a specific dataset"""
    # Load the actual file and return schema info
    return {
        "columns": ["state_body", "program_code", "program_name", "subprogram_total"],
        "dtypes": {"state_body": "string", "program_code": "int64", "subprogram_total": "float64"},
        "shape": [1250, 13],
        "file_path": f"data/processed/csv/{year}_{source_type}.csv"
    }
    
@tool("get_unique_values")
async def get_unique_values(year: int, source_type: str, column: str) -> List:
    """Return unique values in a specific column"""
    # e.g., get_unique_values(2023, "budget_law", "state_body") 
    # Returns: ["Ministry of Education", "Ministry of Health", ...]
    
@tool("filter_budget_data")
async def filter_budget_data(
    year: int, 
    source_type: str, 
    state_body: Optional[str] = None,
    program_codes: Optional[List[int]] = None,
    min_amount: Optional[float] = None
) -> str:
    """Filter budget data and return path to filtered CSV for AI processing"""
    # Example: filter_budget_data(2023, "budget_law", state_body="Ministry of Education")
    # AI can then read and analyze the filtered CSV file
    
    filters = {}
    if state_body: filters["state_body"] = state_body
    if program_codes: filters["program_code"] = program_codes
    if min_amount: filters["subprogram_total >= "] = min_amount
    
    # Apply filters, save to temp file, return path
    filtered_data = apply_filters(year, source_type, filters)
    temp_path = f"/tmp/filtered_{year}_{source_type}_{uuid4()}.csv"
    filtered_data.to_csv(temp_path, index=False)
    
    return temp_path

@tool("get_ministry_spending_summary")
async def get_ministry_spending_summary(year: int, ministry: str) -> Dict:
    """Get spending summary for a specific ministry/state body"""
    # Example: get_ministry_spending_summary(2023, "Ministry of Education")
    return {
        "ministry": ministry,
        "year": year,
        "total_allocated": 45600000.0,
        "total_actual": 42100000.0,  # if spending data available
        "execution_rate": 0.923,
        "program_count": 8,
        "subprogram_count": 34,
        "top_programs": [
            {"code": 1201, "name": "General Education", "amount": 28500000.0},
            {"code": 1202, "name": "Higher Education", "amount": 12400000.0}
        ]
    }
```

### Phase 2: Advanced Analytics Tools

```python
@tool("analyze_spending_trends")
async def analyze_spending_trends(ministry: str, years: List[int]) -> Dict:
    """Analyze spending trends over time"""
    
@tool("detect_anomalies") 
async def detect_anomalies(year: int, threshold: float = 2.0) -> List[Dict]:
    """Find statistical outliers in budget allocations"""
```

## 6. (moved) Migration Roadmap

Roadmap and step-by-step migration have been consolidated in `docs/roadmap.md` and aligned with milestones. This section was moved to keep the architecture focused on structure and responsibilities.

## 7. Core Data Models (v1 types)

```python
# src/armenian_budget/core/models.py
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from enum import Enum

class SourceType(str, Enum):
    BUDGET_LAW = "budget_law"
    SPENDING_Q1 = "spending_q1"
    SPENDING_Q12 = "spending_q12" 
    SPENDING_Q123 = "spending_q123"
    SPENDING_Q1234 = "spending_q1234"

class BudgetItem(BaseModel):
    """Standardized budget item across all years and sources"""
    
    # Identifiers
    year: int
    source_type: SourceType
    source_file: str
    
    # Hierarchy
    state_body: str
    state_body_code: Optional[str] = None
    program_code: int
    program_name: str
    subprogram_code: int
    subprogram_name: str

    # Financial data (v1 uses float; compare with explicit tolerances)
    allocated_amount: Optional[float] = None
    revised_amount: Optional[float] = None
    actual_amount: Optional[float] = None
    period_amount: Optional[float] = None

    # Metadata
    program_goal: Optional[str] = None
    program_result_description: Optional[str] = None
    subprogram_description: Optional[str] = None
    subprogram_type: Optional[str] = None
    
    # Computed fields
    execution_rate: Optional[float] = None
    variance_from_budget: Optional[float] = None

    @validator('allocated_amount', 'revised_amount', 'actual_amount')
    def amounts_must_be_positive_or_zero(cls, v):
        if v is not None and v < 0:
            raise ValueError('Amount cannot be negative')
        return v

class ValidationResult(BaseModel):
    """Result of validation checks"""
    passed: bool
    errors: List[str] = []
    warnings: List[str] = []
    metadata: Dict[str, Any] = {}

class ProcessingResult(BaseModel):
    """Result of processing pipeline"""
    success: bool
    records_processed: int
    output_files: List[str] = []
    validation_result: Optional[ValidationResult] = None
    processing_time: Optional[float] = None

# Future consideration: represent amounts as integer dram subunits (luma) to
# eliminate rounding issues if needed.
```

## 8. Enhanced Pipeline Architecture

```python
# src/armenian_budget/ingestion/pipeline.py
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
import asyncio
from dataclasses import dataclass

@dataclass
class FileProcessingInfo:
    """Information about a file to be processed"""
    path: Path
    year: int
    source_type: SourceType
    last_modified: Optional[float] = None
    checksum: Optional[str] = None

class BudgetDataPipeline:
    """Main orchestration pipeline - wraps your existing parser logic"""
    
    def __init__(self, config_path: Path):
        self.config = self._load_config(config_path)
        self.logger = logging.getLogger(__name__)
        
    async def process_all(self, 
                         force_reprocess: bool = False,
                         validation_level: str = "strict") -> Dict[str, Any]:
        """Process all discovered budget files"""
        
        # 1. Discovery - find files in data/extracted/
        discovered_files = self._discover_files()
        self.logger.info(f"Discovered {len(discovered_files)} files")
        
        # 2. Filter for processing (skip if already processed and not forced)
        files_to_process = self._filter_for_processing(
            discovered_files, force_reprocess
        )
        self.logger.info(f"Will process {len(files_to_process)} files")
        
        # 3. Process each file using your existing parsers
        results = []
        for file_info in files_to_process:
            try:
                # Use your existing flatten_budget_excel_* functions
                parsed_data = await self._parse_file_with_existing_logic(file_info)
                
                # Validate using extracted validation functions on parsed data
                validation_result = await self._validate_data(
                    parsed_data, validation_level
                )
                
                if validation_result.passed:
                    # Store in both CSV and Parquet formats
                    output_files = await self._store_data(parsed_data, file_info)
                    results.append(ProcessingResult(
                        success=True,
                        records_processed=len(parsed_data),
                        output_files=output_files,
                        validation_result=validation_result
                    ))
                else:
                    self.logger.error(f"Validation failed for {file_info.path}")
                    results.append(ProcessingResult(
                        success=False,
                        records_processed=0,
                        validation_result=validation_result
                    ))
                    
            except Exception as e:
                self.logger.error(f"Failed to process {file_info.path}: {e}")
                results.append(ProcessingResult(
                    success=False,
                    records_processed=0,
                    validation_result=ValidationResult(
                        passed=False, 
                        errors=[f"Processing error: {str(e)}"]
                    )
                ))
        
        return {
            'total_files': len(files_to_process),
            'successful': len([r for r in results if r.success]),
            'failed': len([r for r in results if not r.success]),
            'results': results
        }
    
    async def _parse_file_with_existing_logic(self, file_info: FileProcessingInfo) -> pd.DataFrame:
        """Use your existing parser logic"""
        if file_info.year == 2025:
            # Use your existing flatten_budget_excel_2025
            df, overall, _, _ = flatten_budget_excel_2025(str(file_info.path))
        else:
            # Use your existing flatten_budget_excel_2019_2024  
            df, overall, _, _ = flatten_budget_excel_2019_2024(
                str(file_info.path), 
                source_type=file_info.source_type
            )
        
        # Add metadata columns
        df['year'] = file_info.year
        df['source_type'] = file_info.source_type.value
        df['source_file'] = file_info.path.name
        
        return df
```

## 9. (future) Normalization rationale — if we add later

Looking at your current implementation, different years and source types have different column structures:

**Current Reality:**

```python
# 2019-2024 Budget Law format:
["state_body_total", "program_total", "subprogram_total"]

# 2019-2024 Spending Q1/Q12/Q123 format:  
["state_body_annual_plan", "state_body_rev_annual_plan", "state_body_actual", ...]

# 2025 Budget Law format:
["state_body_total", "program_total", "subprogram_total", "program_code_ext"]

# Different meaning: 2019 "total" = budget allocation, 2019 Q1 "actual" = spent amount
```

This section explains why we might add a non-destructive normalization later. For v1 we rely on the column registry and keep source schemas intact.

## 10. Flexible CLI Interface

```bash
# Install the tool
pip install armenian-budget-tools

# Data source management
armenian-budget download --year 2023 --source-type budget_law
armenian-budget download --all --update
armenian-budget extract --year 2024  # Unarchive downloaded files

# Processing pipeline
armenian-budget process --all --validation-level strict
armenian-budget process --year 2023 --force-reprocess
armenian-budget process --years 2019-2023 --output-format parquet

# Data validation
armenian-budget validate --all --level strict 
armenian-budget validate --year 2023 --output validation_report.json

# Data export and analysis
armenian-budget export --format parquet --years 2020-2025
armenian-budget export --format csv --filter "state_body=Ministry of Education"

# MCP Server
armenian-budget mcp-server --port 8000 --data-path ./data/processed

# Utilities
armenian-budget status  # Show what data is available, last processed, etc.
armenian-budget clean --cache  # Clean temporary files
armenian-budget migrate-from-old-structure  # One-time migration script
```

## 11. Agent-Friendly Implementation Notes

**For IDE agents working on this codebase:**

1. **Current State**: Existing parser logic is in `src/budget-am/budget/__init__.py` with comprehensive state machine implementation for Excel parsing

2. **Test Architecture**: Robust parametrized tests in `tests/` with fixtures for all data types. Validation logic should be extracted to `src/validation/` but tests should import and use these functions.

3. **Data Flow**: `original/ → extracted/ → processed/` with metadata tracking at each stage

4. **Parsing Strategy**: Keep existing state machine logic but modularize into format-specific parsers. 2025 format differs from 2019-2024.

5. **MCP Priority**: Start with basic data access tools before building analytics. Focus on letting AI access and filter existing processed data.

6. **Configuration**: Use YAML files for sources, validation rules, and parser configs to avoid hardcoding.

**Key Design Principles:**

- Preserve existing working parser logic
- Extract reusable validation functions from tests
- Enable gradual migration without breaking current functionality
- Keep data lineage (original → extracted → processed)
- Configuration-driven approach for flexibility
- Progressive MCP tool enhancement

Would you like me to detail the implementation of any specific component, or shall we start with the migration script to move your current files into the new structure?
