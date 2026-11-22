# Source Labels, Part 2: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish the label feature after the owner's review: make `sources.yaml` the list of labelled versions, read XML spreadsheets, add the 2021 parliament draft and the revised parliament drafts (`PARLIAMENT2`) for 2020 to 2026, and document the PDF limits.

**Architecture:** Labelled versions come from the registry only; folders on disk no longer create versions. A workbook that is Excel 2003 XML is turned into the same DataFrame `pd.read_excel` would give, by one helper the parsers call in place of `pd.read_excel`. New versions are plain registry entries processed by the normal pipeline.

**Tech Stack:** Python 3.10+, argparse CLI, PyYAML, pandas, pytest. No new dependencies (`xml.etree.ElementTree` from the standard library).

**Spec:** `docs/superpowers/specs/2026-11-22-source-labels-design.md`, section "Amendments after the first build" (it overrides the rest of the spec and Part 1 of the plan where they differ).

## Global Constraints

- Work on the existing branch `feat/source-labels` in the worktree `.worktrees/source-labels` (tip `fdd6ddf` at the start). Do not rebase it.
- Run everything with `PYTHONPATH=<worktree>/src` and the root `.venv` (`<repo>/.venv/bin/pytest`, `<repo>/.venv/bin/armenian-budget`), or tests silently import the main checkout.
- Commit identity on every commit: `git -c user.name="Tigran Shahverdyan" -c user.email=114946824+tigran-gituzh@users.noreply.github.com commit ...`. Subjects: `<type>: <subject>`, no scope, 50 characters at most.
- First commit: the spec amendment and this plan (`docs: add source labels part 2 plan`).
- Label format `^[A-Z0-9]+$`; `GDP` is reserved.
- Unlabelled behaviour is frozen: paths, discovery keys, output names and output bytes of every existing dataset stay the same. The 9 labelled CSVs already committed on the branch also keep their bytes.
- `git status --short data/` must be empty after Tasks 1 and 2.
- No PDF reading, no new downloader or site client, no new dependency, no `same_as`, no ordering by label name.
- Nothing on disk outside scratch is deleted. `data/original/budget_laws/2020_PARLIAMENT` and `data/extracted/budget_laws/2020_PARLIAMENT` stay where they are.
- No push, no merge into `dev`, no release. Stop at a committed branch and a report.
- Before the final report: no new `ruff check src/ tests/` findings against `dev`, full `pytest -q`. `black` is not installed; install nothing.

## Review Focus

1. A labelled folder on disk with no registry entry produces no output file and exactly one warning per run that names the folder. (Task 1)
2. `--input FILE` still writes only the unlabelled outputs and needs no readable `sources.yaml`. (Task 1)
3. A workbook that is not XML takes the same `pd.read_excel` call as before, so existing outputs cannot change. (Task 2)
4. The XML reader keeps column positions: a cell with `ss:Index` lands in that column, and a cell after a merged cell (`ss:MergeAcross="2"`) lands three columns later. (Task 2)
5. Whole-number cells in XML become `int`, as they do from `pd.read_excel`, so codes read `11001`, not `11001.0`. (Task 2)

---

### Task 1: The registry is the list of labelled versions

**Files:**
- Modify: `src/armenian_budget/interfaces/cli/main.py` (`_select_versions` and its callers in `extract`, `discover`, `process`, `validate`, `gdp-extract`)
- Modify: `src/armenian_budget/validation/identical.py` only if it lists versions from disk
- Test: `tests/cli/test_label_commands.py`, `tests/validation/test_identical_data_note.py`, `tests/parser/test_gdp_labels.py`

**Behaviour:**
- Labelled versions of a year and source type = the labels registered in `sources.yaml` for it. Folders and processed files on disk never add a label.
- The unlabelled version is found as today.
- A labelled year folder (`<year>_<LABEL>` matching the label format) under `data/original/<category>/` or `data/extracted/<category>/` whose label is not registered for that year and category: one `WARNING` per run and folder, text `Ignoring <path>: <LABEL> is not registered for <year> in sources.yaml`. No output, not counted as a failure.
- `--label X` where `X` is not registered for a requested year: reported as missing for that year with the existing "nothing processed/validated" exit rule, in `download`, `extract`, `process`, `validate` and `gdp-extract` alike (today `download` and `extract` exit 0 with a warning). `gdp-extract` says the label is not registered, not "no budget message registered".
- The identical-data note compares the unlabelled CSV and the registered labels' CSVs only.
- `sources.yaml` missing or invalid: unlabelled work continues as today; labelled versions are not run and one warning says so; with `--label` this is an error exit.
- `extract` with auto-detected years does not create an empty unlabelled folder for a year that has only labelled versions (2027).

