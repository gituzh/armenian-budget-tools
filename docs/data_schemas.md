# Data Schema and Formats

## 1. Data Pipeline Overview

The Armenian Budget Tools processes official government budget data through a multi-stage pipeline:

```text
Original Archives (.rar/.zip)
        ↓
   Download & Extract
        ↓
Intermediate Files (.xlsx/.xls)
        ↓
      Parse & Normalize
        ↓
   Processed CSVs + Metadata
```

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
- **Source Types**: `BUDGET_LAW`, `SPENDING_Q1`, `SPENDING_Q12`, `SPENDING_Q123`, `SPENDING_Q1234`

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

### 3.2 Data Source Registry

Official download URLs and metadata for all government archives are maintained in `config/sources.yaml`:

- **Purpose**: Centralized registry of all official data sources with direct download links
- **Content**: Year, source type, URL, file format, and human-readable descriptions
- **Source**: Direct URLs from minfin.am government website pages
- **Usage**: Powers the download system and ensures data provenance

### 3.3 Archive Contents and Future Components

Budget law archives contain extensive budget documentation beyond just the program breakdown. The current `BUDGET_LAW` source type only processes the program summary, but many other components are available for future parsing.

**Budget Law Archive Structure (Example 2023):**

```text
ORENQI HAVELVACNER/
├── 1.Հավելված N1 աղյուսակ N1.Ամփոփ ըստ ծրագրերի.xls
│   └── 💡 Currently parsed as BUDGET_LAW
├── 2.Հավելված N1 աղյուսակ N2. Ըստ ծրագրերի և միջոցառումների.xls
├── 3.Հավելված N1 աղյուսակ N3. կապիտալ ծախսեր.xlsx
├── 4.Հավելված N1 աղյուսակ N4 վարկային ծրագրեր.xlsx
├── 5.Հավելված N1 աղյուսակ N5 դրամաշնորհային ծրագրեր.xlsx
├── 6.Հավելված N1 աղյուսակ N6. ճանապարհների ընթացիկ պահպանություն.xlsx
├── 7.Հավելված N1 աղյուսակ N7 սուբվենցիաներ համայնքներին.xlsx
├── 8.Հավելված N1 աղյուսակ N8 սահմանամերձ.xlsx
├── 9.Հավելված N2. Դոտացիա.xlsx
├── 10.Հավելված N3.Դեֆիցիտի ֆինանսավորման աղբյուրներ.xlsx
├── 11.Հավելված N4.ԿԲ վարչական ծախսեր.xlsx
├── 12.Հավելված N5, Ռադիոհաճախականություն.docx
├── 13.Հավելված N 6Աջնահերթություն.xlsx
└── 14.Հավելված N 7 բնապահպանական վճարներ.xlsx
```

**Spending Report Archive Structure (Example 2023 Q123):**

```text
4.Հավելվածներ/
├── 1. 2023_9 ամիս_ամփոփ ըստ ծրագրերի.xls
├── 2. 2023_9 ամիս_ պատասխանատու,ծրագիր,միջոցառում.xls
├── 3. 2023_9 ամիս_վարկ.xls
├── 4. 2023_9 ամիս_դրամաշնորհ.xls
└── 5. 2023_9-ամիս_դեֆիցիտ.xls
```

## 4. Original Table Organization

### 4.1 BUDGET_LAW Tables (Currently Parsed)

**Discovery Pattern:** Files are discovered using regex patterns from `config/parsers.yaml` that match the Armenian word fragments "ծրագ" (from ծրագիր/program) and "միջոց" (from միջոցառում/measure)
**Purpose:** Annual budget allocations broken down by programs and subprograms
**Structure:** 3-level organizational hierarchy with Armenian language headers

**Table Structure:**

- **State Body** (Պետական մարմին): State body, ministry or agency name
- **Program** (Ծրագիր): Budget program with code and description
- **Subprogram** (Միջոցառում): Detailed subprogram with code and description
- **Allocated Amount** (Հատկացված գումար): Budget amount in AMD

