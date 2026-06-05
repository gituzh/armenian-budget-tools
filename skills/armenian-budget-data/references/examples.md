# Examples

These are short worked examples for generic parsed-data use, not a separate
domain mode. Domain-specific mappings belong in downstream skills.

## Example: generic budget vs actual summary

Question:

`Compare one ministry's 2024 allocation and full-year actual spending at program level.`

Approach:

1. Check availability and confirm both `2024_BUDGET_LAW.csv` and `2024_SPENDING_Q1234.csv` exist.
2. Choose `program` grain.
3. Use `program_total` from `BUDGET_LAW` and `program_actual` from `SPENDING_Q1234`.
4. Filter the same ministry in both files.
5. Output the summary with inline `Sources & derivation`.

## Example: topic-mapped chart

Question:

`Build a chart for a manually mapped topic across several years.`

Approach:

1. Check availability for each requested year and source type.
2. Use the downstream skill or explicit user instruction for the topic mapping.
3. Keep the mapping separate from parsed facts in `filters_or_mappings`.
4. Use one source horizon per series, or label mixed horizons explicitly.
5. Add inline provenance or a sidecar JSON for generated files.
