# Armenian Budget Tools - Architecture

> **When to read this:** System architects, technical leads, and developers who need to understand high-level design decisions, component boundaries, and scalability patterns. For implementation details and code examples, see [`developer_guide.md`](developer_guide.md).

## Table of Contents

- [Armenian Budget Tools - Architecture](#armenian-budget-tools---architecture)
  - [Table of Contents](#table-of-contents)
  - [1. Architecture Vision](#1-architecture-vision)
  - [2. Design Principles](#2-design-principles)
    - [Core Architectural Principles](#core-architectural-principles)
    - [Technical Constraints](#technical-constraints)
    - [Security Principles](#security-principles)
  - [3. System Components](#3-system-components)
    - [High-Level Component Architecture](#high-level-component-architecture)
    - [Component Responsibilities](#component-responsibilities)
    - [Repository Structure](#repository-structure)
  - [4. Data Flow Architecture](#4-data-flow-architecture)
    - [Processing Pipeline](#processing-pipeline)
    - [Data Stages](#data-stages)
    - [Architectural Patterns](#architectural-patterns)
  - [5. Module Boundaries \& Responsibilities](#5-module-boundaries--responsibilities)
    - [Core Module Dependencies](#core-module-dependencies)
    - [Dependency Rules](#dependency-rules)
    - [Interface Contracts](#interface-contracts)
  - [6. Integration Patterns](#6-integration-patterns)
    - [CLI Integration](#cli-integration)
    - [Python API Integration](#python-api-integration)
    - [MCP Server Integration](#mcp-server-integration)
  - [7. Scalability \& Performance Considerations](#7-scalability--performance-considerations)
    - [Performance Architecture](#performance-architecture)
    - [Scalability Patterns](#scalability-patterns)
  - [8. Security Architecture](#8-security-architecture)
    - [Data Security](#data-security)
    - [Access Control](#access-control)
    - [Audit \& Logging](#audit--logging)
  - [9. Future Architecture Considerations](#9-future-architecture-considerations)
    - [Post-v1 Enhancements](#post-v1-enhancements)
    - [Migration Strategies](#migration-strategies)
  - [10. Related Documentation](#10-related-documentation)

## 1. Architecture Vision

Armenian Budget Tools provides robust, deterministic processing of official Armenian state budget data while maintaining flexibility for future enhancements. The system emphasizes:

- **Data Integrity**: Clear lineage tracking from original government sources to processed outputs
- **Progressive Enhancement**: Modular design allowing phased feature development
- **Configuration-Driven**: Externalized settings to adapt to changing data formats
- **Multi-Interface Support**: CLI, Python API, and MCP server for different user needs

## 2. Design Principles

### Core Architectural Principles

- **Incremental Evolution**: Preserve working code while enabling gradual enhancement
- **Separation of Concerns**: Clear boundaries between data processing, validation, and interfaces
- **Configuration-Driven**: Externalized settings for adaptability to changing requirements
- **Data Integrity**: Comprehensive lineage tracking from source to output
- **Error Resilience**: Graceful error handling with clear recovery paths
- **Performance-First**: Vectorized operations and efficient resource usage

### Technical Constraints

- **Platform**: Python 3.10+ with macOS/Linux primary support
- **Data Formats**: Excel-based parsing (2019–2025), structured for future PDF support
- **Performance**: Vectorized pandas operations with memory-conscious processing
- **Reliability**: Typed exceptions, deterministic outputs, tolerance-aware comparisons
- **Compatibility**: No `sys.exit` in library code, clear error hierarchies

### Security Principles

- **Data Provenance**: Cryptographic checksums for integrity verification
- **Access Control**: No arbitrary code execution in data processing
- **Input Validation**: Comprehensive validation at all entry points
- **Audit Trail**: Complete logging of all processing operations

## 3. System Components

### High-Level Component Architecture

```text
┌────────────────────────────────────────────────────────────┐
│                   User Interfaces Layer                    │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │   CLI    │    │  Python API  │    │   MCP Server     │  │
│  └──────────┘    └──────────────┘    └──────────────────┘  │
└──────────────────────────┬─────────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────────┐
│                   Core Processing Layer                    │
│  ┌──────────┐    ┌──────────┐    ┌────────────────────┐    │
│  │ Ingestion│◄───┤Discovery │    │    Validation      │    │
│  │ Pipeline │    │  System  │    │     Framework      │    │
│  └──────────┘    └──────────┘    └────────────────────┘    │
└──────────────────────────┬─────────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────────┐
│                   Infrastructure Layer                     │
│  ┌──────────┐    ┌──────────┐    ┌────────────────────┐    │
│  │ Storage  │    │  Sources │    │   Configuration    │    │
│  │ Backends │    │ Registry │    │    Management      │    │
│  └──────────┘    └──────────┘    └────────────────────┘    │
└────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

**User Interfaces Layer:**
- **CLI**: Command-line interface for batch processing and automation
- **Python API**: Programmatic access for custom workflows
- **MCP Server**: AI-assisted analysis and querying

**Core Processing Layer:**
- **Ingestion Pipeline**: Orchestrates file processing, parsing, and validation
- **Discovery System**: Automatic file detection and pattern matching
- **Validation Framework**: Business rule validation and data quality checks

**Infrastructure Layer:**
- **Storage Backends**: CSV and Parquet persistence with metadata
- **Sources Registry**: Official data source URLs and download management
- **Configuration Management**: YAML-based settings for all components

### Repository Structure

```text
src/armenian_budget/
├── core/                   # Core data models and types
├── ingestion/              # Parsing and discovery
├── validation/             # Business rules
├── sources/                # Download and registry
├── storage/                # Persistence layer
├── interfaces/             # CLI, API, MCP
└── utils/                  # Shared utilities

config/                     # Configuration files
├── sources.yaml
├── parsers.yaml
└── validation_rules.yaml

data/                       # Data directories
├── original/               # Downloaded archives
├── extracted/              # Unarchived files
└── processed/              # Normalized outputs
```

## 4. Data Flow Architecture

### Processing Pipeline

```text
┌─────────────┐
│  Download   │  1. Fetch from minfin.am
│   & Store   │     with checksum verification
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Extract   │  2. Unarchive RAR/ZIP
│   & Index   │     with discovery indexing
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Parse    │  3. State-machine parsing
│  & Flatten  │     with Armenian text detection
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Validate   │  4. Business rule checks
│  & Report   │     with tolerance handling
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Persist   │  5. CSV + metadata
│  & Analyze  │     with lineage tracking
└─────────────┘
```

### Data Stages

**Stage 1: Original Archives**
- Government archives with original filenames preserved
- SHA-256 checksums for integrity verification
- Download metadata with timestamps and URLs

**Stage 2: Extracted Files**
- Unarchived Excel files ready for parsing
- Discovery index with file metadata
- Pattern-based file detection

**Stage 3: Processed Data**
- Normalized CSV with consistent schema
- Overall totals JSON for validation
- Processing metadata and lineage

### Architectural Patterns

- **Pipeline Pattern**: Sequential processing with error recovery
- **Observer Pattern**: Event-driven status reporting and logging
- **Factory Pattern**: Parser selection based on file format and year
- **Repository Pattern**: Abstracted data access across storage backends
- **Strategy Pattern**: Validation rules selected by source type

## 5. Module Boundaries & Responsibilities

### Core Module Dependencies

```text
interfaces/         (User-facing)
    ↓
ingestion/          (Orchestration)
    ↓
validation/         (Business logic)
    ↓
storage/            (Persistence)
    ↓
core/               (Data models)

sources/ ←→ utils/  (Infrastructure support)
```

### Dependency Rules

1. **Core** has zero dependencies on other modules (foundation)
2. **Validation** depends only on core (reusable business logic)
3. **Ingestion** depends on core and validation (orchestration)
4. **Interfaces** depend on all above but not vice versa (presentation)
5. **Configuration** is injected, not hardcoded

### Interface Contracts

**Parser Interface:**
- Input: Excel file path, source type
- Output: Flattened DataFrame, overall totals, diagnostics
- Errors: Typed exceptions (ParseError, LabelMismatchError)

**Validation Interface:**
- Input: DataFrame, validation rules
- Output: ValidationResult with passed/errors/warnings
- Errors: ValidationError for severe issues

**Storage Interface:**
- Input: DataFrame, file path, format
- Output: Storage metadata with checksum
- Errors: IOError for write failures

## 6. Integration Patterns

### CLI Integration

- Command pattern for extensibility
- Exit codes mapped from typed exceptions
- Structured logging with progress reporting
- Configuration injection via environment and flags

### Python API Integration

- Mirror CLI functionality for consistency
- Type hints for all public functions
- No global state (pure functions where possible)
- Clear error propagation

### MCP Server Integration

- Resource-based for static data (state bodies, programs)
- Tool-based for dynamic queries and analysis
- Result size detection (inline vs file output)
- Filesystem abstraction for read-only environments

## 7. Scalability & Performance Considerations

### Performance Architecture

**Vectorization Strategy:**
- Pandas-based processing for computational efficiency
- Avoid Python loops for DataFrame operations
- Leverage built-in aggregation and grouping

**Memory Management:**
- Chunked processing for large datasets (configurable size)
- Garbage collection hints after large operations
- Streaming for MCP server responses

**Parallel Processing:**
- File-level parallelism (independent processing)
- No shared state between file processors
- Future: Process pool for multi-file batches

### Scalability Patterns

**Horizontal Scaling:**
- Stateless processing enables distributed execution
- File-based parallelism (no cross-file dependencies)
- MCP server can run multiple instances

**Resource Pooling:**
- Connection pooling for future database backends
- File handle reuse for large batch operations

**Caching Strategy:**
- Discovery index cached to disk
- Parsed data cached with invalidation by checksum
- MCP server response caching (future)

## 8. Security Architecture

### Data Security

**Integrity Verification:**
- SHA-256 checksums for all downloaded files
- Checksum validation before processing
- Metadata tracking with provenance chain

**Input Validation:**
- File path sanitization (no arbitrary paths)
- Source type validation against enum
- Configuration schema validation at startup

**No Code Execution:**
- No eval(), exec(), or dynamic imports from data
- YAML safe loading only
- Sandboxed parsing (no macros, no scripts)

### Access Control

- No authentication in v1 (local tool)
- MCP server stdio mode (controlled by client)
- HTTP mode for testing only (not production)

### Audit & Logging

- Complete processing logs with timestamps
- Validation results persisted
- Error stack traces for debugging

## 9. Future Architecture Considerations

### Post-v1 Enhancements

**Database Backend:**
- PostgreSQL or DuckDB for larger datasets
- SQL query interface for advanced filtering
- Incremental updates (append-only processing)

**Advanced Analytics:**
- Time-series analysis module
- Anomaly detection with ML models
- Cross-temporal trend analysis

**PDF Parsing:**
- OCR integration for 2017-2018 data
- Template-based extraction
- Quality scoring for OCR results

**Multi-language Support:**
- English field name translation
- Armenian-English bidirectional mapping
- Configurable output language

### Migration Strategies

**Backward Compatibility:**
- API versioning for breaking changes
- Deprecation warnings with migration guides
- Legacy parser support for old formats

**Extension Mechanisms:**
- Plugin architecture for custom parsers
- Validation rule plugins
- Custom MCP tools registration

## 10. Related Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| **[README.md](../README.md)** | Quick start and user guide | All users |
| **[docs/prd.md](prd.md)** | Product requirements | Product team |
| **[docs/developer_guide.md](developer_guide.md)** | Implementation patterns and code | Contributors |
| **[docs/data_schemas.md](data_schemas.md)** | Data formats and schemas | Data analysts |
| **[docs/mcp.md](mcp.md)** | MCP server integration | AI developers |
| **[docs/roadmap.md](roadmap.md)** | Development milestones | All contributors |

---

**Navigation:**
- **For implementation details** → See [`developer_guide.md`](developer_guide.md)
- **For data specifications** → See [`data_schemas.md`](data_schemas.md)
- **For product scope** → See [`prd.md`](prd.md)