**Key Characteristics:**

- **Hierarchy**: 3-level structure (State Body → Program → Subprogram) with hierarchical totals
- Consistent structure across 2019-2024
- 2025 format includes extended program codes (`program_code_ext`)

*[Screenshot needed: Hierarchical budget table showing state body/program/subprogram structure]*

### 4.2 SPENDING Tables (Execution Reports)

**Discovery Pattern:** Files are discovered using the same regex patterns from `config/parsers.yaml` as budget law files (matching "ծրագ" and "միջոց" word fragments)

**Key File Types:**

- **Main Summaries**: `1. {year}_{period}_ամփոփ ըստ ծրագրերի.xls` - Program-by-program spending overview
- **Detailed Breakdowns**: `2. {year}_{period}_պատասխանատու,ծրագիր,միջոցառում.xls` - By responsible entity and activity
- **Specialized Reports**: Loan programs (`վարկ.xls`), grants (`դրամաշնորհ.xls`), deficit financing (`դեֆիցիտ.xls`)

**Table Structure:**

- **State Body** (Պետական մարմին): State body, ministry or agency name
- **Program** (Ծրագիր): Budget program with code and description
- **Subprogram** (Միջոցառում): Detailed subprogram with code and description
- **Original Plan** (Սկզբնական պլան): Initial annual budget allocation
- **Revised Plan** (Վերանայված պլան): Mid-year budget adjustments
- **Actual Spending** (Իրական կատարում): Year-to-date actual expenditures
- **Execution Rate** (Կատարման տոկոս): Actual vs Revised Plan (%)

**Key Characteristics:**

- **Hierarchy**: Same 3-level structure (State Body → Program → Subprogram) as budget laws
- Multiple plan/actual columns for year-to-date and period-specific metrics
- Q1234 reports lack period-specific columns (only annual metrics)
- Complex cross-referencing between original/revised/actual amounts

*[Screenshot needed: Spending report table showing plan vs actual columns]*

### 4.3 Data Organization Notes

- **Language**: All tables use Armenian headers and content
- **Year Variations**: 2017-2018 are PDF-only; 2019+ are Excel-based
- **Multiple Worksheets**: Some files contain multiple tabs for different categories
- **Data Quality**: Some cells may be merged or contain notes/comments
- **Currency**: All amounts in Armenian Dram (AMD)

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

- **Location**: `data/processed/csv/`
- **Naming**: `{year}_{SOURCE_TYPE}.csv`
- **Format**: UTF-8 encoded CSV with Armenian text support

**Metadata:**

- **Processing Report**: `data/processed/processing_report.json`
- **Checksums**: SHA-256 hashes recorded in `config/checksums.yaml` for download integrity verification
- **Discovery Index**: `data/extracted/discovery_index.json`

### 6.2 Data Structure

Each row represents one **subprogram** with aggregated totals from parent levels:

```text
state_body | program_code | program_name | subprogram_code | subprogram_total | program_total | state_body_total
```

**Benefits of Flattened Structure:**

- No complex joins needed for hierarchical analysis
- Consistent schema across all source types and years
- Easy filtering by any level (state body, program, or subprogram)
- Compatible with Excel, BI tools, and data analysis software

**Parser Output per File:**

Each parsed Excel file produces two outputs:

1. **CSV file** with the flattened data structure described above
2. **Overall totals** (`overall_values`) for validation and cross-checking

#### Budget Law Overall Totals

For BUDGET_LAW files, `overall_values` is a float representing the total budget amount across all state bodies, programs, and subprograms.

**Example Value:** `1234567890.0` (AMD)

**Purpose:** Sum of all `subprogram_total` values in the dataset for validation and cross-checking.

#### Spending Report Overall Totals

For SPENDING files, `overall_values` is a dictionary containing multiple aggregated totals:

**Example Structure:**

