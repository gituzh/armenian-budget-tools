# Analysis

## Default workflow

1. Run `scripts/data_availability.py` to see which datasets exist.
2. Choose the source type that matches the question.
3. State the aggregation grain and metric before aggregating.
4. Compute the result from parsed files only.
5. Add provenance inline for text outputs and as sidecar JSON for generated files.

## Repeatable patterns

### Availability snapshot

- Use the helper script first.
- Quote exact filenames in the answer if availability itself matters.

### Single-year summary

- Pick one source type and one metric.
- Aggregate at one grain only.
- State whether the result is allocation, revised plan, period plan, or actual.

### Budget vs actual comparison

- Full-year comparison: `BUDGET_LAW` vs `SPENDING_Q1234`.
- Partial-year comparison: use `SPENDING_Q1`, `SPENDING_Q12`, or `SPENDING_Q123`, and label the result as year-to-date.
- If you compare partial-year actuals to annual budget or revised annual plan, say that the comparison is intentionally mixed-horizon.

### Cross-year trend table

- Keep the metric definition stable across years.
- If a year is missing the preferred source type, either omit the year or clearly mark it as unavailable.
- Note reorganizations, code changes, or manual mappings when continuity is not trivial.

### Chart or report generation

- The skill does not force a charting stack or report format.
- Whatever the output, embed or accompany it with provenance.
- For file artifacts, write `<artifact_filename>.provenance.json` next to the artifact.

## Sources & derivation section

Every text or table answer should end with a short inline section like this:

```md
**Sources & derivation**
- Data root: `...`
- Source files: `2024_BUDGET_LAW.csv`, `2024_SPENDING_Q1234.csv`
- Grain: `program`
- Metrics: `program_total`, `program_actual`
- Filters or mappings: `state_body contains "..."`
- Caveats: `None` or a concise note
```

## Provenance sidecar JSON

Generated files should have a sidecar JSON named `<artifact_filename>.provenance.json`.

Required fields:

- `artifact`
- `generated_at`
- `data_root`
- `source_files`
- `years`
- `source_types`
- `grain`
- `metrics`
- `filters_or_mappings`
- `caveats`

Example:

```json
{
  "artifact": "docs/generated/example_chart.html",
  "generated_at": "2026-03-06T12:00:00Z",
  "data_root": "/abs/path/data/processed",
  "source_files": [
    "2024_BUDGET_LAW.csv",
    "2024_SPENDING_Q1234.csv"
  ],
  "years": [2024],
  "source_types": ["BUDGET_LAW", "SPENDING_Q1234"],
  "grain": "program",
  "metrics": ["program_total", "program_actual"],
  "filters_or_mappings": [
    "program_code == 1162"
  ],
  "caveats": [
    "None"
  ]
}
```

## Cross-year caveats to state explicitly

- Missing dataset coverage for some years
- Partial-year vs full-year mismatches
- Institutional reorganizations and renamed state bodies
- Program or subprogram continuity that required manual mapping
- External denominators or classifications not present in parsed files