- [ ] **Step 1: Write the failing tests**
  - `test_unregistered_label_folder_is_ignored` (Review Focus 1): registry with `EDRAFT` for 2026; `extracted/budget_laws/2026_PARLIAMENT/` holds a workbook; `process --years 2026` writes no `2026_BUDGET_LAW_PARLIAMENT.*`, logs the warning once, exit code unchanged.
  - `test_validate_ignores_unregistered_csv`: a stray `2026_BUDGET_LAW_OLD.csv` in the processed root is neither validated nor named in any identical-data note.
  - `test_label_not_registered_fails_everywhere`: parametrized over the five commands with `--label NOPE` → non-zero exit.
  - `test_input_needs_no_registry` (Review Focus 2): `process --input FILE --config /nonexistent.yaml` writes the unlabelled outputs.
  - `test_invalid_registry_runs_unlabelled_only`: invalid `sources.yaml` → unlabelled dataset processed, warning logged; with `--label EDRAFT` non-zero exit.
  - `test_extract_no_empty_unlabelled_folder`: only `original/budget_laws/2027_DRAFT/` exists and is registered → `extract` with no `--years` creates no `extracted/budget_laws/2027/`.
  - Update existing tests that create a labelled version from a folder alone so that they register it in a test `sources.yaml`; do not weaken what they assert.
- [ ] **Step 2: Run them, expect failures**
- [ ] **Step 3: Implement**
- [ ] **Step 4: Run them, expect pass; then full `pytest -q`.** Regression on real data into a scratch processed root: `process` and `validate --report --report-json` for 2019-2027, `--source-type BUDGET_LAW`, with the real `--extracted-root`. Every CSV and `_overall.json` committed on the branch reproduces byte-identically, reports differ only in the timestamp line, no `2020_BUDGET_LAW_PARLIAMENT.*` and no `2021_BUDGET_LAW_PARLIAMENT.*` appears, and the log has the "Ignoring" warning for both folders.
- [ ] **Step 5: Commit** — `feat: take labelled versions from sources only`

### Task 2: Read Excel 2003 XML workbooks

**Files:**
- Create: `src/armenian_budget/ingestion/parsers/workbook_reader.py`
- Modify: `src/armenian_budget/ingestion/parsers/excel_2019_2024.py:189`, `excel_2025.py:86`, `excel_mtep.py:66` (the `pd.read_excel(excel_file_path, sheet_name=0, header=None)` call), and any other place under `src/` that opens a candidate workbook with pandas (grep `read_excel`)
- Test: `tests/parser/test_workbook_reader.py` (new)

**Interfaces — produces:**
- `read_first_sheet(path) -> pd.DataFrame`: if the file starts with `<?xml` (after optional BOM/whitespace) and its root element is `{urn:schemas-microsoft-com:office:spreadsheet}Workbook`, return the first worksheet as a DataFrame with integer column labels and no header row; otherwise return `pd.read_excel(path, sheet_name=0, header=None)` unchanged.
- XML rules: rows and cells may carry `ss:Index` (1-based position; without it, previous + 1); `ss:MergeAcross="n"` moves the next cell `n` extra columns; `Data ss:Type="Number"` becomes `int` when the text has no `.`, `e` or `E`, else `float`; other types stay text; an empty or absent cell is `None`/NaN as in `pd.read_excel`. Numeric character references to control characters that XML 1.0 forbids (`&#1;` … `&#31;` except 9, 10, 13) are removed before parsing; the 2021 workbook contains `&#1;` and `&#30;`.

A working reader, written for the scratch check (`/home/tigran/.hermes/cache/scratch/sl2/probe.py`, function `spreadsheetml_to_df`), which you may adapt:

```python
NS = "{urn:schemas-microsoft-com:office:spreadsheet}"

def spreadsheetml_to_df(path):
    raw = Path(path).read_bytes()
    raw = re.sub(rb"&#(?:[0-8]|1[124-9]|2[0-9]|3[01]);", b"", raw)
    root = ET.fromstring(raw)
    table = root.find(f"{NS}Worksheet/{NS}Table")
    rows = {}
    r = 0
    for row in table.findall(f"{NS}Row"):
        r = int(row.get(f"{NS}Index", r + 1))
        c = 0
        for cell in row.findall(f"{NS}Cell"):
            c = int(cell.get(f"{NS}Index", c + 1))
            data = cell.find(f"{NS}Data")
            if data is not None:
                text = "".join(data.itertext())
                if data.get(f"{NS}Type") == "Number":
                    val = float(text) if re.search(r"[.eE]", text) else int(text)
                else:
                    val = text
                rows.setdefault(r, {})[c] = val
            c += int(cell.get(f"{NS}MergeAcross", 0))
    nr = max(rows)
    nc = max(max(v) for v in rows.values())
    return pd.DataFrame([[rows.get(i, {}).get(j) for j in range(1, nc + 1)] for i in range(1, nr + 1)])
```

