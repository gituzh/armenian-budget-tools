# Armenian State Budget Tools

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

→ See full validation list in [developer_guide.md](docs/developer_guide.md#validation-vs-tests)

### 🤖 AI-Assisted Analysis (MCP Server)

> 🚧 **Status:** In active development

**Easiest setup (Claude Desktop):**

1. Download or clone this repo:
   - **Download**: [Latest release](https://github.com/gituzh/armenian-budget-tools/releases/latest) or [current branch archive](https://github.com/gituzh/armenian-budget-tools/archive/refs/heads/main.zip) → extract the ZIP
   - **Clone**: `git clone https://github.com/gituzh/armenian-budget-tools.git`
   - Then install and process data (see "Run the Pipeline Yourself" below)
2. Add to your Claude Desktop config:
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

3. Restart Claude Desktop

→ See [mcp.md](docs/mcp.md) for detailed setup and available tools

### 🛠️ Run the Pipeline Yourself

```bash
# Install
python -m venv venv && source venv/bin/activate
pip install -U -e .

# Download, extract, process
armenian-budget download --years 2019-2024 --extract
armenian-budget process --years 2019-2024

# Find outputs in ./data/processed/csv/
```

### 👩‍💻 For Developers & Contributors

- **Implementation details** → [developer_guide.md](docs/developer_guide.md)
- **System design** → [architecture.md](docs/architecture.md)
- **Data formats** → [data_schemas.md](docs/data_schemas.md)

---

## Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| [README.md](README.md) | Quick start guide | All users |
| [docs/data_schemas.md](docs/data_schemas.md) | Data formats & columns | Data analysts |
| [docs/developer_guide.md](docs/developer_guide.md) | Implementation & API | Developers |
| [docs/mcp.md](docs/mcp.md) | MCP server integration | AI developers |
| [docs/architecture.md](docs/architecture.md) | System design | Architects |

## Installation

```bash
# Clone and install
git clone https://github.com/gituzh/armenian-budget-tools.git
cd armenian-budget-tools
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -U -e .

# Verify
armenian-budget --help
```

**Requirements:**

- Python 3.10+
- `unar` or `unrar` for RAR extraction

Need help? See [developer_guide.md](docs/developer_guide.md#common-development-tasks)

## Data Sources

Official government sources:

- **Budget Laws**: https://minfin.am/hy/page/petakan_byuj/
- **Spending Reports**: https://minfin.am/hy/page/hy_hashvetvutyunner/
- **MTEP (Mid-Term Expenditures Program)**: https://minfin.am/hy/page/petakan_mijnazhamket_tsakhseri_tsragre/

→ See [config/sources.yaml](config/sources.yaml) for complete registry with URLs

## License

MIT License - See [LICENSE](LICENSE)
