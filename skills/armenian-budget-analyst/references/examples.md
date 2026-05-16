# Examples

These are short worked examples, not a separate domain mode.

## Example: generic budget vs actual summary

Question:

`Compare one ministry's 2024 allocation and full-year actual spending at program level.`

Approach:

1. Check availability and confirm both `2024_BUDGET_LAW.csv` and `2024_SPENDING_Q1234.csv` exist.
2. Choose `program` grain.
3. Use `program_total` from `BUDGET_LAW` and `program_actual` from `SPENDING_Q1234`.
4. Filter the same ministry in both files.
5. Output the summary with inline `Sources & derivation`.

## Example: R&D stacked spending chart

This is illustrative only. The skill remains general-purpose.

Goal:

`Build a stacked absolute spending chart for HESC and MIC from parsed files only.`

Files used:

- `2019_BUDGET_LAW.csv` through `2026_BUDGET_LAW.csv`
- `2019_SPENDING_Q1234.csv` through `2025_SPENDING_Q1234.csv`
- `2026_SPENDING_Q1.csv`, if the user explicitly wants the latest partial-year
  spending shown and labeled as Q1

Illustrative mapping:

- HESC budget and factuals are taken at `program` grain from program code `1162`.
- MIC budget and factuals are taken at `subprogram` grain from topic-specific R&D rows.
- The MIC continuity is not trivial across years and requires an explicit mapping note.

Caveats that must be stated:

- `2019` crosses an institutional transition, so continuity is manual rather than automatic.
- `2026` has budget data and Q1 spending data, but no parsed full-year factual spending file.
- `2026_SPENDING_Q1.csv` must be shown as partial-year Q1 spending, not full-year factual spending.
- Do not replace a missing full-year factual with a partial-year, expected, or forecast value unless the user explicitly asks for a mixed-horizon or projected series.
- GDP-share versions can use parsed GDP snapshots when the needed year, source, and scenario/status are available; otherwise the denominator is external or unavailable and must be labeled.
- The topical R&D classification is a mapping layer on top of parsed budget facts; keep that mapping separate and explicit in provenance.

Minimum provenance for the chart:

- exact source CSV basenames
- grain used for each series
- manual filters or mappings
- GDP denominator source, scenario/status, and unit conversion if a GDP-share chart is produced
- any partial-year labels if a non-`SPENDING_Q1234` source is intentionally used
- a sidecar JSON named after the generated chart file
