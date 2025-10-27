# Armenian Budget Tools - Architecture

> **When to read this:** System architects, technical leads, and developers who need to understand high-level design decisions and system organization. For implementation details and code examples, see [`developer_guide.md`](developer_guide.md).
>
> **Documentation Philosophy:** This document is kept minimal and purposeful—documenting only design decisions that cannot be understood from reading the code itself.

## Table of Contents

- [Armenian Budget Tools - Architecture](#armenian-budget-tools---architecture)
  - [Table of Contents](#table-of-contents)
  - [1. Architecture Vision](#1-architecture-vision)
  - [2. Design Principles](#2-design-principles)
  - [3. System Overview](#3-system-overview)
  - [4. Data Flow](#4-data-flow)
  - [5. Repository Structure](#5-repository-structure)
  - [6. Access Methods](#6-access-methods)
  - [7. Future Considerations](#7-future-considerations)
  - [8. Related Documentation](#8-related-documentation)

## 1. Architecture Vision

Armenian Budget Tools transforms official Armenian state budget data into openly available, analysis-ready datasets. The system prioritizes:

- **Open data accessibility**: Clean, validated CSV outputs ready for public use and analysis
- **Data quality assurance**: Rigorous validation to minimize errors and ensure financial integrity
- **Data provenance**: Complete lineage tracking from original government sources to processed outputs
- **Multiple access methods**: CLI for automation, MCP server for AI assistance

## 2. Design Principles

- **Incremental evolution**: Preserve working code while enabling gradual enhancement
- **Separation of concerns**: Clear boundaries between ingestion, validation, and interfaces
- **Data integrity**: Checksum verification, hierarchical validation, and tolerance-based comparisons
- **Error resilience**: Graceful handling with typed exceptions and clear recovery paths
- **Configuration-driven**: YAML-based settings adapt to changing data formats without code changes

**Technical constraints:**

- Python 3.10+ (macOS/Linux primary support)
- Excel parsing (2019-2025 formats)
- Vectorized data operations

## 3. System Overview

**Core components:**

- **Interfaces**: CLI commands and MCP server tools (public interfaces)
- **Ingestion**: Excel parsers with state-machine row detection, discovery system for file finding
- **Validation**: Business rules (hierarchical totals, spending percentages, cross-validation)
- **Storage**: CSV writer with metadata, JSON for overall totals
- **Configuration**: YAML files for sources, parsers, and validation rules

## 4. Data Flow

The processing pipeline transforms government archives into validated datasets:

```text
┌─────────────┐
│  Download   │  1. Fetch from minfin.am with SHA-256 checksum verification
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Extract   │  2. Unarchive RAR/ZIP to extracted directory
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Discover   │  3. Find best file match using patterns, build discovery index
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Parse    │  4. State-machine parsing with Armenian text detection
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Validate   │  5. Business rule checks with tolerance handling
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Persist   │  6. Write CSV + JSON with metadata and lineage tracking
└─────────────┘
```

**Data locations:**

- `data/original/` - Downloaded archives with checksums
- `data/extracted/` - Unarchived Excel files + discovery index
- `data/processed/csv/` - Final CSV outputs + overall totals JSON

## 5. Repository Structure

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
└── parsers.yaml

data/                       # Data directories
├── original/               # Downloaded archives
├── extracted/              # Unarchived files
└── processed/              # Normalized outputs
```

## 6. Access Methods

The system provides two public interfaces:

**CLI (Command-line interface):**

- Primary public interface for batch processing and automation
- Commands: `download`, `extract`, `discover`, `process`, `validate`, `mcp-server`
- Exit codes from typed exceptions, structured logging with progress reporting

**MCP Server:**

- Public interface for AI-assisted analysis via Model Context Protocol
- Resources for static data (state bodies, programs, subprograms)
- Tools for dynamic queries (spending analysis, budget comparisons)
- Returns inline data for small results, file paths for large datasets

**Internal Python API:**

- For internal library use only (not a public interface)
- Type-hinted functions for CLI and MCP implementations
- See `docs/developer_guide.md` for internal API reference

## 7. Future Considerations

Post-v1 enhancements under consideration:

- **PDF parsing**: OCR integration for 2017-2018 budget data
- **Multi-language support**: English translations for field names and outputs
- **Advanced analytics**: Time-series analysis, trend detection, anomaly detection

## 8. Related Documentation

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