- [ ] **Step 1: Write the failing tests** (synthetic XML written by the test, no real data)
  - `test_xml_cell_positions` (Review Focus 4): row `ss:Index="3"`, a cell `ss:Index="4"`, a cell after `ss:MergeAcross="2"`.
  - `test_xml_number_types` (Review Focus 5): `11001` → `int`, `12.5` → `float`, `1E3` → `float`, a String `"007"` stays `"007"`.
  - `test_xml_control_character_refs_removed`.
  - `test_non_xml_goes_to_pandas` (Review Focus 3): an `.xlsx` written with pandas gives a frame equal to `pd.read_excel(..., header=None)`; `pd.read_excel` is called exactly once with the same arguments (monkeypatch).
  - `test_xml_workbook_parses_like_xlsx`: build a small 2019-2024-layout budget-law table as a DataFrame, write it once as `.xlsx` and once as SpreadsheetML named `.xls`, run `flatten_budget_excel_2019_2024` on both → equal result frames and totals.
  - `test_other_xml_is_not_claimed`: a file starting with `<?xml` whose root is not the spreadsheet `Workbook` goes to pandas (and fails there as before).
- [ ] **Step 2: Run them, expect failures**
- [ ] **Step 3: Implement**
- [ ] **Step 4: Run them, expect pass; then full `pytest -q`.** Regression on real data into a scratch processed root: `process` for 2019-2027 with **all** source types (budget laws, spending, MTEP), real `--extracted-root`: every CSV and `_overall.json` committed on the branch reproduces byte-identically.
- [ ] **Step 5: Commit** — `feat: read Excel 2003 XML workbooks`

### Task 3: Register the 2021 draft and the revised drafts

**Files:**
- Modify: `config/sources.yaml`, `config/checksums.yaml`
- Modify: `data/extracted/discovery_index.json` (new keys only, merged key by key)
- Create: `data/processed/<year>_BUDGET_LAW_PARLIAMENT2.*` for 2020-2026, `data/processed/2021_BUDGET_LAW_PARLIAMENT.*`
- Modify: `data/processed/<year>_BUDGET_LAW_validation.{md,json}` for 2020-2026 (identical-data note) and the 2026 `DRAFT2` reports

Entries to add (annexes archive only; `file_format: "rar"`; same shape as `2025_budget_law_parliament`):

| name | year | label | published | url (under `https://parliament.am/diskStorage/`) | archive sha256 starts |
|---|---|---|---|---|---|
| `2021_budget_law_parliament` | 2021 | `PARLIAMENT` | 2020-10-01 | `draft_docs7/K-752/K-752_orenqi_havelvacner.rar` | `d712bcc0ff80b7b1` |
| `2020_budget_law_parliament2` | 2020 | `PARLIAMENT2` | — | `draft_docs7/K-306lr_havelvatsner.rar` | `0b7272a6190b7067` |
| `2021_budget_law_parliament2` | 2021 | `PARLIAMENT2` | 2020-12-07 | `draft_docs7/K-752lr/K-752lr_orenq_havelvacner.rar` | `b962d5739de11907` |
| `2022_budget_law_parliament2` | 2022 | `PARLIAMENT2` | — | `draft_docs8/K-059lr_havelvatsner.rar` | `22501d02259af577` |
| `2023_budget_law_parliament2` | 2023 | `PARLIAMENT2` | — | `draft_docs8/K-382lr_orenqi_havelvatsner.rar` | `8a7d2ad0cd78eed0` |
| `2024_budget_law_parliament2` | 2024 | `PARLIAMENT2` | 2023-12-04 | `draft_docs8/K-669lr_havelvatsner.rar` | `29c4e8489a6b4ada` |
| `2025_budget_law_parliament2` | 2025 | `PARLIAMENT2` | 2024-12-02 | `draft_docs8/K-932lr_havelvatsner.rar` | `d88ec56060303d71` |
| `2026_budget_law_parliament2` | 2026 | `PARLIAMENT2` | 2025-12-01 | `draft_docs8/K-1160lr_havelvatsner.rar` | `b3bdc72b2fa666cb` |

