# Armenian State Budget Tools

[![Donate](https://img.shields.io/badge/💝_Donate-Support_Gituzh-ff69b4)](https://gituzh.am/donate?utm_id=gh-abt)
[![Sponsors](https://img.shields.io/badge/🌟_Our-Supporters-orange)](https://gituzh.am/en/supporters/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Clean, validated Armenian budget data** - Budget laws, spending reports, and mid-term expenditure program (MTEP) (2019-2025)

> ⚠️ **Project Status:** Active development - APIs and data schemas may change

Parses official Armenian government budget documents into analysis-ready CSVs with full validation and lineage tracking.

---

## Quick Start

### 💾 Just Want the Data?

Pre-processed CSVs ready to use:

- **Budget Laws** (2019-2025): `data/processed/csv/{year}_BUDGET_LAW.csv`
- **Spending Reports** (2019-2024): `data/processed/csv/{year}_SPENDING_Q{1,12,123,1234}.csv`
- **MTEP** (2024+): `data/processed/csv/{year}_MTEP.csv`

→ See [data_schemas.md](docs/data_schemas.md) for column details

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

### 🤖 AI-Assisted Analysis (MCP Server)

> 🚧 **Status:** In active development

**Easiest setup (Claude Desktop):**

#### 1. Download or clone this repo

- **Download**: [Latest release](https://github.com/gituzh/armenian-budget-tools/releases/latest) or [current branch archive](https://github.com/gituzh/armenian-budget-tools/archive/refs/heads/main.zip) → extract the ZIP
- **Clone**: `git clone https://github.com/gituzh/armenian-budget-tools.git`

#### 2. Install

```bash
cd armenian-budget-tools
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -U -e .
```

#### 3. Add to your Claude Desktop config

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "armenian-budget": {
      "command": "python",
      "args": ["-m", "armenian_budget.interfaces.mcp.server"],
      "cwd": "/absolute/path/to/armenian-budget-tools",
      "env": {
        "ARMENIAN_BUDGET_DATA_PATH": "/absolute/path/to/armenian-budget-tools/data/processed"
      }
    }
  }
}
```

#### 4. Restart Claude Desktop

→ See [mcp.md](docs/mcp.md) for detailed setup and available tools

### 🛠️ Run the Data Processing Pipeline Yourself

> **Note:** Processed data is already included in this repo. This section shows how to regenerate it from scratch.

#### 1. Download/clone and install (see steps 1-2 in "AI-Assisted Analysis" above)

#### 2. Run the pipeline

```bash
armenian-budget download --years 2019-2024 --extract
armenian-budget discover --years 2019-2024
armenian-budget process --years 2019-2024

# Find outputs in ./data/processed/csv/
```

### 👩‍💻 For Developers & Contributors

**Documentation Philosophy:** We keep docs minimal and purposeful. They serve humans and AI agents who need context to understand, extend, and audit the system. Only document what cannot be understood from code alone.

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
  year = {2025}
}
```

**Plain text:**

```text
The Gituzh Initiative. (2025). Armenian State Budget Tools.
https://github.com/gituzh/armenian-budget-tools
```

When using the parsed data, please acknowledge the source to help others discover this resource and support transparency in government data.

## Requirements

- Python 3.10+
- `unar` or `unrar` for RAR extraction

For installation steps, see [AI-Assisted Analysis](#-ai-assisted-analysis-mcp-server) above.

Need help? See [developer_guide.md](docs/developer_guide.md#common-development-tasks)

## Data Sources

Official government sources:

- **Budget Laws**: [minfin.am/hy/page/petakan_byuj/](https://minfin.am/hy/page/petakan_byuj/)
- **Spending Reports**: [minfin.am/hy/page/hy_hashvetvutyunner/](https://minfin.am/hy/page/hy_hashvetvutyunner/)
- **MTEP (Mid-Term Expenditures Program)**: [minfin.am/hy/page/petakan_mijnazhamket_tsakhseri_tsragre/](https://minfin.am/hy/page/petakan_mijnazhamket_tsakhseri_tsragre/)

→ See [config/sources.yaml](config/sources.yaml) for complete registry with URLs

→ See [data_schemas.md](docs/data_schemas.md) for data formats and column details

## Support This Project

If you find this project valuable, consider supporting Gituzh's work on civic technology and open data:

- **[Donate](https://gituzh.am/donate)** - Support our mission
- **[Our Supporters](https://gituzh.am/en/supporters/)** - See who makes this work possible

Your support helps maintain this project and enables us to build more tools for government transparency and civic engagement.

## License

MIT License - See [LICENSE](LICENSE)
