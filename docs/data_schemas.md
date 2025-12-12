# Data Schema and Formats

## 1. Data Pipeline Overview

The Armenian Budget Tools processes official government budget data through a multi-stage pipeline. For the complete data flow diagram, see [architecture.md](architecture.md#4-data-flow).

**Key Characteristics:**

- **Original sources**: Archives downloaded from minfin.am containing multiple Excel files
- **Extraction**: Unarchiving reveals inconsistent folder structures across years
- **Processing**: Currently parses budget program breakdowns; future expansion to other components
- **Output**: Normalized CSVs with consistent column schemas across years

## 2. Data Folder Structure

```text
data/
├── original/           # Downloaded archives (original filenames preserved)
│   ├── budget_laws/    # Original .rar/.zip files from budget law pages
│   │   └── 2023/
│   │       └── Orenqi havelvacner_Excel.rar  # Original archive name
│   └── spending_reports/ # Original .rar/.zip files from execution reports
│       └── 2023/
│           └── f601731c.rar  # Original archive name (hash-based)
├── extracted/          # Unarchived source files
│   ├── budget_laws/    # Year folders with .xlsx/.xls files
│   │   ├── 2023/
│   │       └── 1.1.ORENQI HAVELVACNER/  # Extracted folder structure
│   │           ├── 1.Հավելված N1 աղյուսակ N1.Ամփոփ ըստ ծրագրերի.xls
│   │           └── [other budget components]
│   └── spending_reports/ # Organized by year/quarter
│       ├── 2023/
│       │   ├── Q1/
│       │   │   └── f601731c/  # Extracted folder (original hash name)
│       │   │       └── 4.Հավելվածներ/
│       │   │           ├── 1. 2023_I եռամսյակ_ամփոփ ըստ ծրագրերի.xls
│       │   │           └── [other spending components]
│       │   └── [Q12, Q123, Q1234]
└── processed/          # Normalized outputs
    ├── csv/            # {year}_{SOURCE_TYPE}.csv files
    └── processing_report.json
```

**Naming Conventions:**

- **Archives**: Original filenames from minfin.am (e.g., `Orenqi havelvacner_Excel.rar`, hash-based names)
- **Extracted Folders**: Varies by archive structure (may preserve archive name or use internal folder names)
- **Processed CSVs**: `{year}_{SOURCE_TYPE}.csv` (e.g., `2023_BUDGET_LAW.csv`)
- **Source Types**: `BUDGET_LAW`, `SPENDING_Q1`, `SPENDING_Q12`, `SPENDING_Q123`, `SPENDING_Q1234`, `MTEP`

## 3. Original Data Archives

### 3.1 Archive Sources and Web Pages

**Budget Law Archives:**

- **Source Page**: [State Budget Law](https://minfin.am/hy/page/petakan_byuj/) - "Պետական բյուջե"
- **Years Available**: 2019-2025
- **Format**: RAR/ZIP archives containing multiple Excel files
- **Current Scope**: Only parsing program summary (Ամփոփ ըստ ծրագրերի)

**Note:** 2017-2018 budget laws are PDF-only format and are not currently supported. Before 2019, the Armenian budget was not programmatic (program-based), so the data structure differs significantly from later years.

**Spending Report Archives:**

- **Source Page**: [Budget Execution Reports](https://minfin.am/hy/page/hy_hashvetvutyunner/) - "Պետական բյուջեեի կատարման մասին հաշվետվություններ"
- **Years Available**: 2019-2025
- **Quarters**: Q1, Q12, Q123, Q1234
- **Format**: RAR/ZIP archives with nested folder structures

**MTEP Archives:**

- **Source Page**: [Mid-Term Expenditure Program](https://minfin.am/hy/page/petakan_mijnazhamket_tsakhseri_tsragre/) - "Պետական միջնաժամկետ ծախսերի ծրագրե"
- **Years Available**: 2024+
- **Format**: RAR/ZIP archives
- **Purpose**: Multi-year budget projections (3-year horizon)

### 3.2 Data Source Registry

Official download URLs and metadata for all government archives are maintained in `config/sources.yaml`:

- **Purpose**: Centralized registry of all official data sources with direct download links
- **Content**: Year, source type, URL, file format, and human-readable descriptions
- **Source**: Direct URLs from minfin.am government website pages
- **Usage**: Powers the download system and ensures data provenance

### 3.3 Archive Contents and Future Components

Archives contain multiple budget components beyond the currently parsed program summaries:

**Budget Law Archives:**
- **Currently Parsed**: Program summary (Ամփոփ ըստ ծրագրերի) → `BUDGET_LAW`
- **Available for Future**: Capital expenditures, loan programs, grants, subsidies, deficit financing, administrative costs, environmental fees, and other budget components

**Spending Report Archives:**
- **Currently Parsed**: Program summary (ամփոփ ըստ ծրագրերի)
- **Available for Future**: Detailed breakdowns by responsible entity and activity, loan programs, grants, deficit financing

## 4. Original Table Organization

### 4.1 BUDGET_LAW Tables (Currently Parsed)

**Discovery Pattern:** `config/parsers.yaml` patterns match Armenian word fragments "ծրագ" (program) and "միջոց" (measure)

**Structure:** 3-level hierarchy (State Body → Program → Subprogram) with Armenian headers and hierarchical totals. Annual budget allocations in AMD. 2025 format adds extended program codes (`program_code_ext`).

### 4.2 SPENDING Tables (Execution Reports)

**Discovery Pattern:** Same `config/parsers.yaml` patterns as budget law files

**Structure:** 3-level hierarchy (State Body → Program → Subprogram) with plan vs actual columns. Includes original/revised annual plans, period plans (Q1/Q12/Q123 only), actual spending, and execution rates (%). Q1234 reports contain only annual metrics.

### 4.3 MTEP Tables (Mid-Term Expenditure Program)

**Discovery Pattern:** `config/parsers.yaml` pattern "միջնաժամկետ.*ծախսերի.*ծրագիր"

**Structure:** 2-level hierarchy (State Body → Program only, no subprograms). Multi-year projections (3-year horizon) with year-specific columns (y0, y1, y2). Overall JSON contains `plan_years` array with calendar years. Available from 2024+.

## 5. Extracted Data

**Extraction Process:**

- **Tools Required**: `unar` (recommended) or `unrar` for RAR files; standard `unzip` for ZIP
- **Inconsistent Structures**: Each archive has unique folder organization
- **File Discovery**: Pattern-based matching to identify relevant Excel files
- **Intermediate Format**: Preserves original .xlsx/.xls files before processing
- **Integrity Verification**: SHA-256 checksums recorded in `config/checksums.yaml` after downloads
- **Download Optimization**: Checksums enable skip_existing logic to avoid redundant downloads

**Discovery Strategy:**

- Pattern matching on file names and content
- Configuration-driven file selection via `config/parsers.yaml`
- Fallback to manual file specification when auto-discovery fails
- **Discovery Caching**: Results cached in `data/extracted/discovery_index.json` with file metadata
- **Metadata Tracking**: File size, modification time, checksum, and matching pattern stored for reproducibility

## 6. Processed Data

### 6.1 Output Formats

**CSV Files:**

- **Location**: `data/processed/`
- **Naming**: `{year}_{SOURCE_TYPE}.csv`
- **Format**: UTF-8 encoded CSV with Armenian text support

**Metadata:**

- **Processing Report**: `data/processed/processing_report.json`
- **Checksums**: SHA-256 hashes recorded in `config/checksums.yaml` for download integrity verification
- **Discovery Index**: `data/extracted/discovery_index.json`

### 6.2 Data Structure

**CSV Structure:** Flattened rows with hierarchical totals (no joins needed for analysis).

- **3-level sources (BUDGET_LAW, SPENDING):** Each row = one subprogram with parent totals
- **2-level source (MTEP):** Each row = one program (subprogram columns empty for compatibility)

**Overall JSON:** Each processed file produces a companion `*_overall.json` with grand totals for validation. Budget Law contains a single total; Spending contains multiple aggregates (annual_plan, rev_annual_plan, actual, execution rates); MTEP contains multi-year totals and plan_years array.

## 7. Complete Column Reference

### BUDGET_LAW Fields

| Field | Description | Type | Availability |
|-------|-------------|------|--------------|
| `state_body` | State body/ministry/agency name | string | 2019+ |
| `program_code` | Program identifier | string | 2019+ |
| `program_code_ext` | Extended program code (e.g., "12-345") | string | 2025+ |
| `program_name` | Program name | string | 2019+ |
| `program_goal` | Program goal description | string | 2019+ |
| `program_result_desc` | Program result description | string | 2019+ |
| `subprogram_code` | Subprogram identifier | string | 2019+ |
| `subprogram_name` | Subprogram name | string | 2019+ |
| `subprogram_desc` | Subprogram description | string | 2019+ |
| `subprogram_type` | Subprogram type/category | string | 2019+ |
| `*_total` | Total allocated amount | numeric | 2019+ |

**Wildcard (`*`) represents:** `state_body`, `program`, `subprogram` (CSV); `overall` (JSON)

### SPENDING Fields

| Field | Description | Type | Availability |
|-------|-------------|------|--------------|
| `state_body` | State body/ministry/agency name | string | 2019+ |
| `program_code` | Program identifier | string | 2019+ |
| `program_code_ext` | Extended program code (e.g., "12-345") | string | 2025+ |
| `program_name` | Program name | string | 2019+ |
| `program_goal` | Program goal description | string | 2019+ |
| `program_result_desc` | Program result description | string | 2019+ |
| `subprogram_code` | Subprogram identifier | string | 2019+ |
| `subprogram_name` | Subprogram name | string | 2019+ |
| `subprogram_desc` | Subprogram description | string | 2019+ |
| `subprogram_type` | Subprogram type/category | string | 2019+ |
| `*_annual_plan` | Original annual allocation | numeric | 2019+ |
| `*_rev_annual_plan` | Revised annual plan | numeric | 2019+ |
| `*_period_plan` | Original period allocation | numeric | Q1, Q12, Q123 (2019+) |
| `*_rev_period_plan` | Revised period plan | numeric | Q1, Q12, Q123 (2019+) |
| `*_actual` | Actual spending | numeric | 2019+ |
| `*_actual_vs_rev_annual_plan` | Execution rate vs revised annual plan (%) | numeric | 2019+ |
| `*_actual_vs_rev_period_plan` | Execution rate vs revised period plan (%) | numeric | Q1, Q12, Q123 (2019+) |

**Wildcard (`*`) represents:** `state_body`, `program`, `subprogram` (CSV); `overall` (JSON)

### MTEP Fields

**Structure:** 2-level hierarchy (State Body → Program). Subprogram fields retained for schema compatibility but left empty. Multi-year projections with year-specific columns (y0, y1, y2).

| Field | Description | Type | Availability |
|-------|-------------|------|--------------|
| `state_body` | State body/ministry/agency name | string | 2024+ |
| `program_code` | Program identifier | string | 2024+ |
| `program_name` | Program name | string | 2024+ |
| `program_goal` | Program goal description (optional) | string | 2024+ |
| `program_result_desc` | Program result description (optional) | string | 2024+ |
| `*_total_y0` | Total allocated amount (base year) | numeric | 2024+ |
| `*_total_y1` | Total allocated amount (base year + 1) | numeric | 2024+ |
| `*_total_y2` | Total allocated amount (base year + 2) | numeric | 2024+ |
| `plan_years` | Calendar years array (e.g., [2024, 2025, 2026]) (JSON only) | array | 2024+ |

**Wildcard (`*`) represents:** `state_body`, `program` (CSV); `overall` (JSON)

## 8. Data Quality and Validation

Comprehensive validation checks are performed on all processed data. See [validation.md](validation.md) for complete validation rules and how to run validation reports.

---

*This document will be updated as new components are added to the processing pipeline.*
