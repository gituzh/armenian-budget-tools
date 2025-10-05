# Armenian Budget Analysis Tool - Architecture Overview

## 1. Overview & Design Principles

### 1.1 Architecture Vision & Core Philosophy

The Armenian Budget Tools architecture is designed to provide robust, deterministic processing of official Armenian state budget data while maintaining flexibility for future enhancements. The system emphasizes:

- **Data Integrity**: Clear lineage tracking from original government sources to processed outputs
- **Progressive Enhancement**: Modular design allowing phased feature development
- **Configuration-Driven**: Externalized settings to adapt to changing data formats
- **Multi-Interface Support**: CLI, Python API, and MCP server for different user needs

### 1.2 Design Principles & Constraints

**Core Architectural Principles:**

- **Incremental Evolution**: Preserve working code while enabling gradual enhancement
- **Separation of Concerns**: Clear boundaries between data processing, validation, and interfaces
- **Configuration-Driven**: Externalized settings for adaptability to changing requirements
- **Data Integrity**: Comprehensive lineage tracking from source to output
- **Error Resilience**: Graceful error handling with clear recovery paths
- **Performance-First**: Vectorized operations and efficient resource usage

**Security Principles:**

- **Data Provenance**: Cryptographic checksums for integrity verification
- **Access Control**: No arbitrary code execution in data processing
- **Input Validation**: Comprehensive validation at all entry points
- **Audit Trail**: Complete logging of all processing operations

**Technical Constraints:**

- **Platform**: Python 3.10+ with macOS/Linux primary support
- **Data Formats**: Excel-based parsing (2019–2025), structured for future PDF support
- **Performance**: Vectorized pandas operations with memory-conscious processing
- **Reliability**: Typed exceptions, deterministic outputs, tolerance-aware comparisons
- **Compatibility**: No `sys.exit` in library code, clear error hierarchies

### 1.3 Data Flow Architecture

The system implements a clear three-stage data pipeline with comprehensive lineage tracking:

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Original      │    │   Extracted     │    │   Processed     │
│   Archives      │───▶│   Files         │───▶│   CSVs +        │
│   (.rar/.zip)   │    │   (.xlsx/.xls)  │    │   Metadata      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
   ┌─────────────┐    ┌─────────────────┐    ┌─────────────┐
   │ Provenance  │    │ File Discovery  │    │ Validation  │
   │ Tracking    │    │ & Pattern       │    │ & Quality   │
   │             │    │ Matching        │    │ Checks      │
   └─────────────┘    └─────────────────┘    └─────────────┘
