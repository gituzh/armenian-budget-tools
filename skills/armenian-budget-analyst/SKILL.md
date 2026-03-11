---
name: armenian-budget-analyst
description: "Analyze parsed Armenian budget CSVs: inspect year and source availability, compare allocations and spending across ministries, programs, and subprograms, and create source-cited tables, charts, and reports from data/processed."
---

# Armenian Budget Analyst

Use this skill for analysis of parsed Armenian budget data in `data/processed`.

## Start here

1. Bootstrap the repo environment:
   - if `.venv` does not exist, create it with `uv venv .venv` when `uv` is available; otherwise use `python -m venv .venv`
   - install main dependencies with `.venv/bin/pip install -U -e .`
   - use `.venv/bin/python` for local scripts and one-off analysis commands
   - if both venv creation paths fail, explain the minimum prerequisite instead of guessing:
     - macOS: install `uv` with `brew install uv`, or install Python 3.10+ with `brew install python`
     - Debian/Ubuntu: install `uv`, or install `python3` plus `python3-venv`
     - Windows: install `uv`, or install Python 3.10+ from `winget` or python.org with venv support enabled
2. Resolve the data root:
   - use `ARMENIAN_BUDGET_DATA_PATH` if set
   - otherwise use repo `data/processed`
   - if neither exists, fail clearly
3. Verify parsed data is actually present in the chosen data root.
   - if `data/processed` is missing or empty, do not invent data; point the user to another parsed data root or generate processed files first
4. Inventory datasets by year and source type before computing anything:
   - prefer `skills/armenian-budget-analyst/scripts/data_availability.py`
   - if that script is unavailable, fall back to direct filename discovery under `data/processed`
   - do not assume the helper script lives in the repo root
5. Pick the source type intentionally, then state the aggregation grain and metric before computing anything.

## Choose the right dataset

- `BUDGET_LAW`: allocation data
- `SPENDING_Q1234`: full-year actuals when available
- `SPENDING_Q1`, `SPENDING_Q12`, `SPENDING_Q123`: year-to-date data only; label partial coverage explicitly
- `MTEP`: projection and planning data only, not factual spending
- `*_overall.json`: fastest path for `overall`-grain year-level tasks; prefer these sidecars over full CSVs when you only need aggregate totals
  - `BUDGET_LAW_overall.json` exposes allocation totals via `overall_total`
  - `SPENDING_Q1234_overall.json` exposes full-year actuals via `overall_actual`

## Required workflow

1. Inventory available files first.
2. Treat budget availability and spending availability independently by year.
3. If a year has `BUDGET_LAW` but no matching full-year spending file, keep it as a budget-only year instead of dropping it silently.
4. Name the exact source files used.
5. State the grain explicitly: `overall`, `state_body`, `program`, or `subprogram`.
6. State the metric explicitly: `overall_total`, `overall_actual`, `*_total`, `*_annual_plan`, `*_rev_annual_plan`, `*_actual`, or `*_total_y0/y1/y2`.
7. Keep parsed-data facts separate from any external denominator, manual classification, or policy interpretation.
8. Add provenance to every output:
   - inline `Sources & derivation` for text and table answers
   - sidecar JSON `<artifact_filename>.provenance.json` for generated files

## Output tips

- For simple chart artifacts, direct SVG generation is a robust fallback when plotting libraries are unavailable.
- If you use the SVG fallback, keep labels, source types, missing-data notes, and comparability warnings inside the chart or its provenance sidecar.

## Hard rules

- Do not mix program-level and subprogram-level numbers silently.
- Do not sum repeated `program_*` or `state_body_*` totals across every subprogram row; deduplicate parent totals before aggregating above `subprogram` grain.
- Do not assume budget and spending datasets overlap for the same year.
- Do not compare partial-year actuals with full-year actuals without labeling the mismatch.
- Do not substitute a missing factual series with an estimate, forecast, expected value, or external hardcoded number unless the user explicitly asks for that.
- Do not treat `MTEP` as executed spending.
- Do not use `assets/` as a live data mirror.
- If a mapping is manual or topic-specific, state it explicitly in `filters_or_mappings`.
- If a topic mapping is reused across years or outputs, keep it as a separate explicit mapping artifact or script rather than implying it as a native dataset fact.

## References

- `references/datasets.md`: dataset semantics and comparability rules
- `references/analysis.md`: repeatable output patterns and provenance contract
- `references/examples.md`: short worked examples, including one R&D example
