# Implementation Guide

This document provides detailed implementation information for developers working on the Armenian Budget Tools codebase.

## Table of Contents

- [Implementation Guide](#implementation-guide)
  - [Table of Contents](#table-of-contents)
  - [Project Structure](#project-structure)
    - [Source Code Organization](#source-code-organization)
    - [Configuration Files](#configuration-files)
    - [Data Directory Structure](#data-directory-structure)
  - [Core Implementation Patterns](#core-implementation-patterns)
    - [Pipeline Orchestration Implementation](#pipeline-orchestration-implementation)
    - [Testing Strategy Implementation](#testing-strategy-implementation)
      - [Validation Testing Examples](#validation-testing-examples)
      - [Integration Testing Examples](#integration-testing-examples)
    - [Parser Architecture](#parser-architecture)
      - [Abstract Parser Interface](#abstract-parser-interface)
      - [Format-Specific Implementations](#format-specific-implementations)
    - [Validation Framework](#validation-framework)
      - [Validation Function Pattern](#validation-function-pattern)
      - [Validation Integration Pattern](#validation-integration-pattern)
    - [Pipeline Orchestration](#pipeline-orchestration)
  - [Key Components Implementation](#key-components-implementation)
    - [Ingestion System](#ingestion-system)
      - [File Discovery Implementation](#file-discovery-implementation)
    - [Validation System](#validation-system)
      - [Validation Rule Engine](#validation-rule-engine)
    - [Storage System](#storage-system)
      - [Backend Interface](#backend-interface)
      - [CSV Backend Implementation](#csv-backend-implementation)
  - [Error Handling Patterns](#error-handling-patterns)
    - [Exception Hierarchy](#exception-hierarchy)
    - [Error Recovery](#error-recovery)
    - [Logging Strategy](#logging-strategy)
  - [Configuration Management](#configuration-management)
    - [Sources Configuration](#sources-configuration)
    - [Parser Configuration](#parser-configuration)
    - [Validation Rules](#validation-rules)
  - [Testing Strategy](#testing-strategy)
    - [Unit Tests](#unit-tests)
    - [Integration Tests](#integration-tests)
    - [Data Validation Tests](#data-validation-tests)
  - [Performance Considerations](#performance-considerations)
    - [Vectorization Patterns](#vectorization-patterns)
    - [Memory Management](#memory-management)
    - [File I/O Optimization](#file-io-optimization)
  - [Development Workflow](#development-workflow)
    - [Setting Up Development Environment](#setting-up-development-environment)
    - [Running Tests](#running-tests)
    - [Code Quality](#code-quality)
    - [Contributing Guidelines](#contributing-guidelines)

## Project Structure

### Source Code Organization

```bash
src/armenian_budget/
├── core/                          # Core data models and types
│   ├── models.py                  # Pydantic models for data structures
│   ├── schemas.py                 # JSON schemas for validation
│   └── enums.py                   # Enumeration types (SourceType, etc.)
├── ingestion/                     # Data ingestion and parsing
│   ├── parsers/                   # Format-specific parsers
│   │   ├── base.py               # Abstract parser interface
│   │   ├── excel_2019_2024.py    # 2019-2024 Excel parser
│   │   └── excel_2025.py         # 2025 Excel parser
│   ├── discovery.py              # File discovery logic
│   └── pipeline.py               # Pipeline orchestration
├── validation/                    # Business rule validation
│   ├── financial.py              # Financial validation rules
│   ├── structural.py             # Data structure validation
│   └── cross_temporal.py         # Cross-year consistency checks
├── sources/                       # Data source management
│   ├── registry.py               # Source registry management
│   ├── downloader.py             # Download functionality
│   └── organizer.py              # File organization logic
├── storage/                       # Data persistence layer
│   ├── backends/                 # Storage backend implementations
│   │   ├── csv.py               # CSV storage backend
│   │   └── parquet.py           # Parquet storage backend
│   ├── repository.py             # Data access layer
│   └── metadata.py               # Metadata tracking
├── interfaces/                    # User-facing interfaces
│   ├── cli/                      # Command-line interface
│   │   ├── commands/            # CLI command implementations
│   │   └── main.py              # CLI entry point
│   ├── api/                      # Python API functions
│   └── mcp/                      # MCP server implementation
└── utils/                         # Shared utilities
    ├── logging.py                # Logging configuration
    ├── config.py                 # Configuration management
    └── helpers.py                # Helper functions
```

### Configuration Files

```bash
config/
├── sources.yaml                  # Official data source definitions
├── parsers.yaml                  # Parser configuration and patterns
├── program_patterns.yaml         # MCP program pattern matching
├── validation_rules.yaml         # Business validation rules
└── checksums.yaml                # File integrity verification
```

### Data Directory Structure

```bash
data/
├── original/                     # Downloaded government archives
│   ├── budget_laws/             # Budget law archives by year
│   └── spending_reports/         # Spending report archives by year
├── extracted/                    # Unarchived source files
│   ├── budget_laws/             # Excel files ready for parsing
│   │   └── 2023/
│   │       └── budget_law.xlsx
│   └── spending_reports/         # Organized by year/quarter
│       └── 2023/
│           ├── Q1/
│           │   └── spending_q1.xlsx
│           └── Q12/
│               └── spending_q12.xlsx
├── processed/                    # Normalized output data
│   ├── csv/                     # CSV format outputs
│   │   ├── 2023_BUDGET_LAW.csv
│   │   └── 2023_SPENDING_Q12.csv
│   ├── parquet/                 # Parquet format outputs
│   └── metadata.json            # Processing metadata
└── analysis/                     # Analysis outputs (future)
    └── reports/
```

## Core Implementation Patterns

### Pipeline Orchestration Implementation

The main processing pipeline coordinates all components with comprehensive error handling and logging:

```python
# src/armenian_budget/ingestion/pipeline.py
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from ..core.models import SourceType, ProcessingResult, ValidationResult

@dataclass
class FileProcessingInfo:
    """Information about a file to be processed"""
    path: Path
    year: int
    source_type: SourceType
    last_modified: Optional[float] = None
    checksum: Optional[str] = None

class BudgetDataPipeline:
    """Main orchestration pipeline for budget data processing"""

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
        """Use your existing parser logic - bridge to current implementation"""
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

    async def process_file_with_recovery(self, file_info: FileProcessingInfo) -> ProcessingResult:
        """Process file with comprehensive error recovery"""

        try:
            # Primary processing attempt
            return await self._process_file(file_info)

        except LabelMismatchError as e:
            # Try with relaxed label matching
            self.logger.warning(f"Label mismatch for {file_info.path}, trying relaxed matching")
            try:
                return await self._process_file_relaxed(file_info)
            except Exception:
                raise e  # Re-raise original error if recovery fails

        except ValidationError as e:
            # Continue processing but mark as failed validation
            self.logger.error(f"Validation failed for {file_info.path}: {e}")
            return ProcessingResult(
                success=False,
                records_processed=0,
                validation_result=ValidationResult(
                    passed=False,
                    errors=[str(e)],
                    metadata={"error_type": "validation"}
                )
            )

        except Exception as e:
            # Unexpected error - log and fail
            self.logger.error(f"Unexpected error processing {file_info.path}: {e}")
            return ProcessingResult(
                success=False,
                records_processed=0,
                validation_result=ValidationResult(
                    passed=False,
                    errors=[f"Unexpected error: {str(e)}"],
                    metadata={"error_type": "unexpected"}
                )
            )
```

### Testing Strategy Implementation

#### Validation Testing Examples

```python
# tests/validation/test_financial_validation.py
import pytest
from armenian_budget.validation.financial import validate_hierarchical_totals

class TestHierarchicalTotals:
    """Test hierarchical total validation"""

    def test_hierarchical_totals_with_valid_data(self, sample_budget_data):
        """Test that validation passes with correct data"""
        result = validate_hierarchical_totals(sample_budget_data.df)

        assert result.passed
        assert len(result.errors) == 0
        assert result.metadata["tolerance_used"] == 0.01

    def test_hierarchical_totals_detects_mismatches(self, broken_budget_data):
        """Test that invalid hierarchical data fails validation"""
        result = validate_hierarchical_totals(broken_budget_data.df)

        assert not result.passed
        assert len(result.errors) > 0
        assert "mismatch" in " ".join(result.errors).lower()
```

#### Integration Testing Examples

```python
# tests/integration/test_pipeline.py
import pytest
from pathlib import Path
from armenian_budget.ingestion.pipeline import BudgetDataPipeline

class TestBudgetDataPipeline:
    """Test end-to-end pipeline functionality"""

    @pytest.mark.asyncio
    async def test_process_single_file_success(self, sample_excel_file):
        """Test successful processing of a single file"""
        # Setup test data
        test_file = self.temp_dir / 'extracted' / 'budget_laws' / '2023' / 'test.xlsx'
        test_file.parent.mkdir(parents=True)
        shutil.copy(sample_excel_file, test_file)

        # Process file
        result = await self.pipeline.process_file(
            year=2023,
            source_type=SourceType.BUDGET_LAW,
            input_path=str(test_file)
        )

        # Verify results
        assert result.success
        assert result.records_processed > 0
        assert len(result.output_files) > 0
```

### Parser Architecture

The parsing system is designed to handle multiple Excel formats while maintaining extensibility:

#### Abstract Parser Interface

```python
# src/armenian_budget/ingestion/parsers/base.py
from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any
import pandas as pd

class BudgetParser(ABC):
    """Abstract base class for budget data parsers"""

    @abstractmethod
    def parse(self, file_path: str, **kwargs) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Parse budget file and return standardized format

        Args:
            file_path: Path to the Excel file
            **kwargs: Parser-specific arguments

        Returns:
            Tuple of (flattened_dataframe, overall_totals_dict)
        """
        pass

    @abstractmethod
    def get_supported_source_types(self) -> List[SourceType]:
        """Return list of supported source types"""
        pass
```

#### Format-Specific Implementations

```python
# src/armenian_budget/ingestion/parsers/excel_2019_2024.py
class Excel2019_2024Parser(BudgetParser):
    """Parser for 2019-2024 Excel budget formats"""

    def parse(self, file_path: str, source_type: SourceType) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        # Implementation details for 2019-2024 format
        # State machine parsing logic
        # Armenian text detection and normalization
        pass

    def get_supported_source_types(self) -> List[SourceType]:
        return [SourceType.BUDGET_LAW, SourceType.SPENDING_Q1,
                SourceType.SPENDING_Q12, SourceType.SPENDING_Q123,
                SourceType.SPENDING_Q1234]
```

### Validation Framework

The validation system separates business logic from testing infrastructure:

#### Validation Function Pattern

```python
# src/armenian_budget/validation/financial.py
from typing import List
from .models import ValidationResult

def validate_hierarchical_totals(data: pd.DataFrame, tolerance: float = 0.01) -> ValidationResult:
    """Validate that state body totals = sum of program totals"""
    errors = []
    warnings = []

    for state_body in data["state_body"].unique():
        state_body_data = data[data["state_body"] == state_body]

        # Calculate totals by hierarchy level
        state_body_total = state_body_data["state_body_total"].iloc[0]
        program_totals_sum = state_body_data["program_total"].sum()
        subprogram_totals_sum = state_body_data["subprogram_total"].sum()

        # Check hierarchical consistency
        if abs(state_body_total - program_totals_sum) > tolerance:
            errors.append(f"Hierarchical mismatch for {state_body}: "
                         f"state_body_total={state_body_total}, "
                         f"program_totals_sum={program_totals_sum}")

        if abs(program_totals_sum - subprogram_totals_sum) > tolerance:
            warnings.append(f"Program-subprogram mismatch for {state_body}")

    return ValidationResult(
        passed=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        metadata={"tolerance_used": tolerance, "records_checked": len(data)}
    )
```

#### Validation Integration Pattern

```python
# tests/validation/test_financial_validation.py
import pytest
from armenian_budget.validation.financial import validate_hierarchical_totals

class TestHierarchicalTotals:
    """Test hierarchical total validation"""

    def test_valid_hierarchy_passes(self, sample_budget_data):
        """Test that valid hierarchical data passes validation"""
        result = validate_hierarchical_totals(sample_budget_data.df)

        assert result.passed
        assert len(result.errors) == 0
        assert result.metadata["tolerance_used"] == 0.01

    def test_invalid_hierarchy_fails(self, broken_budget_data):
        """Test that invalid hierarchical data fails validation"""
        result = validate_hierarchical_totals(broken_budget_data.df)

        assert not result.passed
        assert len(result.errors) > 0
        assert "mismatch" in " ".join(result.errors).lower()
```

### Pipeline Orchestration

The main processing pipeline coordinates all components:

```python
# src/armenian_budget/ingestion/pipeline.py
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from ..core.models import SourceType, ProcessingResult, ValidationResult

@dataclass
class FileProcessingInfo:
    """Information about a file to be processed"""
    path: Path
    year: int
    source_type: SourceType
    last_modified: Optional[float] = None
    checksum: Optional[str] = None

class BudgetDataPipeline:
    """Main orchestration pipeline for budget data processing"""

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

        # 3. Process each file using existing parsers
        results = []
        for file_info in files_to_process:
            try:
                # Use existing flatten_budget_excel_* functions
                parsed_data = await self._parse_file_with_existing_logic(file_info)

                # Validate using extracted validation functions
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
        """Use existing parser logic - bridge to current implementation"""
        if file_info.year == 2025:
            # Use existing flatten_budget_excel_2025
            df, overall, _, _ = flatten_budget_excel_2025(str(file_info.path))
        else:
            # Use existing flatten_budget_excel_2019_2024
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

## Key Components Implementation

### Ingestion System

The ingestion system handles file discovery and initial processing:

#### File Discovery Implementation

```python
# src/armenian_budget/ingestion/discovery.py
from pathlib import Path
from typing import List, Optional, Dict, Any
import yaml

def discover_files(year: int, source_type: SourceType,
                  extracted_root: Path, parsers_config: Dict) -> List[Path]:
    """Discover files matching the specified criteria"""

    # Load parser patterns from config
    patterns = parsers_config.get(str(year), parsers_config.get('global', {}))

    # Search in appropriate directory structure
    search_paths = [
        extracted_root / f"{source_type.value}s" / str(year),
        # Additional search paths for different source types
    ]

    discovered_files = []
    for search_path in search_paths:
        if search_path.exists():
            for file_path in search_path.rglob("*.xlsx"):
                if _matches_pattern(file_path, patterns, source_type):
                    discovered_files.append(file_path)

    return discovered_files

def _matches_pattern(file_path: Path, patterns: Dict,
                    source_type: SourceType) -> bool:
    """Check if file matches expected patterns"""
    # Implementation of pattern matching logic
    # Uses Armenian text detection and file structure validation
    pass
```

### Validation System

The validation system implements business rules and data quality checks:

#### Validation Rule Engine

```python
# src/armenian_budget/validation/structural.py
from typing import List, Dict, Any
import pandas as pd
from .models import ValidationResult

class StructuralValidator:
    """Validate data structure and required fields"""

    def __init__(self, rules_config: Dict[str, Any]):
        self.rules = rules_config

    def validate_required_columns(self, data: pd.DataFrame) -> ValidationResult:
        """Validate that all required columns are present"""
        required_columns = self.rules.get('required_columns', [])
        missing_columns = [col for col in required_columns if col not in data.columns]

        return ValidationResult(
            passed=len(missing_columns) == 0,
            errors=[f"Missing required columns: {missing_columns}"] if missing_columns else [],
            metadata={"required_columns": required_columns, "found_columns": list(data.columns)}
        )

    def validate_data_types(self, data: pd.DataFrame) -> ValidationResult:
        """Validate that columns have expected data types"""
        errors = []

        for col, expected_type in self.rules.get('column_types', {}).items():
            if col in data.columns:
                actual_type = str(data[col].dtype)
                if not self._types_compatible(actual_type, expected_type):
                    errors.append(f"Column {col}: expected {expected_type}, got {actual_type}")

        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            metadata={"checked_columns": list(data.columns)}
        )
```

### Storage System

The storage system provides multiple backend options for data persistence:

#### Backend Interface

```python
# src/armenian_budget/storage/backends/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any
import pandas as pd

class StorageBackend(ABC):
    """Abstract base class for storage backends"""

    @abstractmethod
    def save(self, data: pd.DataFrame, file_path: str, **kwargs) -> Dict[str, Any]:
        """Save DataFrame to storage"""
        pass

    @abstractmethod
    def load(self, file_path: str, **kwargs) -> pd.DataFrame:
        """Load DataFrame from storage"""
        pass

    @abstractmethod
    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get file metadata (size, checksum, etc.)"""
        pass
```

#### CSV Backend Implementation

```python
# src/armenian_budget/storage/backends/csv.py
import pandas as pd
from pathlib import Path
import hashlib

class CsvBackend(StorageBackend):
    """CSV storage backend implementation"""

    def save(self, data: pd.DataFrame, file_path: str, **kwargs) -> Dict[str, Any]:
        """Save DataFrame as CSV"""
        compression = kwargs.get('compression', None)
        encoding = kwargs.get('encoding', 'utf-8')

        data.to_csv(file_path, index=False, compression=compression, encoding=encoding)

        # Calculate checksum
        with open(file_path, 'rb') as f:
            checksum = hashlib.sha256(f.read()).hexdigest()

        return {
            'file_path': file_path,
            'format': 'csv',
            'compression': compression,
            'encoding': encoding,
            'rows': len(data),
            'columns': list(data.columns),
            'checksum': checksum
        }

    def load(self, file_path: str, **kwargs) -> pd.DataFrame:
        """Load DataFrame from CSV"""
        compression = kwargs.get('compression', None)
        encoding = kwargs.get('encoding', 'utf-8')

        return pd.read_csv(file_path, compression=compression, encoding=encoding)

    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get CSV file metadata"""
        path = Path(file_path)
        stat = path.stat()

        return {
            'size_bytes': stat.st_size,
            'modified_time': stat.st_mtime,
            'exists': path.exists()
        }
```

## Error Handling Patterns

### Exception Hierarchy

The system defines a clear exception hierarchy for different error types:

```python
# src/armenian_budget/core/exceptions.py
from typing import Optional, Dict, Any

class BudgetToolsError(Exception):
    """Base exception for all budget tools errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}

class ParseError(BudgetToolsError):
    """Raised when Excel file parsing fails"""
    pass

class LabelMismatchError(ParseError):
    """Raised when expected Armenian text labels are not found"""
    pass

class ValidationError(BudgetToolsError):
    """Raised when business rule validation fails"""
    pass

class SourceNotFoundError(BudgetToolsError):
    """Raised when required data source files are not found"""
    pass

class ConfigurationError(BudgetToolsError):
    """Raised when configuration is invalid"""
    pass
```

### Error Recovery

The system implements graceful error recovery patterns:

```python
# src/armenian_budget/ingestion/pipeline.py
async def process_file_with_recovery(self, file_info: FileProcessingInfo) -> ProcessingResult:
    """Process file with comprehensive error recovery"""

    try:
        # Primary processing attempt
        return await self._process_file(file_info)

    except LabelMismatchError as e:
        # Try with relaxed label matching
        self.logger.warning(f"Label mismatch for {file_info.path}, trying relaxed matching")
        try:
            return await self._process_file_relaxed(file_info)
        except Exception:
            raise e  # Re-raise original error if recovery fails

    except ValidationError as e:
        # Continue processing but mark as failed validation
        self.logger.error(f"Validation failed for {file_info.path}: {e}")
        return ProcessingResult(
            success=False,
            records_processed=0,
            validation_result=ValidationResult(
                passed=False,
                errors=[str(e)],
                metadata={"error_type": "validation"}
            )
        )

    except Exception as e:
        # Unexpected error - log and fail
        self.logger.error(f"Unexpected error processing {file_info.path}: {e}")
        return ProcessingResult(
            success=False,
            records_processed=0,
            validation_result=ValidationResult(
                passed=False,
                errors=[f"Unexpected error: {str(e)}"],
                metadata={"error_type": "unexpected"}
            )
        )
```

### Logging Strategy

The logging system provides different levels of detail for different use cases:

```python
# src/armenian_budget/utils/logging.py
import logging
import json
from typing import Dict, Any
from pathlib import Path

class StructuredLogger:
    """Structured logging with JSON output for production"""

    def __init__(self, name: str, log_file: Optional[Path] = None):
        self.logger = logging.getLogger(name)
        self.log_file = log_file

        # Configure handlers
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup console and file handlers"""

        # Console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self._get_console_formatter())
        self.logger.addHandler(console_handler)

        # File handler for production (JSON format)
        if self.log_file:
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setFormatter(self._get_json_formatter())
            self.logger.addHandler(file_handler)

    def _get_console_formatter(self):
        """Human-readable console formatter"""
        return logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def _get_json_formatter(self):
        """JSON formatter for structured logging"""
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    'timestamp': self.formatTime(record),
                    'level': record.levelname,
                    'logger': record.name,
                    'message': record.getMessage(),
                    'module': record.module,
                    'function': record.funcName,
                    'line': record.lineno
                }

                # Add extra fields if present
                if hasattr(record, 'extra_data'):
                    log_entry.update(record.extra_data)

                return json.dumps(log_entry)

        return JsonFormatter()

    def log_processing_event(self, event_type: str, details: Dict[str, Any]):
        """Log structured processing events"""
        self.logger.info(
            f"Processing event: {event_type}",
            extra={'extra_data': details}
        )
```

## Configuration Management

### Sources Configuration

The sources configuration defines available data sources:

```yaml
# config/sources.yaml
sources:
  - name: "2025_budget_law"
    year: 2025
    source_type: "budget_law"
    url: "https://www.gov.am/files/docs/4850.zip"
    file_format: "zip"
    checksum: null
    description: "2025 State Budget Law attachments"

  - name: "2024_spending_q12"
    year: 2024
    source_type: "spending_q12"
    url: "https://minfin.am/website/images/files/72393188f3b5505559d18a66a6a6b89ffdfc829a433af986e6cf72b369d86751.rar"
    file_format: "rar"
    checksum: null
    description: "2024 Q1-Q2 Spending Report"
```

### Parser Configuration

Parser configuration controls file discovery and parsing behavior:

```yaml
# config/parsers.yaml
# Global patterns for file discovery
patterns:
  budget_law: "ծրագիր.*միջոցառում"
  spending: "ծրագիր.*միջոցառում"

# Label tolerance settings
tolerance:
  armenian_text: 0.8
  header_detection: 0.7

# Year-specific overrides
overrides:
  "2025":
    patterns:
      budget_law: "extended.*ծրագիր.*միջոցառում"
    tolerance:
      armenian_text: 0.9

  "2019":
    patterns:
      spending: "modified.*pattern"
```

### Validation Rules

Validation rules define business logic constraints:

```yaml
# config/validation_rules.yaml
rules:
  # Financial validation
  hierarchical_tolerance: 0.01
  execution_rate_bounds: [0.0, 2.0]
  negative_amount_check: true

  # Structural validation
  required_columns:
    - state_body
    - program_code
    - subprogram_total

  column_types:
    state_body: string
    program_code: int64
    subprogram_total: float64

  # Cross-temporal validation
  year_consistency_check: true
  program_code_stability: 0.95
```

## Testing Strategy

### Unit Tests

Unit tests focus on individual components in isolation:

```python
# tests/unit/test_parsers.py
import pytest
from unittest.mock import Mock, patch
from armenian_budget.ingestion.parsers.excel_2019_2024 import Excel2019_2024Parser

class TestExcel2019_2024Parser:
    """Test Excel 2019-2024 parser functionality"""

    def setup_method(self):
        self.parser = Excel2019_2024Parser()

    def test_supported_source_types(self):
        """Test that parser reports correct supported source types"""
        supported = self.parser.get_supported_source_types()

        assert SourceType.BUDGET_LAW in supported
        assert SourceType.SPENDING_Q1 in supported
        assert len(supported) == 5

    @patch('pandas.read_excel')
    def test_parse_budget_law_success(self, mock_read_excel):
        """Test successful budget law parsing"""
        # Mock Excel file reading
        mock_df = pd.DataFrame({
            'state_body': ['Ministry A', 'Ministry A'],
            'program_total': [100.0, 200.0],
            'subprogram_total': [50.0, 150.0]
        })
        mock_read_excel.return_value = mock_df

        result_df, overall = self.parser.parse('/fake/path.xlsx', SourceType.BUDGET_LAW)

        assert len(result_df) == 2
        assert 'overall' in overall
        assert overall['overall'] > 0

    def test_parse_invalid_file_raises_error(self):
        """Test that invalid files raise appropriate errors"""
        with pytest.raises(ParseError):
            self.parser.parse('/nonexistent/file.xlsx', SourceType.BUDGET_LAW)
```

### Integration Tests

Integration tests verify component interactions:

```python
# tests/integration/test_pipeline.py
import pytest
from pathlib import Path
import tempfile
import shutil
from armenian_budget.ingestion.pipeline import BudgetDataPipeline

class TestBudgetDataPipeline:
    """Test end-to-end pipeline functionality"""

    def setup_method(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.pipeline = BudgetDataPipeline(self.temp_dir / 'config')

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    @pytest.mark.asyncio
    async def test_process_single_file_success(self, sample_excel_file):
        """Test successful processing of a single file"""
        # Setup test data
        test_file = self.temp_dir / 'extracted' / 'budget_laws' / '2023' / 'test.xlsx'
        test_file.parent.mkdir(parents=True)
        shutil.copy(sample_excel_file, test_file)

        # Process file
        result = await self.pipeline.process_file(
            year=2023,
            source_type=SourceType.BUDGET_LAW,
            input_path=str(test_file)
        )

        # Verify results
        assert result.success
        assert result.records_processed > 0
        assert len(result.output_files) > 0

        # Check output files exist
        for output_file in result.output_files:
            assert Path(output_file).exists()

    @pytest.mark.asyncio
    async def test_process_with_validation_failure(self, invalid_excel_file):
        """Test processing with validation failures"""
        # Setup invalid test data
        test_file = self.temp_dir / 'extracted' / 'budget_laws' / '2023' / 'invalid.xlsx'
        test_file.parent.mkdir(parents=True)
        shutil.copy(invalid_excel_file, test_file)

        # Process file
        result = await self.pipeline.process_file(
            year=2023,
            source_type=SourceType.BUDGET_LAW,
            input_path=str(test_file)
        )

        # Verify failure handling
        assert not result.success
        assert result.validation_result is not None
        assert not result.validation_result.passed
        assert len(result.validation_result.errors) > 0
```

### Data Validation Tests

Data validation tests ensure quality of processed outputs:

```python
# tests/data_validation/test_budget_law_validation.py
import pytest
import pandas as pd
from armenian_budget.validation.financial import validate_hierarchical_totals

class TestBudgetLawValidation:
    """Test validation of processed budget law data"""

    def test_hierarchical_totals_valid_data(self, processed_budget_law_csv):
        """Test hierarchical totals validation on real processed data"""
        data = pd.read_csv(processed_budget_law_csv)

        result = validate_hierarchical_totals(data)

        assert result.passed, f"Validation failed: {result.errors}"
        assert len(result.warnings) >= 0  # Warnings are OK

    def test_no_negative_amounts(self, processed_budget_law_csv):
        """Test that no negative amounts exist in processed data"""
        data = pd.read_csv(processed_budget_law_csv)

        # Check for negative amounts in financial columns
        financial_columns = [col for col in data.columns if 'total' in col.lower()]

        for col in financial_columns:
            negative_count = (data[col] < 0).sum()
            assert negative_count == 0, f"Found {negative_count} negative values in {col}"

    def test_required_columns_present(self, processed_budget_law_csv):
        """Test that all required columns are present"""
        data = pd.read_csv(processed_budget_law_csv)

        required_columns = [
            'state_body', 'program_code', 'program_name',
            'subprogram_code', 'subprogram_name', 'subprogram_total'
        ]

        for col in required_columns:
            assert col in data.columns, f"Missing required column: {col}"

    def test_data_types_correct(self, processed_budget_law_csv):
        """Test that columns have correct data types"""
        data = pd.read_csv(processed_budget_law_csv)

        # String columns should not be numeric
        string_columns = ['state_body', 'program_name', 'subprogram_name']
        for col in string_columns:
            assert data[col].dtype == 'object', f"Column {col} should be string, got {data[col].dtype}"

        # Numeric columns should be numeric
        numeric_columns = ['program_code', 'subprogram_code', 'subprogram_total']
        for col in numeric_columns:
            assert pd.api.types.is_numeric_dtype(data[col]), f"Column {col} should be numeric"
```

## Performance Considerations

### Vectorization Patterns

The system uses pandas vectorized operations for performance:

```python
# Efficient data processing patterns
def process_budget_data_efficient(data: pd.DataFrame) -> pd.DataFrame:
    """Process budget data using vectorized operations"""

    # Vectorized calculations
    data['execution_rate'] = data['actual'] / data['planned']
    data['variance'] = data['actual'] - data['planned']
    data['variance_percent'] = (data['variance'] / data['planned']) * 100

    # Vectorized filtering
    valid_data = data[
        (data['execution_rate'] >= 0) &
        (data['execution_rate'] <= 2.0) &
        (data['planned'] > 0)
    ]

    # Vectorized grouping and aggregation
    summary = data.groupby(['state_body', 'year']).agg({
        'planned': 'sum',
        'actual': 'sum',
        'execution_rate': 'mean'
    }).reset_index()

    return valid_data, summary
```

### Memory Management

Large dataset processing with memory efficiency:

```python
# src/armenian_budget/ingestion/pipeline.py
class MemoryEfficientPipeline:
    """Pipeline optimized for large dataset processing"""

    def __init__(self, chunk_size: int = 10000):
        self.chunk_size = chunk_size

    def process_large_file(self, file_path: str) -> pd.DataFrame:
        """Process large files in chunks to manage memory"""

        results = []

        # Process file in chunks
        for chunk in pd.read_csv(file_path, chunksize=self.chunk_size):
            # Process chunk
            processed_chunk = self._process_chunk(chunk)

            # Validate chunk
            validation_result = self._validate_chunk(processed_chunk)

            if validation_result.passed:
                results.append(processed_chunk)
            else:
                self.logger.warning(f"Chunk validation failed: {validation_result.errors}")

        # Combine results efficiently
        if results:
            return pd.concat(results, ignore_index=True)
        else:
            return pd.DataFrame()

    def _process_chunk(self, chunk: pd.DataFrame) -> pd.DataFrame:
        """Process individual chunk"""
        # Vectorized processing
        chunk['processed_total'] = chunk['raw_total'] * self.exchangerate
        return chunk

    def _validate_chunk(self, chunk: pd.DataFrame) -> ValidationResult:
        """Validate individual chunk"""
        # Chunk-level validation
        return validate_chunk_data(chunk)
```

### File I/O Optimization

Efficient file operations for large datasets:

```python
# src/armenian_budget/storage/optimized_io.py
import pandas as pd
from typing import Iterator, Dict, Any

class OptimizedFileIO:
    """Optimized file I/O operations"""

    @staticmethod
    def save_large_dataframe(df: pd.DataFrame, file_path: str,
                           compression: str = 'gzip', chunksize: int = 100000):
        """Save large DataFrame efficiently"""

        with pd.io.common.get_handle(file_path, 'w', compression=compression) as f:
            # Write header
            df.head(0).to_csv(f, index=False)

            # Write data in chunks
            for i in range(0, len(df), chunksize):
                chunk = df.iloc[i:i + chunksize]
                chunk.to_csv(f, header=False, index=False)

    @staticmethod
    def stream_csv_processing(file_path: str, processor_func,
                            chunksize: int = 50000) -> Iterator[Dict[str, Any]]:
        """Stream process CSV file"""

        for chunk in pd.read_csv(file_path, chunksize=chunksize):
            # Process chunk
            result = processor_func(chunk)

            # Yield results without loading everything into memory
            yield result

    @staticmethod
    def parallel_file_processing(file_paths: List[str],
                               processor_func, max_workers: int = 4):
        """Process multiple files in parallel"""

        from concurrent.futures import ProcessPoolExecutor
        import multiprocessing as mp

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Process files in parallel
            futures = [executor.submit(processor_func, path) for path in file_paths]

            # Collect results
            results = []
            for future in futures:
                try:
                    result = future.result(timeout=300)  # 5 minute timeout
                    results.append(result)
                except Exception as e:
                    logger.error(f"File processing failed: {e}")
                    results.append(None)

            return results
```

## Development Workflow

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/gituzh/budget-am.git
cd budget-am

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install in development mode
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Run initial setup
python scripts/bootstrap.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=armenian_budget --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration
pytest tests/validation/

# Run tests for specific module
pytest tests/test_ingestion.py -v

# Run tests in parallel
pytest -n auto
```

### Code Quality

```bash
# Run linting
ruff check src/
black --check src/

# Auto-fix issues
ruff check --fix src/
black src/

# Type checking
mypy src/armenian_budget/

# Security scanning
bandit -r src/
```

### Contributing Guidelines

1. **Branch Strategy**

   ```bash
   # Create feature branch
   git checkout -b feature/your-feature-name

   # Create bugfix branch
   git checkout -b bugfix/issue-description
   ```

2. **Code Standards**

   - Follow Google Python Style Guide
   - Use type hints for all function parameters and return values
   - Write comprehensive docstrings
   - Add unit tests for new functionality

3. **Testing Requirements**

   - All new code must have unit tests
   - Integration tests for new features
   - Data validation tests for parser changes
   - Minimum 80% code coverage

4. **Documentation Updates**

   - Update API documentation for new functions
   - Add examples for new features
   - Update implementation guide for architectural changes

5. **Pull Request Process**

   ```bash
   # Ensure all tests pass
   pytest --cov=armenian_budget --cov-fail-under=80

   # Run linting and type checking
   ruff check src/
   mypy src/armenian_budget/

   # Update CHANGELOG.md
   # Update version if needed

   # Create pull request with description
   ```

6. **Code Review Checklist**
   - [ ] Code follows style guidelines
   - [ ] Type hints are complete
   - [ ] Docstrings are comprehensive
   - [ ] Unit tests are included
   - [ ] Integration tests pass
   - [ ] Documentation is updated
   - [ ] No breaking changes without migration path
