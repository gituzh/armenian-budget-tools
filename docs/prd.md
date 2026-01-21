# Product Requirements Document (PRD) — Armenian Budget Tools

> **When to read this:** Product managers, contributors, and AI assistants who need to understand WHO uses the system, WHAT they expect from it, and WHY key design decisions were made. For implementation details, see `architecture.md` and `developer_guide.md`.

## Users and Use Cases

**Data analysts / researchers:**

- Batch process multiple years via CLI
- Validate data integrity with configurable tolerances
- Export clean CSVs for analysis in Excel, R, Python, BI tools

**Journalists / civic tech:**

- Inspect specific ministries/programs across years
- Validate budget claims with official data
- Track spending execution rates

**Developers:**

- Extend parsers for new data formats
- Contribute validation rules
- Improve error handling and discovery logic

**AI agents (via MCP server):**

- List available datasets by year/source
- Filter budget data by ministry, program, or criteria
- Generate spending summaries and comparisons

## Success Criteria

**Data quality:**

- Hierarchical totals validated within tolerance (5 AMD for spending, 0 for budget laws)
- No structural errors (missing columns, encoding issues)
- Cross-validation between budget laws and spending reports

**Usability:**

- Single command to download, extract, and process a year
- Clear progress reporting and error messages
- CSV outputs ready for analysis without additional cleanup

**Integration:**

- MCP server provides AI agents access to processed data
- CLI integrates into automated workflows
- Outputs compatible with standard analysis tools

## Key Decisions

**Why CSV over database?**

- Universal compatibility with Excel, R, Python, BI tools
- Simple data exchange without server infrastructure
- Easy inspection and version control

**Why preserve original columns?**

- Maximum flexibility for diverse analysis needs
- Transparency (users can verify against source files)
- Future-proof (new analyses don't require reprocessing)

**Why YAML configuration?**

- Adapt to format changes without code modifications
- Year-specific overrides for edge cases
- Clear separation of data patterns from parsing logic

**Why typed exceptions over exit codes?**

- Library-friendly (no forced process exits)
- Composable (callers handle errors appropriately)
- Testable (exception handling in unit tests)

**Why pandas over raw Python?**

- Vectorized operations for performance
- Rich ecosystem for data manipulation
- Industry standard for data processing