```

**Stage Responsibilities:**

- **Original**: Government archives with checksums and download metadata
- **Extracted**: Unarchived source files with discovery indexing
- **Processed**: Normalized outputs with validation results and lineage

**Architectural Patterns:**

- **Pipeline Pattern**: Sequential processing with error recovery
- **Observer Pattern**: Event-driven status reporting and logging
- **Factory Pattern**: Parser selection based on file format and year
- **Repository Pattern**: Abstracted data access across storage backends

### 1.4 Relationship to Product Requirements

This architecture document focuses on system design and technical implementation. For detailed information on various aspects of the system:

**📋 Product & Requirements:**

- Product scope, user stories, and acceptance criteria: [`docs/prd.md`](../prd.md)
- Implementation milestones and development roadmap: [`docs/roadmap.md`](../roadmap.md)

**🔧 Usage & Examples:**

- CLI commands and usage examples: [`README.md`](../README.md)
- Python API usage and code examples: [`README.md`](../README.md)

**📊 Data & Schemas:**

- Detailed data schemas and column references: [`docs/data_schemas.md`](../data_schemas.md)
- Data pipeline and format specifications: [`docs/data_schemas.md`](../data_schemas.md)

**🤖 AI Integration:**

- MCP server tools and API: [`docs/mcp.md`](../mcp.md)
- AI-assisted analysis capabilities: [`docs/mcp.md`](../mcp.md)

## 2. System Architecture

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

### 2.1 Repository Structure & Component Organization

The repository follows a modular structure designed for maintainability and progressive development:

**Core Modules:**

- **`core/`**: Fundamental data models, schemas, and type definitions
- **`ingestion/`**: Data discovery, parsing, and pipeline orchestration
- **`validation/`**: Business rule validation and data quality checks
- **`sources/`**: Data source management and download capabilities
- **`interfaces/`**: User-facing interfaces (CLI, API, MCP)
- **`storage/`**: Persistence layer with multiple backend support

**Supporting Infrastructure:**

- **`config/`**: Externalized configuration files
- **`data/`**: Organized data directory with clear stage separation
- **`tests/`**: Comprehensive test suite with validation integration
- **`docs/`**: Documentation for different audiences and purposes

### 2.2 Component Dependencies & Interfaces

**Key Dependencies:**

- Core modules have minimal dependencies to maintain flexibility
- Interfaces depend on core modules but not vice versa
- Validation functions are extracted from tests for reuse across contexts
- Configuration drives behavior without hardcoding

**Interface Boundaries:**

- **Ingestion**: Pure data processing, no user interaction
- **Validation**: Reusable business logic, no framework dependencies
- **Storage**: Abstract persistence layer supporting multiple backends
- **Interfaces**: User interaction, delegating to core modules

### 2.3 Data Pipeline Overview

The system implements a clean separation of concerns across the data pipeline:

```text
Discovery → Parsing → Validation → Storage → Metadata
```

**Pipeline Stages:**

1. **Discovery**: File detection and metadata extraction
2. **Parsing**: Format-specific data extraction using existing logic
3. **Validation**: Business rule application and quality checks
4. **Storage**: Output generation in requested formats
5. **Metadata**: Lineage tracking and provenance recording

### 2.4 Module Responsibilities & Boundaries

**Naming Conventions:**

- GitHub repository: `budget-am`
- Python package: `armenian-budget-tools` (proposed)
- Import namespace: `armenian_budget`

**Module Boundaries:**

- Each module has a single responsibility
- Clear API contracts between modules
- Configuration externalized to YAML files
- Error handling through typed exceptions

## 3. Core Data Architecture

### 3.1 Data Model Design & Pydantic Schemas

The system uses Pydantic models to ensure type safety and validation throughout the data pipeline:

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

### 3.2 Source Type System & Enums

The `SourceType` enum defines the different categories of budget data supported:

- **BUDGET_LAW**: Annual budget allocations (currently parses program summary)
- **SPENDING_Q1/Q12/Q123/Q1234**: Quarterly spending reports with different period scopes
- **MTEP**: Mid‑term expenditure program (three‑year plan, two‑level hierarchy: state body → program). Initial support targets 2024 format.

Each source type has distinct column structures and validation rules. For detailed schemas, see [`docs/data_schemas.md`](../data_schemas.md).

### 3.3 Column Registry & Role Mapping Strategy

The column registry provides a flexible mapping between conceptual roles and actual column names:

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

**Design Principles:**

- v0.1 provides this registry only; it avoids forcing datasets into a single schema
- Cross-year comparability remains limited (totals, ministries with caveats)
- Future (post v1): a non-destructive Common Core normalization may be added if useful in practice

### 3.4 Storage Layer Design (CSV vs Parquet considerations)

The system supports multiple storage backends with different trade-offs:

**CSV Backend:**

- Human-readable format compatible with Excel and BI tools
- UTF-8 encoding supports Armenian text
- Easy debugging and manual inspection
- Larger file sizes and slower queries for large datasets

**Parquet Backend:**

- Columnar storage optimized for analytical queries
- Efficient compression and fast filtering
- Better performance for large datasets
- Less human-readable for debugging

**Metadata Tracking:**

- Processing history and checksums recorded in `metadata.json`
- File lineage tracking from original sources
- Version information for reproducibility

### 3.5 Data Lineage & Metadata Tracking

Every processed dataset maintains complete provenance information:

- **Source tracking**: Original government URLs and archive checksums
- **Processing metadata**: Timestamps, versions, and configuration used
- **Validation results**: Quality checks and any issues encountered
- **File relationships**: Links between original, extracted, and processed files

## 4. Processing Pipeline Architecture

### 4.1 Ingestion & Discovery System

The ingestion system provides automated file discovery and metadata extraction:

**Discovery Strategy:**

- Pattern-based matching on file names and content via `config/parsers.yaml`
- Configuration-driven file selection to adapt to changing formats
- Fallback to manual file specification when auto-discovery fails
- Results cached in `data/extracted/discovery_index.json` with file metadata
- Metadata tracking includes file size, modification time, checksum, and matching pattern

**File Processing Info:**

```python
@dataclass
class FileProcessingInfo:
    """Information about a file to be processed"""
    path: Path
    year: int
    source_type: SourceType
    last_modified: Optional[float] = None
    checksum: Optional[str] = None
