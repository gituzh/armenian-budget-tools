# Data Schema and Formats

## 1. Data Pipeline Overview

The Armenian Budget Tools processes official government budget data through a multi-stage pipeline. For the complete data flow diagram, see [architecture.md](architecture.md#4-data-flow).

**Key Characteristics:**

- **Original sources**: Archives downloaded from minfin.am containing multiple Excel files
- **Extraction**: Unarchiving reveals inconsistent folder structures across years
- **Processing**: Parses budget program breakdowns and selected macro/GDP tables
- **Output**: Normalized CSVs plus selected JSON/HTML macro indicator outputs

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
│           └── .revisions/   # Prior copies when --force detects changed content
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
    ├── {year}_{SOURCE_TYPE}[_{LABEL}].csv
    ├── {year}_{SOURCE_TYPE}[_{LABEL}]_GDP.json
    └── processing_report.json
└── reports/            # Rendered HTML reports
    └── gdp_report.html
```

**Naming Conventions:**

- **Archives**: Original filenames from minfin.am (e.g., `Orenqi havelvacner_Excel.rar`, hash-based names)
- **Extracted Folders**: Varies by archive structure (may preserve archive name or use internal folder names)
- **Processed CSVs**: `{year}_{SOURCE_TYPE}.csv` (e.g., `2023_BUDGET_LAW.csv`)
- **GDP snapshots**: `{year}_{SOURCE_TYPE}_GDP.json` for `BUDGET_LAW` and `SPENDING_Q1234`
- **Labelled versions**: `_{LABEL}` after the source type in every output name, and a
  `{year}_{LABEL}` year folder under `original/` and `extracted/` (see
  [3.4 Source Labels](#34-source-labels))
- **Source Types**: `BUDGET_LAW`, `SPENDING_Q1`, `SPENDING_Q12`, `SPENDING_Q123`, `SPENDING_Q1234`, `MTEP`

## 3. Original Data Archives

### 3.1 Archive Sources and Web Pages

**Budget Law Archives:**

- **Source Page**: [State Budget Law](https://minfin.am/hy/page/petakan_byuj/) - "Պետական բյուջե"
- **Years Available**: 2019-2026
- **Format**: RAR/ZIP archives containing multiple Excel files
- **Input workbooks**: `.xlsx`, `.xls`, and Excel 2003 XML ("SpreadsheetML") saved with an `.xls` name; the XML kind is read with the standard library
- **Current Scope**: Only parsing program summary (Ամփոփ ըստ ծրագրերի)

**Note:** 2017-2018 budget laws are PDF-only format and are not currently supported. Before 2019, the Armenian budget was not programmatic (program-based), so the data structure differs significantly from later years.

**Spending Report Archives:**

- **Source Page**: [Budget Execution Reports](https://minfin.am/hy/page/hy_hashvetvutyunner/) - "Պետական բյուջեեի կատարման մասին հաշվետվություններ"
- **Years Available**: 2019-2025 for all supported quarters; 2026 Q1, Q12 and Q123
- **Quarters**: Q1, Q12, Q123, Q1234 where published and packaged
- **Format**: RAR/ZIP archives with nested folder structures

**MTEP Archives:**

- **Source Page**: [Mid-Term Expenditure Program](https://minfin.am/hy/page/petakan_mijnazhamket_tsakhseri_tsragre/) - "Պետական միջնաժամկետ ծախսերի ծրագրե"
- **Years Available**: 2024+
- **Format**: RAR/ZIP archives
- **Purpose**: Multi-year budget projections (3-year horizon)

### 3.2 Data Source Registry

Official download URLs and metadata for all government archives are maintained in `config/sources.yaml`:

- **Purpose**: Centralized registry of all official data sources with direct download links
- **Content**: Year, source type, URL or multi-file `files` entries, file format,
  optional local filename, and human-readable descriptions
- **Source**: Direct URLs from minfin.am government website pages
- **Usage**: Powers the download system and ensures data provenance

Registry entries may either point to a single archive with top-level `url` and `file_format`
fields, or group related downloads under `files`. Multi-file entries are used when one
logical source needs both program attachments and supporting documents, such as budget-law
Excel attachments plus explanatory notes for GDP extraction. A `filename` field may be set
when the local archive name should be explicit instead of inferred from the URL.

### 3.3 Archive Contents and Future Components

Archives contain multiple budget components beyond the currently parsed program summaries:

**Budget Law Archives:**
- **Currently Parsed**: Program summary (Ամփոփ ըստ ծրագրերի) → `BUDGET_LAW`
- **Available for Future**: Capital expenditures, loan programs, grants, subsidies, deficit financing, administrative costs, environmental fees, and other budget components

**Spending Report Archives:**
- **Currently Parsed**: Program summary (ամփոփ ըստ ծրագրերի)
- **Available for Future**: Detailed breakdowns by responsible entity and activity, loan programs, grants, deficit financing

### 3.4 Source Labels

A document can exist in several public versions, for example a budget law as a
government draft, a public-consultation copy, the draft submitted to parliament
and the adopted law. An entry in `config/sources.yaml` may carry a `label`;
entries with the same year and source type but different labels are separate
versions, each processed by the normal pipeline.

```yaml
- name: "2026_budget_law_edraft"
  year: 2026
  source_type: "budget_law"
  label: "EDRAFT"         # optional; ^[A-Z0-9]+$, "GDP" is reserved
  published: 2025-10-01   # optional ISO date
  files: [...]
```

- **No label**: behaves as before. For a budget law the unlabelled entry is the
  adopted law.
- **`published`**: the best evidence of the date the file first appeared on
  that site. It is shown only in the identical-data note below and never
  affects file names, parsing or which version counts as final. For MinFin
  entries it is the archive's `Last-Modified` date where that is plausible;
  entries re-uploaded later have none.
- **Names**: `{year}_{SOURCE_TYPE}[_{LABEL}]` for the CSV, `_overall.json`,
  `_validation.md`, `_validation.json` and `_GDP.json`, e.g.
  `2026_BUDGET_LAW_EDRAFT.csv`.
- **Folders**: `budget_laws/2026_EDRAFT/` beside `budget_laws/2026/` under
  `data/original/` and `data/extracted/`. Discovery for one version only
  searches its own folder; its index key is `{year}/{source_type}/{LABEL}`.
- **Commands**: `download`, `extract`, `discover`, `process`, `validate` and
  `gdp-extract` cover the unlabelled version and every labelled one;
  `--label LABEL` selects one version and `--unlabelled` only the unlabelled
  one.
- **Registered versions only**: labelled versions come from `sources.yaml`
  (`--config`) and nowhere else. A `{year}_{LABEL}` folder on disk with no
  entry for that year is ignored, with one warning per run (`Ignoring <path>:
  <LABEL> is not registered for <year> in sources.yaml`). Nothing is written
  for it and nothing is deleted. A registered version with nothing on disk is
  reported as `FAIL` or `MISSING`. A year that has only labelled versions
  (an unlabelled entry is not registered and nothing of it is on disk) skips
  its unlabelled version in `process`, `validate`, `discover` and
  `gdp-extract` with one `INFO` line; `--unlabelled` still reports it as
  missing. `--label X` for a label not registered for
  the year is reported as missing, and the command exits non-zero when nothing
  was done. If `sources.yaml` is missing or invalid, unlabelled work continues,
  labelled versions are not run and one warning says so; with `--label` it is
  an error.
- **Labels are opaque**: they are not ordered and need no code change. A
  version is registered only if the existing downloader fetches it and the
  existing parser reads it.

Label convention: a label names the site a version came from, plus a number for
later revisions on that site.

| Label | Site | Meaning for a budget law |
|---|---|---|
| `DRAFT`, `DRAFT2`, … | e-gov.am | Draft on a government session agenda; `DRAFT2` is the revised draft |
| `EDRAFT`, … | e-draft.am | Public-consultation copy (2020-2026) |
| `PARLIAMENT` | parliament.am | Draft as submitted to parliament (not the adopted law) |
| `PARLIAMENT2`, … | parliament.am | Revised draft published for the second reading; in 2020-2026 it holds the same data as the adopted law. A further revision would be `PARLIAMENT3` |
| *(none)* | minfin.am | Adopted law |

**Draft coverage by year.** State of the search on 22 Nov 2026. "Not found"
means a bounded search missed it; it does not show that the version was never
published. "File lost" means the session agenda still lists the file and the
link answers "Problem with file download: Invalid file identifier" while other
files of the same session download.

| Budget year | `DRAFT` (e-gov.am) | `EDRAFT` (e-draft.am) | `PARLIAMENT` | `DRAFT2` (e-gov.am) | `PARLIAMENT2` |
|---|---|---|---|---|---|
| 2019 | not published as a spreadsheet (session of 27 Sep 2018: programme table only as PDF) | not published as a spreadsheet (project 1230 links a minfin.am archive of 15 PDFs) | not published as a spreadsheet (draft K-383: annexes archive holds only PDFs) | not published as a spreadsheet archive (session of 19 Nov 2018: one sheet of changes, no annexes archive) | not published as a spreadsheet (K-383 revised: only PDFs) |
| 2020 | not published as a spreadsheet (session of 30 Sep 2019: programme tables N1 and N2 are PDF) | exists (project 1980, 4 Oct 2019) | not published as a spreadsheet (programme table is PDF only) | not published as a spreadsheet (session of 28 Nov 2019: programme tables are PDF) | exists |
| 2021 | not found: searched the e-gov.am session archive for 10 Sep-31 Dec 2020 on 22 Nov 2026; it lists no session between 24 Sep and 12 Nov 2020 | exists (project 2786, 2 Oct 2020) | exists | not found: searched the e-gov.am session archive for 10 Sep-31 Dec 2020 on 22 Nov 2026; no agenda item about the revised draft | exists |
| 2022 | file lost (session of 30 Sep 2021, file id 1576078) | exists (project 3614, 5 Oct 2021) | exists | not found: searched every e-gov.am session agenda of 4 Nov-30 Dec 2021 on 22 Nov 2026 | exists |
| 2023 | file lost (session of 29 Sep 2022, file id 2175808) | exists (project 4797, 5 Oct 2022) | exists | file lost (session of 1 Dec 2022, file id 2285509) | exists |
| 2024 | file lost (session of 28 Sep 2023, file id 2806894) | exists (project 6318, 4 Oct 2023) | exists | file lost (session of 30 Nov 2023, file id 2920939) | exists |
| 2025 | file lost (session of 26 Sep 2024, file id 3431295) | exists (project 7738, 2 Oct 2024) | exists | file lost (session of 28 Nov 2024, file id 3542251) | exists |
| 2026 | file lost (session of 25 Sep 2025, file id 4035951) | exists (project 9166, 1 Oct 2025) | exists | exists (session of 27 Nov 2025) | exists |
| 2027 | exists (session of 1 Oct 2026) | not published as a spreadsheet (project 10708, 2 Oct 2026, has only the law text) | not found: searched parliament.am's draft lists on 22 Nov 2026; they hold no draft later than 3 Jul 2026 | not yet published (session agendas read up to 19 Nov 2026) | not found: searched parliament.am's draft lists on 22 Nov 2026; they hold no draft later than 3 Jul 2026 |

"exists" means a dataset is registered in `sources.yaml` and processed.

**Identical data.** When `validate` runs, the CSVs of the same year and source
type are compared by checksum, whatever `--label` selected: the unlabelled CSV
and the CSVs of labels registered in `sources.yaml`. A report whose CSV
is byte-identical to others carries one line listing the whole group, oldest
`published` first and undated versions last:
`**Identical data:** EDRAFT (2025-10-01), PARLIAMENT (2025-10-01)` in Markdown
and a top-level `identical_data` list in JSON (absent when nothing matches).
The note is information, not a check.
The 2021-2024 `EDRAFT` CSVs are identical to the `PARLIAMENT` CSV of the
same year; 2020 `EDRAFT` is identical to no other version (its total
1,880,186,389.82 differs from 1,855,697,119.479 in the adopted law).

**GDP.** A labelled budget-law version gets `{year}_BUDGET_LAW_{LABEL}_GDP.json`
from the budget message (`explanatory_note` file, DOCX) registered in its own
entry; the snapshot records its `label`. A version without one gets no GDP
file. `gdp_report.html` shows unlabelled snapshots only. `EDRAFT` has a
snapshot for 2021-2026 but not for 2020.

**Known limitations.**

- PDF sources are not read.
- 2019: every source publishes the programme tables only as PDF (`DRAFT2`: one
  sheet of changes, no annexes archive), so there is no 2019 draft dataset.
  2020: the `PARLIAMENT`, `DRAFT` and `DRAFT2` programme tables are PDF only
  (`EDRAFT` and `PARLIAMENT2` exist).
- Lost e-gov.am files: `DRAFT` 2022-2026 and `DRAFT2` 2023-2025 are listed on
  the session agendas but cannot be downloaded (table above has the session
  and file id).
- Not found by a bounded search (22 Nov 2026): 2021 `DRAFT` and `DRAFT2`
  (e-gov.am session archive), 2022 `DRAFT2` (e-gov.am session agendas),
  2027 `PARLIAMENT` and `PARLIAMENT2` (parliament.am draft lists). 2027
  `EDRAFT` has no spreadsheet and 2027 `DRAFT2` is not yet published.
- `PARLIAMENT` and `PARLIAMENT2` versions have no `_GDP.json`: parliament.am
  publishes the budget message only as PDF.
- 2020 `EDRAFT` has no `_GDP.json`: the extractor does not find the GDP table
  in the 2020 budget message (the adopted 2020 law has none either).
- Dataset-driven tests cover unlabelled datasets only; labelled datasets are
  covered by their validation reports.

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

- **Tools Required**: 7-Zip with RAR support or `unrar` for RAR files (`unar` as a last resort; it fails on some RAR5 archives); Python's `zipfile` module for ZIP
- **Inconsistent Structures**: Each archive has unique folder organization
- **File Discovery**: Pattern-based matching to identify relevant Excel files
- **Intermediate Format**: Preserves original .xlsx/.xls files before processing
- **Integrity Verification**: SHA-256 checksums recorded in `config/checksums.yaml` after downloads
- **Change Tracking**: `download --force` re-fetches existing archives, preserves changed prior copies under `.revisions/`, and records checksum changes in `config/checksum_history.yaml`
- **Download Optimization**: Existing archives are skipped unless `--force` is used

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
- **Naming**: `{year}_{SOURCE_TYPE}[_{LABEL}].csv`
- **Format**: UTF-8 encoded CSV with Armenian text support

**GDP JSON Snapshots:**

- **Location**: `data/processed/`
- **Naming**: `{year}_{BUDGET_LAW|SPENDING_Q1234}_GDP.json`; `{year}_BUDGET_LAW_{LABEL}_GDP.json` for a labelled budget-law version
- **Scope**: GDP and related macro indicators extracted from budget-law explanatory notes and annual spending reports

**GDP HTML Report:**

- **Location**: `data/reports/gdp_report.html`
- **Scope**: Review table built from available GDP JSON snapshots

**Metadata:**

- **Processing Report**: `data/processed/processing_report.json`
- **Checksums**: Current SHA-256 hashes in `config/checksums.yaml`; same-URL content changes in `config/checksum_history.yaml`
- **Discovery Index**: `data/extracted/discovery_index.json`

### 6.2 Data Structure

**CSV Structure:** Flattened rows with hierarchical totals (no joins needed for analysis).

- **3-level sources (BUDGET_LAW, SPENDING):** Each row = one subprogram with parent totals
- **2-level source (MTEP):** Each row = one program (subprogram columns empty for compatibility)

**Overall JSON:** Each processed file produces a companion `*_overall.json` with grand totals for validation. Budget Law contains a single total; Spending contains multiple aggregates (annual_plan, rev_annual_plan, actual, execution rates); MTEP contains multi-year totals and plan_years array.

**GDP JSON:** Each snapshot contains `year`, `source_type`, `metric_set`, `source_file`, and one or more `tables`. Table records use `target_year`, `status`, `indicator`, `unit`, and `value`.

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
