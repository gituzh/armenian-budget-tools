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
- `2019_SPENDING_Q1234.csv` through `2024_SPENDING_Q1234.csv`
- `2025_SPENDING_Q123.csv`

Illustrative mapping:

- HESC budget and factuals are taken at `program` grain from program code `1162`.
- MIC budget and factuals are taken at `subprogram` grain from topic-specific R&D rows.
- The MIC continuity is not trivial across years and requires an explicit mapping note.

Caveats that must be stated:

- `2019` crosses an institutional transition, so continuity is manual rather than automatic.
- `2025` factual spending is only available through `Q123`; it must be labeled as partial-year.
- `2026` has budget data but no parsed factual spending file.
- GDP-share versions of the chart need an external GDP denominator and are not derivable from parsed files alone.

Minimum provenance for the chart:

- exact source CSV basenames
- grain used for each series
- manual filters or mappings
- the `Q123` partial-year label for `2025`
- a sidecar JSON named after the generated chart file