- `published` for `PARLIAMENT2` is the second date in the reading code on parliament.am (`Կ-752-02.10.2020,07.12.2020-…`). 2020, 2022 and 2023 have no such code in the draft history, and the files' `Last-Modified` is a 2026 re-upload, so they stay empty. Do not search further.
- Description wording: `"<year> budget law revised draft for the second reading (parliament.am draft K-<n>)"`.
- Several inner file names end in `..xls`/`..xlsx`; if extraction or the downloader needs a `filename` override, use the mechanism the registry already has.
- The 2021 `PARLIAMENT` archive is already in `data/original/budget_laws/2021_PARLIAMENT/`; let the downloader verify or re-fetch it.

- [ ] **Step 1: Add the entries; run `download`, `extract`, `process`, `validate --report --report-json` for 2020-2026** through the CLI, `--source-type BUDGET_LAW`, real original and extracted roots, processed root = the worktree's `data/processed`.
- [ ] **Step 2: Check against the scratch measurements**

| Check | Expected |
|---|---|
| `2021_BUDGET_LAW_PARLIAMENT.csv` | 746 rows, `overall_total` 1843133616.39, 0 validation errors (sha256 starts `00d5687c541e` in the scratch run through an xlsx conversion; if yours differs, report both and say which cells differ) |
| `<year>_BUDGET_LAW_PARLIAMENT2.csv`, 2020-2026 | byte-identical to `<year>_BUDGET_LAW.csv`; rows 802, 752, 801, 853, 857, 827, 797 |
| identical-data note, adopted law 2020-2025 | names `PARLIAMENT2` and `(unlabelled)` |
| identical-data note, 2026 | names `DRAFT2`, `PARLIAMENT2`, `(unlabelled)` |
| every existing CSV, `_overall.json`, `_GDP.json`, `gdp_report.html` | unchanged |
| `git status --short data/processed` | only new `PARLIAMENT2` and 2021 `PARLIAMENT` files and reports whose note changed; timestamp-only report changes restored |
| no `2020_BUDGET_LAW_PARLIAMENT.*` | true; the run logs the "Ignoring" warning for `2020_PARLIAMENT` |

  A version that fails to download or parse is left unregistered and reported; do not work around it.
- [ ] **Step 3: Tests** — the config tests (`tests/sources/`) pass with the new entries (2026 `PARLIAMENT2` shares its checksum with `DRAFT2`; different labels of one year may). Full `pytest -q`.
- [ ] **Step 4: Discovery index and main checkout** — merge the new keys into the worktree's `data/extracted/discovery_index.json`, restore the main checkout's copy (`git -C <repo> checkout -- data/extracted/discovery_index.json`), confirm the main checkout's `git status --short` is clean.
- [ ] **Step 5: Commit** — `feat: add revised parliament budget drafts` (the 2021 `PARLIAMENT` entry may be its own commit: `feat: add 2021 budget law parliament draft`).

### Task 4: Documentation

**Files:**
- Modify: `docs/data_schemas.md` (section 3.4 Source Labels), `skills/armenian-budget-data/` dataset reference where labels are listed, `CHANGELOG.md` (`Unreleased`, version-neutral), `docs/roadmap.md` only if it names something this delivers

- [ ] **Step 1: Write**
  - Label table: add `PARLIAMENT2` = revised draft published for the second reading; say that in 2020-2026 it holds the same data as the adopted law.
  - Replace the text saying unregistered folders on disk are processed with the new rule (registered versions only; a stray folder is ignored with a warning).
  - A **Known limitations** list under 3.4:
    - PDF sources are not read.
    - 2020 `PARLIAMENT`: the programme table is published only as PDF, so there is no dataset (2020 `PARLIAMENT2` exists).
    - `PARLIAMENT` and `PARLIAMENT2` versions have no `_GDP.json`: parliament.am publishes the budget message only as PDF.
    - 2019: parliament.am shows no draft history for the law.
    - 2026 `DRAFT`: the first e-gov draft (25 Sep 2025) is lost.
    - Dataset-driven tests cover unlabelled datasets only.
  - Supported input formats: mention Excel 2003 XML saved as `.xls`.
  - Changelog: revised parliament drafts 2020-2026 and the 2021 parliament draft added; XML workbooks readable; labelled versions come from `sources.yaml` only.
- [ ] **Step 2: Commit** — `docs: document revised drafts and limits`

### Task 5: Whole-branch review and report

- [ ] **Step 1:** Full `pytest -q`, ruff comparison against `dev`, `git log --format='%ae %ce' dev..feat/source-labels | sort -u` shows only the noreply address.
- [ ] **Step 2:** Whole-branch review of `dev...feat/source-labels` on the most capable model, as SDD's final review describes. One fix wave for Critical and Important findings, each with a test that fails first; a scoped re-review of the fix diff.
- [ ] **Step 3:** Final report (contents in the handoff).