```json
{
    "total_annual_plan": 1234567890.0,      // Sum of all annual_plan values
    "total_rev_annual_plan": 1234567890.0,  // Sum of all rev_annual_plan values
    "total_actual": 1234567890.0,           // Sum of all actual spending values
    "total_actual_vs_rev_annual_plan": 0.95 // Overall execution rate (95%)
}
```

**Purpose:** Aggregated totals for cross-validation against individual row calculations and reporting.

**Note:** Overall totals are **not included in the CSV output** but are available in the processing pipeline for validation, reporting, and debugging purposes.

## 7. Complete Column Reference

### Common Columns (All Source Types)

| Column | Description | Type | Required |
|--------|-------------|------|----------|
| `state_body` | State body/ministry/agency name | string | ✓ |
| `program_code` | Program identifier | string | ✓ |
| `program_name` | Program name | string | ✓ |
| `program_goal` | Program goal description | string | ✓ |
| `program_result_desc` | Program result description | string | ✓ |
| `subprogram_code` | Subprogram identifier | string | ✓ |
| `subprogram_name` | Subprogram name | string | ✓ |
| `subprogram_desc` | Subprogram description | string | ✓ |
| `subprogram_type` | Subprogram type/category | string | ✓ |

### BUDGET_LAW Columns (2019-2024)

| Column | Description | Type |
|--------|-------------|------|
| `state_body_total` | Total allocated for state body | numeric |
| `program_total` | Total allocated for program | numeric |
| `subprogram_total` | Allocated amount for subprogram | numeric |

### BUDGET_LAW Columns (2025)

| Column | Description | Type |
|--------|-------------|------|
| `state_body_total` | Total allocated for state body | numeric |
| `program_code_ext` | Extended program code (e.g., "12-345") | string |
| `program_total` | Total allocated for program | numeric |
| `subprogram_total` | Allocated amount for subprogram | numeric |

### SPENDING_Q1/Q12/Q123 Columns (2019-2024)

**Annual Metrics (Year-to-Date):**

- `*_annual_plan`: Original annual allocation
- `*_rev_annual_plan`: Revised annual plan
- `*_actual`: Actual spending year-to-date
- `*_actual_vs_rev_annual_plan`: Execution rate vs revised annual plan (%)

**Period-Specific Metrics (Quarter/Half-Year):**

- `*_period_plan`: Original period allocation
- `*_rev_period_plan`: Revised period plan
- `*_actual_vs_rev_period_plan`: Execution rate vs revised period plan (%)

**Wildcard (`*`) represents:** `state_body_`, `program_`, `subprogram_`

### SPENDING_Q1234 Columns (2019-2024)

- `*_annual_plan`: Original annual allocation
- `*_rev_annual_plan`: Final revised annual plan
- `*_actual`: Actual spending for full year
- `*_actual_vs_rev_annual_plan`: Final execution rate vs revised annual plan (%)

### SPENDING_Q1/Q12 Columns (2025)

Same as SPENDING_Q1/Q12/Q123 (2019-2024) but with added:

- `program_code_ext`: Extended program code field

## 8. Data Quality and Validation

### Validation Rules

**Hierarchical Consistency:**

- State body total = sum of program totals
- Program total = sum of subprogram totals
- Cross-year structural validation

**Financial Validation:**

- Execution rates between 0% and 200%
- Period spending ≤ annual spending
- Revised plans ≥ original plans (logical constraint)

**Structural Validation:**

- Required columns present
- Data types consistent
- Armenian text encoding valid

### Known Data Quality Issues

- Some merged cells in original Excel files
- Inconsistent formatting across years
- Occasional manual corrections in spending reports
- PDF-only format for 2017-2018 budget laws

## 9. Future Expansion Opportunities

### Enhanced Processing Features

- **Cross-year Analysis**: Program equivalency mapping and trend analysis
- **Data Quality Scoring**: Automated validation and quality metrics
- **Advanced Discovery**: Pattern recognition for additional file types
- **Metadata Enrichment**: Extended processing reports with more detailed lineage

---

*This document will be updated as new components are added to the processing pipeline.*
