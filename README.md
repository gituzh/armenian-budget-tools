# Armenian State Budget Tools

[![Donate](https://img.shields.io/badge/💝_Donate-Support_Gituzh-ff69b4)](https://gituzh.am/donate?utm_id=gh-abt)
[![Sponsors](https://img.shields.io/badge/🌟_Our-Supporters-orange)](https://gituzh.am/en/supporters/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Clean, validated Armenian budget data** - Budget laws, spending reports, and mid-term expenditure program (MTEP)

> ⚠️ **Project Status:** Active development - APIs and data schemas may change
>
> ⚠️ **Known Data Issues:** The source data contains structural anomalies (split state bodies, formatting inconsistencies). See [validation_known_issues.md](docs/validation_known_issues.md) for details and current validation exceptions.

Parses official Armenian government budget documents into analysis-ready CSVs with full validation and lineage tracking.

**Data Coverage:**
- **Budget Laws**: 2019-2026
- **Spending Reports**: 2019-2025 (Q1, Q12, Q123, Q1234) plus 2026 Q1
- **MTEP**: 2024
- **GDP snapshots**: budget-law sources and annual spending reports where source
  documents expose GDP/macro tables

---

## Quick Start

### 💾 Just Want the Data?

Pre-processed CSVs ready to use:

- **Budget Laws** (2019-2026): `data/processed/{year}_BUDGET_LAW.csv`
- **Spending Reports**: `data/processed/{year}_SPENDING_Q{1,12,123,1234}.csv`
  for 2019-2025, plus `data/processed/2026_SPENDING_Q1.csv`
- **MTEP** (2024): `data/processed/2024_MTEP.csv`
- **GDP snapshots**: `data/processed/{year}_{BUDGET_LAW|SPENDING_Q1234}_GDP.json`
- **GDP report**: `data/reports/gdp_report.html`

→ See [data_schemas.md](docs/data_schemas.md) for column details

### AI-Assisted Data Work

The recommended AI-facing data contract is the
[`armenian-budget-data`](skills/armenian-budget-data/SKILL.md) skill.

- Works directly against `data/processed`
- Defines valid source types, grains, metrics, GDP denominators, and provenance
- Uses bundled helper scripts internally when needed

Example workflow:

```bash
git clone https://github.com/gituzh/armenian-budget-tools.git
cd armenian-budget-tools
```

Launch Codex in the repo root and prompt it with:

```text
Use $armenian-budget-data to inspect available parsed budget and GDP files, choose valid source types, grains, metrics, denominators, and include exact source file references plus provenance metadata.
```

### ✅ How We Ensure Data Quality

This project:

1. **Downloads** official data from minfin.am (checksummed)
2. **Parses** Excel files with Armenian text handling
3. **Validates** hierarchical totals, execution rates, and structural integrity
4. **Outputs** clean CSVs with full lineage tracking

**Validation checks:**

- **Financial**: Hierarchical totals, execution rates (0-200%), period ≤ annual
- **Structural**: Required columns, data types, encoding
- **Cross-temporal**: Program consistency across years

→ See full validation list in [validation.md](docs/validation.md)
→ Source-data anomalies and current validation exceptions: [validation_known_issues.md](docs/validation_known_issues.md)

### 🛠️ Run the Data Processing Pipeline Yourself

> **Note:** Processed data is already included in this repo. This section shows how to regenerate it from scratch.

#### 1. Install

```bash
git clone https://github.com/gituzh/armenian-budget-tools.git
cd armenian-budget-tools
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -U -e .
```

For development and tests, install the optional dev dependencies instead:

```bash
pip install -U -e ".[dev]"
```

#### 2. Run the pipeline

```bash
armenian-budget download --years 2019-2026 --extract
armenian-budget process --years 2019-2026
armenian-budget validate --years 2019-2026  # Optional: validate processed data

# Find parsed outputs in ./data/processed/ and HTML reports in ./data/reports/

# Optional: if archives were downloaded without --extract, extract them later
armenian-budget extract --years 2019-2026

# Optional: pre-cache discovered source workbooks before processing
armenian-budget discover --years 2019-2026

# Optional: re-check official archives for silent upstream changes
armenian-budget download --years 2024-2025 --force

# Optional: inspect current MinFin budget-law and spending-report downloads
armenian-budget minfin-budget --years 2025-2026 --downloads-only
armenian-budget minfin-spending-reports --years 2026 --quarter Q1 --downloads-only

# Optional: process specific source type only
armenian-budget process --years 2023 --source-type BUDGET_LAW

# Optional: extract GDP snapshots from GDP-supported sources and render the GDP review report
armenian-budget gdp-extract --years 2021-2026 --source-type BUDGET_LAW
armenian-budget gdp-extract --years 2022-2025 --source-type SPENDING_Q1234
armenian-budget gdp-report
```

### 👩‍💻 For Developers & Contributors

**Documentation Philosophy:** We keep docs minimal and purposeful. They serve humans and AI agents who need context to understand, extend, and audit the system. Only document what cannot be understood from code alone.

Build release artifacts, including the data archive and ChatGPT skill archive:

```bash
python scripts/build_artifacts.py --target all
```

For the full release checklist, see
[developer_guide.md#release-preparation](docs/developer_guide.md#release-preparation).

Run the test and lint checks used during development:

```bash
.venv/bin/pytest -q
.venv/bin/ruff check src/ tests/
```

- **User expectations** → [prd.md](docs/prd.md)
- **System design** → [architecture.md](docs/architecture.md)
- **Implementation details** → [developer_guide.md](docs/developer_guide.md)
- **Data formats** → [data_schemas.md](docs/data_schemas.md)

## Citation & Attribution

If you use this data or code in your research, publications, or projects, please cite:

**BibTeX:**

```bibtex
@software{armenian_budget_tools,
  title = {Armenian State Budget Tools},
  author = {The Gituzh Initiative},
  url = {https://github.com/gituzh/armenian-budget-tools},
  year = {2026}
}
```

**Plain text:**

```text
The Gituzh Initiative. (2026). Armenian State Budget Tools.
https://github.com/gituzh/armenian-budget-tools
```

When using the parsed data, please acknowledge the source to help others discover this resource and support transparency in government data.

## Requirements

- Python 3.10+
- `unar` or `unrar` for RAR extraction

For installation steps, see [Run the Data Processing Pipeline Yourself](#️-run-the-data-processing-pipeline-yourself) above.

Need help? See [developer_guide.md](docs/developer_guide.md#common-development-tasks)

## Data Sources

Official government sources:

- **Budget Laws**: [minfin.am/hy/page/petakan_byuj/](https://minfin.am/hy/page/petakan_byuj/)
- **Spending Reports**: [minfin.am/hy/page/hy_hashvetvutyunner/](https://minfin.am/hy/page/hy_hashvetvutyunner/)
- **MTEP (Mid-Term Expenditures Program)**: [minfin.am/hy/page/petakan_mijnazhamket_tsakhseri_tsragre/](https://minfin.am/hy/page/petakan_mijnazhamket_tsakhseri_tsragre/)

→ See [config/sources.yaml](config/sources.yaml) for complete registry with URLs

Downloaded archive hashes are recorded in [config/checksums.yaml](config/checksums.yaml).
When `download --force` detects changed content at an existing URL, the prior archive
is kept under `.revisions/` and the change is logged in
[config/checksum_history.yaml](config/checksum_history.yaml).

→ See [data_schemas.md](docs/data_schemas.md) for data formats and column details

## Support This Project

If you find this project valuable, consider supporting Gituzh's work on civic technology and open data:

- **[Donate](https://gituzh.am/donate)** - Support our mission
- **[Our Supporters](https://gituzh.am/en/supporters/)** - See who makes this work possible

Your support helps maintain this project and enables us to build more tools for government transparency and civic engagement.

## License

MIT License - See [LICENSE](LICENSE)