```

### 4.2 Parser Architecture & Format Handling

The system supports multiple Excel formats through a modular parser architecture:

**Parser Modules:**

- **`excel_2019_2024.py`**: Handles 2019–2024 budget laws and spending reports
- **`excel_2025.py`**: Specialized parser for 2025 format changes
- **`pdf_parser.py`**: Future support for historical PDF formats (pre-2019)

**Key Design Decisions:**

- Preserve existing working parser logic during migration
- Separate parsers for different year ranges due to format variations
- Maintain state machine logic for complex Excel parsing
- Extract common functionality into base classes for reusability

### 4.3 Validation Framework Design

The validation system separates business logic from testing infrastructure:

**Validation Architecture:**

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

**Validation Architecture:**

The system implements a multi-layered validation strategy with clear separation between business logic and testing:

- **Framework Integration**: Validation functions are designed to work seamlessly with testing frameworks
- **Result Pattern**: Consistent `ValidationResult` objects with error tracking and metadata
- **Testability**: Validation logic is extracted from tests to enable independent testing

**Validation Types:**

- **Parse-time validation**: Schema, required fields, data types → in `ingestion/`
- **Business rule validation**: Financial consistency, logical relationships → in `validation/`
- **Cross-file validation**: Temporal consistency, cross-references → in `validation/cross_temporal.py`
- **Test-specific validation**: Test data setup, fixtures → stay in `tests/`

### 4.4 Orchestration & Error Handling

**Pipeline Architecture Pattern:**
The system implements a robust orchestration layer that coordinates data processing across multiple stages with comprehensive error handling and recovery mechanisms.

**Key Architectural Components:**

- **Centralized Pipeline Controller**: Orchestrates the entire processing workflow
- **Error Recovery Patterns**: Graceful degradation and retry mechanisms
- **Progress Tracking**: Detailed logging and status reporting
- **Resource Management**: Efficient memory usage and parallel processing

**Error Handling Strategy:**

- **Typed Exceptions**: Clear error hierarchy with specific exception types
- **Recovery Mechanisms**: Automatic retry with fallback strategies
- **Logging Integration**: Structured logging for debugging and monitoring
- **Status Reporting**: Comprehensive processing results and error summaries

For detailed implementation of the pipeline orchestration, see [`docs/implementation_guide.md`](../implementation_guide.md).

### 4.5 Performance Considerations & Vectorization Strategy

**Performance Architecture:**

- **Vectorized Operations**: Pandas-based processing for computational efficiency
- **Memory Management**: Chunked processing for large datasets with configurable sizes
- **Parallel Processing**: Concurrent file processing where dependencies allow
- **Caching Strategy**: Intermediate result caching to avoid redundant computations

**Scalability Patterns:**

- **Horizontal Scaling**: Independent file processing enables distributed execution
- **Resource Pooling**: Connection pooling for external service access
- **Batch Processing**: Efficient handling of multiple files with shared resources
- **Progressive Loading**: On-demand data loading to minimize memory footprint

**Data Processing Strategy:**

- **Precision Handling**: Float64 operations with tolerance-aware comparisons
- **Format Optimization**: Automatic selection between CSV and Parquet based on use case
- **I/O Optimization**: Buffered reading/writing with appropriate chunk sizes
- **Memory Efficiency**: Garbage collection hints and object reuse patterns

## 5. External Interfaces Design

### 5.1 CLI Architecture & Command Structure

The CLI provides a user-friendly interface to core processing functionality:

```bash
**CLI Design Principles:**

- Commands mirror core module functionality for consistency
- Consistent parameter patterns across all commands
- Clear error messages and standardized exit codes
- Support for both interactive and automated usage patterns
- Configuration-driven behavior with sensible defaults

For detailed CLI usage examples and command reference, see [`README.md`](../README.md).

### 5.2 Python API Design Principles

The Python API provides programmatic access to all core functionality:

```python
from armenian_budget.ingestion.parsers import (
    flatten_budget_excel_2019_2024,
    flatten_budget_excel_2025,
    SourceType,
)

# Budget law (2019–2024 format)
df, overall, *_ = flatten_budget_excel_2019_2024(
    "./data/extracted/budget_laws/2023/file.xlsx", SourceType.BUDGET_LAW
)
# overall contains total budget amount (float)
```

**API Design Goals:**

- Mirror CLI functionality for consistency
- Support both simple and advanced use cases
- Clear function signatures with type hints
- Comprehensive error handling and validation

### 5.3 MCP Server Integration Strategy

The MCP server provides AI-friendly access to processed budget data:

**Core Tools:**

**MCP Tool Architecture:**

- **Data Discovery Tools**: Dataset inventory and metadata access
- **Schema Inspection Tools**: Data structure and type information
- **Filtering & Query Tools**: Flexible data extraction and analysis
- **Summary & Aggregation Tools**: High-level insights and statistics

**Progressive Enhancement:**

- **Phase 1**: Basic data access and filtering tools
- **Phase 2**: Advanced analytics and trend analysis
- **Future**: Specialized tools for cross-year comparisons and anomaly detection

For detailed MCP server documentation including all tools and usage examples, see [`docs/mcp.md`](../mcp.md).

## 6. Development & Quality Assurance

### 6.1 Testing Architecture & Validation Extraction

The system maintains a clear separation between business logic validation and test infrastructure:

**Validation Framework Design:**

- Reusable functions return typed `ValidationResult` objects
- Business logic extracted from test files for broader use
- Configurable validation levels (strict vs lenient)
- Comprehensive error reporting with context

**Test Organization:**

```python
# tests/validation/test_financial_validation.py
import pytest
from armenian_budget.validation.financial import validate_hierarchical_totals

def test_hierarchical_totals_with_valid_data(sample_budget_data):
    """Test that validation passes with correct data"""
    result = validate_hierarchical_totals(sample_budget_data.df)
    assert result.passed
    assert len(result.errors) == 0
```

### 6.2 Error Handling & Exception Design

**Typed Exception Hierarchy:**

- `ParseError`: Issues with file parsing or format recognition
- `LabelMismatchError`: Armenian text detection failures
- `ValidationError`: Business rule violations
- `SourceNotFoundError`: Missing data source files

**Error Handling Strategy:**

- Library functions raise typed exceptions (no `sys.exit`)
- CLI maps exceptions to appropriate exit codes
- Clear error messages with actionable guidance
- Graceful degradation where possible

### 6.3 Logging & Observability Strategy

**Logging Levels:**

- **Development**: Human-readable logs with context
- **Production**: Structured JSON logs for monitoring
- **Debug**: Detailed tracing for troubleshooting

**Observability Features:**

- Processing time tracking
- File processing statistics
- Validation result summaries
- Data lineage metadata

### 6.4 Performance & Reliability Patterns

**Performance Optimizations:**

- Vectorized pandas operations for data processing
- Memory-conscious file processing
- Efficient filtering and aggregation
- Parallel processing where beneficial

**Reliability Patterns:**

- Deterministic processing with explicit tolerances
- Comprehensive input validation
- Graceful error recovery
- Data integrity verification through checksums

**Current Implementation Notes:**

- Existing parser logic in `src/budget-am/budget/__init__.py` with state machine implementation
- Robust parametrized tests with fixtures for all data types
- Data flow: `original/ → extracted/ → processed/` with metadata tracking
- Preserve existing working parser logic during migration
- Extract validation functions from tests for reuse
- Configuration-driven approach using YAML files

## 7. Deployment & Configuration

### 7.1 Configuration File Structure & Schema

**Core Configuration Files:**

- **`config/sources.yaml`**: Official data source URLs and metadata
- **`config/parsers.yaml`**: Parser configurations and discovery patterns
- **`config/program_patterns.yaml`**: Keyword patterns for MCP tools
- **`config/checksums.yaml`**: SHA-256 hashes for download verification

**Configuration Principles:**

- Externalized settings to avoid hardcoding
- YAML format for human readability
- Validation of configuration files at startup
- Environment-specific overrides where needed

### 7.2 Source Registry & Download Management

**Source Registry & Download Management:**

The system includes a comprehensive data source management layer for handling official government data sources:

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

**Source Configuration:**

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
```

This source management system provides:

- **Centralized registry** of all official data sources with metadata
- **Automated download** capabilities with integrity verification
- **Archive extraction** support for RAR/ZIP files
- **Checksum validation** for data integrity
- **Graceful error handling** for network and parsing issues

### 7.3 Packaging & Distribution Strategy

**Python Package Configuration:**

- Package name: `armenian-budget-tools` (proposed)
- Import namespace: `armenian_budget`
- Console script entry point: `armenian-budget`

**Distribution Channels:**

- PyPI for pip installation
- GitHub releases for source distribution
- Docker containerization for deployment
- Editable installation for development

### 7.4 Environment & Dependency Management

**Runtime Dependencies:**

- Python 3.10+ compatibility
- Core: pandas, pydantic, openpyxl
- Optional: rapidfuzz (MCP text similarity), uvicorn (HTTP server)
- Platform-specific: unar/unrar for archive extraction

**Environment Setup:**

- Virtual environment isolation
- Dependency management via requirements.txt/pyproject.toml
- Development vs production configurations
- CI/CD pipeline integration

## 8. Future Architecture Considerations

### 8.1 Post-v1 Enhancement Roadmap

For detailed implementation milestones and development roadmap, see [`docs/roadmap.md`](../roadmap.md).

**Key Future Enhancements:**

- Advanced analytics and trend analysis
- Cross-year data harmonization
- PDF parsing for historical data (2017-2018)
- Multilingual field support (EN/AM)
- Performance optimizations and scaling improvements

### 8.2 Scalability & Performance Extensions

**Performance Roadmap:**

- Larger dataset handling optimizations
- Parallel processing improvements
- Memory usage optimizations
- Database backend integration

**Scalability Considerations:**

- Cloud deployment options
- Distributed processing capabilities
- API rate limiting and caching
- Horizontal scaling architecture

### 8.3 Advanced Analytics Integration Points

**Analytics Extensions:**

- Trend analysis and forecasting
- Anomaly detection algorithms
- Cross-temporal comparisons
- Automated reporting and visualization

**Machine Learning Integration:**

- Pattern recognition in budget data
- Predictive modeling capabilities
- Automated categorization
- Quality scoring and validation

### 8.4 Migration & Compatibility Strategies

**Migration Planning:**

- Backward compatibility maintenance
- Gradual feature rollout
- Data migration utilities
- User communication and training

**Long-term Evolution:**

- API versioning strategy
- Deprecation policies
- Extension mechanisms
- Community contribution guidelines

---

## 📚 Documentation Organization Guide

This architecture document provides the technical foundation and design decisions. For specific implementation details and usage examples, refer to:

| Document | Purpose | Content Level | Primary Audience | Key Content |
|----------|---------|---------------|------------------|-------------|
| [`README.md`](../README.md) | **User Guide** | Usage Examples | End Users | Installation, CLI commands, API examples, MCP setup |
| [`docs/architecture.md`](../docs/architecture.md) | **System Architecture** | High-Level Design | Architects/Tech Leads | Design patterns, component relationships, scalability |
| [`docs/prd.md`](../docs/prd.md) | **Product Requirements** | Business Requirements | Product Team | Goals, user stories, scope, acceptance criteria |
| [`docs/data_schemas.md`](../docs/data_schemas.md) | **Data Specifications** | Technical Details | Data Analysts | Schema details, column references, data formats |
| [`docs/mcp.md`](../docs/mcp.md) | **AI Integration Guide** | Integration Examples | AI Developers | MCP tools, server config, AI-assisted workflows |
| [`docs/api_reference.md`](../docs/api_reference.md) | **API Reference** | Function Reference | Developers | Function signatures, parameters, return types |
| [`docs/implementation_guide.md`](../docs/implementation_guide.md) | **Implementation Guide** | Code Architecture | Contributors | Implementation patterns, testing strategies, development workflow |
| [`docs/roadmap.md`](../docs/roadmap.md) | **Development Roadmap** | Project Planning | Contributors | Milestones, release planning, development priorities |

### 🧭 Navigation Guide

**🎯 For Different User Types:**

- **👥 End Users/Newcomers**: Start with `README.md` for installation and basic usage
- **🏗️ Architects/Tech Leads**: This `architecture.md` for system design and patterns
- **👨‍💻 Developers**: `api_reference.md` + `implementation_guide.md` for coding details
- **📊 Data Analysts**: `data_schemas.md` for data structure and column specifications
- **🤖 AI Integration Specialists**: `mcp.md` for MCP server and tool development
- **📋 Product Managers**: `prd.md` for requirements and scope understanding
- **🛠️ Contributors**: `roadmap.md` + `implementation_guide.md` for development workflow

**🔗 Content Flow:**

```text
README.md (Getting Started)
    ↓
architecture.md (System Understanding)
    ↓
Specialized Docs (Implementation Details)
```

**⚠️ Important Notes:**

- This `architecture.md` focuses on **design decisions and patterns**, not implementation details
- Implementation specifics are in `implementation_guide.md` and `api_reference.md`
- Usage examples are consolidated in `README.md` to avoid duplication
- Data specifications are centralized in `data_schemas.md` for consistency
