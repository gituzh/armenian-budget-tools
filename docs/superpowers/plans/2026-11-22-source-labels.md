# Source Labels Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let one year and source type hold several labelled versions of a document, each processed by the normal pipeline, and add the known budget-law drafts.

**Architecture:** A label is an optional string on a source entry. It becomes a suffix on the year folder under `data/original/` and `data/extracted/`, a third segment of the discovery-index key, and a suffix on every output file name. Commands find the versions of a year from what is on disk (config for `download`), so nothing downstream of the registry needs a list of labels. Identical versions are reported from the processed CSVs when validation runs.

**Tech Stack:** Python 3.10+, argparse CLI, PyYAML, pandas, pytest. No new dependencies.

**Spec:** `docs/superpowers/specs/2026-11-22-source-labels-design.md` (read it first; this plan argues from it).

## Global Constraints

- `dev` must contain `22b5f96` (the 2025 e-draft parser fix). Branch `feat/source-labels` from `dev`, worktree `.worktrees/source-labels`. Run everything with `PYTHONPATH=<worktree>/src` and the root `.venv` (`<repo>/.venv/bin/pytest`), or tests silently import the main checkout.
- Commit identity on every commit: `git -c user.name="Tigran Shahverdyan" -c user.email=114946824+tigran-gituzh@users.noreply.github.com commit ...` (the owner's noreply address; older commits on `dev` carry a gmail address, do not copy it). Subjects per `git-workflow`: `<type>: <subject>`, no scope, 50 characters at most.
- Commit the spec and this plan first (`docs: add source labels spec and plan`).
- Label format `^[A-Z0-9]+$`; `GDP` is reserved.
- Unlabelled behaviour is frozen: paths, discovery keys, output names and output bytes of every existing dataset stay the same. After every task, `git status --short data/` must be empty until Task 7.
- No new downloader or site client, no parser change, no `same_as`, no ordering by label name, no drafts on the GDP report page.
- A version is registered in `sources.yaml` only if it downloads through the existing downloader and parses with the existing parser. Otherwise leave it out and list it in the final report.
- No push, no merge into `dev`, no release. Stop at a committed branch and a report.
- Before the final report: `ruff check src/ tests/`, `black --check src/ tests/`, full `pytest -q`.

## Review Focus

Inputs the spec implies and no acceptance line names. Each has a test in the task shown.

1. `--label X` for a year that has no version `X`: that year is reported as a failure or missing dataset, and the exit code follows the existing "nothing processed/validated" rule. It is never silently skipped. (Task 3)
2. `--label edraft` in lower case on the command line is accepted and treated as `EDRAFT`; `label: edraft` in `sources.yaml` is a load error. (Tasks 1, 3)
3. `extract` with no `--years` finds `2026_EDRAFT` although the folder name is not all digits, and ignores a folder such as `2026_old-copy`. (Task 2)
4. `--input FILE` with no label flag writes only the unlabelled outputs, as today, even when labelled versions exist on disk. (Task 3)
5. `validate --label EDRAFT` still compares `EDRAFT` against every version on disk for the identical-data note, not only the selected one. (Task 4)
6. `gdp-extract` for the unlabelled 2026 law still picks the adopted law's budget message once labelled 2026 entries with their own `explanatory_note` files exist. Today the lookup takes the first `explanatory_note` entry of the year, whatever its label. (Task 5)
7. `gdp-report` and `load_gdp_snapshots` skip labelled snapshots, so `gdp_report.html` does not change when draft GDP files appear. (Task 5)

---

### Task 1: Label on the registry and in names

**Files:**
- Modify: `src/armenian_budget/sources/registry.py`
- Modify: `src/armenian_budget/core/utils.py`
- Test: `tests/sources/test_registry.py`, `tests/test_label_naming.py` (new)

**Interfaces — produces:**
- `SourceDefinition.label: Optional[str] = None`, `SourceDefinition.published: Optional[datetime.date] = None`. Both are read from the entry level and copied to each of its `files`.
- `SourceRegistry.published_by_label(year: int, source_type: str) -> dict[Optional[str], Optional[datetime.date]]` (`source_type` lower case as in YAML; key `None` is the unlabelled entry).
- In `core/utils.py`:
  - `LABEL_RE = re.compile(r"^[A-Z0-9]+$")`, `RESERVED_LABELS = frozenset({"GDP"})`
  - `validate_label(label: str) -> str` (returns it, raises `ValueError`)
  - `year_dir_name(year: int, label: Optional[str] = None) -> str` → `"2026"` / `"2026_EDRAFT"`
  - `dataset_stem(year: int, source_type_name: str, label: Optional[str] = None) -> str` → `"2026_BUDGET_LAW"` / `"2026_BUDGET_LAW_EDRAFT"`
  - `get_processed_paths(year, source_type, processed_root, label: Optional[str] = None)` (new optional last parameter)

- [ ] **Step 1: Write the failing tests**

`tests/test_label_naming.py`:
- `test_dataset_stem`: `dataset_stem(2026, "BUDGET_LAW") == "2026_BUDGET_LAW"`; with `"EDRAFT"` → `"2026_BUDGET_LAW_EDRAFT"`.
- `test_year_dir_name`: `"2026"` and `"2026_EDRAFT"`.
- `test_processed_paths_with_label`: names `2026_BUDGET_LAW_EDRAFT.csv` and `2026_BUDGET_LAW_EDRAFT_overall.json`; without label unchanged.
- `test_validate_label_rejects`: parametrized over `"edraft"`, `"E_DRAFT"`, `"E-DRAFT"`, `""`, `"GDP"` → `ValueError`.

`tests/sources/test_registry.py`:
- `test_registry_reads_label_and_published`: entry with `label: "EDRAFT"`, `published: 2025-10-01` and two files → both `SourceDefinition`s carry `label == "EDRAFT"` and `published == date(2025, 10, 1)`. A quoted `published: "2025-10-01"` gives the same date.
- `test_registry_defaults_are_unlabelled`: existing-style entry → `label is None`, `published is None`.
- `test_registry_rejects_bad_label`: `label: edraft` and `label: GDP` → `ValueError` naming the entry.
- `test_registry_rejects_bad_published`: `published: "October 2025"` → `ValueError`.
- `test_registry_rejects_duplicate_version`: two entries with different `name`, same year, source type and label (also two unlabelled ones) → `ValueError`.
- `test_published_by_label`: unlabelled dated entry plus `EDRAFT` dated and `PARLIAMENT` undated → `{None: date, "EDRAFT": date, "PARLIAMENT": None}`.

- [ ] **Step 2: Run them, expect failures** — `pytest tests/test_label_naming.py tests/sources/test_registry.py -q`
- [ ] **Step 3: Implement** the fields, validation at load time and the helpers. A YAML label that is not a string (for example `label: 2`) is converted with `str()` before validation.
- [ ] **Step 4: Run them, expect pass; then `pytest -q`** (the real `config/sources.yaml` must still load: `test_registry_rejects_duplicate_version` must not fire on existing entries).
- [ ] **Step 5: Commit** — `feat: read label and published date from sources`

### Task 2: Separate folders and discovery keys per version

**Files:**
- Modify: `src/armenian_budget/sources/downloader.py` (`_category_and_subdir`, its call site)
- Modify: `src/armenian_budget/ingestion/discovery.py` (`_iter_search_roots`, `discover_best_file`)
- Modify: `src/armenian_budget/interfaces/cli/main.py` (`cmd_extract` only)
- Modify: `src/armenian_budget/core/utils.py`
- Test: `tests/sources/test_label_folders.py` (new), `tests/test_discovery_labels.py` (new)

**Interfaces — consumes:** `year_dir_name`, `validate_label`, `LABEL_RE` from Task 1.

**Interfaces — produces:**
- `_category_and_subdir(original_root, year, source_type, label=None)`: the year segment becomes `year_dir_name(year, label)` for every category, e.g. `budget_laws/2026_EDRAFT`, `spending_reports/2026_X/Q1`.
- `discover_best_file(..., label: Optional[str] = None)`: search root uses the same year segment; index key is `f"{year}/{source_type.lower()}"` when unlabelled (unchanged) and `f"{year}/{source_type.lower()}/{label}"` otherwise.
- `core/utils.py`: `list_version_dirs(category_root: Path, year: int) -> list[Optional[str]]` — labels of the folders `<year>` and `<year>_<LABEL>` that exist under `category_root`; `None` first when `<year>` exists, then labels sorted; names that do not match `LABEL_RE` are ignored.

- [ ] **Step 1: Write the failing tests**

`tests/sources/test_label_folders.py`:
- `test_subdir_unlabelled_unchanged`: budget law 2026 → `original/budget_laws/2026`; spending Q1 → `original/spending_reports/2026/Q1`.
- `test_subdir_labelled`: → `original/budget_laws/2026_EDRAFT`, `original/spending_reports/2026_X/Q1`.
- `test_list_version_dirs`: folders `2026`, `2026_EDRAFT`, `2026_DRAFT2`, `2026_old-copy`, `2025_EDRAFT` → `[None, "DRAFT2", "EDRAFT"]` for 2026.
- `test_extract_covers_labelled_folders` (Review Focus 3): build `original/budget_laws/2026/a.zip` and `original/budget_laws/2026_EDRAFT/b.zip`, run `cmd_extract` with no `--years` → `extracted/budget_laws/2026/a/...` and `extracted/budget_laws/2026_EDRAFT/b/...` both exist; a `2026_old-copy` folder is not extracted.

`tests/test_discovery_labels.py` (workbooks are ≥ 20 KB dummy `.xlsx` files whose names match the global budget-law pattern; use `tests`' own `parsers.yaml` fixture or the repo's `config/parsers.yaml`):
- `test_unlabelled_discovery_ignores_labelled_folder`: only `budget_laws/2026_EDRAFT/` holds a workbook → `discover_best_file(year=2026, source_type="BUDGET_LAW")` raises `FileNotFoundError`.
- `test_labelled_discovery_ignores_unlabelled_folder`: only `budget_laws/2026/` holds one → `label="EDRAFT"` raises `FileNotFoundError`.
- `test_each_version_gets_its_own_workbook_and_key`: both folders hold one → each call returns the file in its own folder, and the saved index has keys `2026/budget_law` and `2026/budget_law/EDRAFT`.

- [ ] **Step 2: Run them, expect failures**
- [ ] **Step 3: Implement.** In `cmd_extract`, for each category and requested year extract every folder returned by `list_version_dirs`; when years are auto-detected, take them from folder names matching `^\d{4}(_[A-Z0-9]+)?$`. Selection flags come in Task 3.
- [ ] **Step 4: Run them, expect pass; then `pytest -q`**
- [ ] **Step 5: Commit** — `feat: keep each labelled version in its own folder`

### Task 3: Commands run every version, with `--label` and `--unlabelled`

**Files:**
- Modify: `src/armenian_budget/interfaces/cli/main.py` (`cmd_download`, `cmd_extract`, `cmd_discover`, `cmd_process`, `cmd_validate`, `build_parser`)
- Modify: `src/armenian_budget/core/utils.py`
- Test: `tests/cli/test_label_commands.py` (new)

**Interfaces — consumes:** Tasks 1 and 2.

**Interfaces — produces:**
- `core/utils.py`: `list_processed_labels(processed_root: Path, year: int, source_type_name: str) -> list[Optional[str]]` — from files `<year>_<TYPE>.csv` and `<year>_<TYPE>_<LABEL>.csv`; `None` first, then labels sorted. `2026_SPENDING_Q12.csv` is not a label of `SPENDING_Q1`.
- `main.py`: `_select_versions(available: list[Optional[str]], label: Optional[str], unlabelled: bool) -> list[Optional[str]]`:
  - `label` given → `[label]` (whether or not it is in `available`)
  - `unlabelled` → `[None]`
  - neither → `[None]` followed by the labels in `available` (the unlabelled version is always attempted, as today)
- Options on `download`, `extract`, `discover`, `process`, `validate`: `--label` (`type=str.upper`, checked with `validate_label`) and `--unlabelled`, mutually exclusive.
- Where each command gets `available` from: `download` from the registry entries; `extract` from `data/original`; `discover` and `process` from `data/extracted` (`list_version_dirs` on the category root); `validate` from `list_processed_labels`.

Behaviour to implement:
- `process` and `validate` write and read `dataset_stem(year, st_name, label)`-based names for the CSV, `_overall.json`, `_validation.md` and `_validation.json`.
- A labelled version's entry in the processing report and in the validation summary carries `"label": "<LABEL>"`, and its log line shows it (`2026 BUDGET_LAW EDRAFT: OK`). Unlabelled entries keep today's keys exactly.
- `process --input FILE`: with `--label X` writes the labelled outputs; with no flag writes only the unlabelled outputs.
- `download` passes each source's label to `_category_and_subdir`.

- [ ] **Step 1: Write the failing tests** (`tests/cli/test_label_commands.py`; stub the parser with `monkeypatch` so a one-row DataFrame and `{"overall_total": 1.0}` come back, as existing CLI tests do for their collaborators)
- `test_select_versions`: the three rules above, including `label="X"` with `available == [None]` → `["X"]`.
- `test_list_processed_labels`: files `2026_BUDGET_LAW.csv`, `2026_BUDGET_LAW_EDRAFT.csv`, `2026_BUDGET_LAW_GDP.json`, `2026_BUDGET_LAW_EDRAFT_validation.md`, `2026_SPENDING_Q12.csv` → `[None, "EDRAFT"]` for `BUDGET_LAW`, `[]` for `SPENDING_Q1`.
- `test_process_default_runs_all_versions`: extracted tree with `2026` and `2026_EDRAFT` → both `2026_BUDGET_LAW.csv` and `2026_BUDGET_LAW_EDRAFT.csv` (and their `_overall.json`) are written; exit 0.
- `test_process_label_runs_one`: `--label EDRAFT` → only the labelled pair is written.
- `test_process_unlabelled_runs_one`: `--unlabelled` → only the unlabelled pair.
- `test_process_label_lowercase` (Review Focus 2): `--label edraft` behaves as `EDRAFT`.
- `test_process_missing_label_fails` (Review Focus 1): `--label NOPE` for a year without it → report entry with `status == "FAIL"` and `label == "NOPE"`, exit 1.
- `test_process_input_writes_unlabelled_only` (Review Focus 4): labelled folder exists, `--input f.xlsx --source-type BUDGET_LAW --years 2026` → only `2026_BUDGET_LAW.csv`.
- `test_process_input_with_label`: same with `--label EDRAFT` → only `2026_BUDGET_LAW_EDRAFT.csv`.
- `test_label_and_unlabelled_conflict`: both flags → argparse error (exit 2).
- `test_validate_default_covers_labelled`: processed dir with both versions, `--report --report-json` → `2026_BUDGET_LAW_EDRAFT_validation.md` and `.json` exist next to the unlabelled ones.
- `test_validate_missing_label` (Review Focus 1): `--label NOPE` → summary entry `MISSING` with `label == "NOPE"`, exit 1.
- `test_download_uses_label_folder`: with the HTTP client stubbed as in `tests/cli/test_download_checksums.py`, a labelled source is saved under `budget_laws/2026_EDRAFT/`.
- `test_unlabelled_report_entry_shape_unchanged`: an unlabelled processing-report entry has exactly the keys `year`, `source`, `status`, `reason`.

- [ ] **Step 2: Run them, expect failures**
- [ ] **Step 3: Implement**
- [ ] **Step 4: Run them, expect pass; then `pytest -q`**
- [ ] **Step 5: Regression proof on real data.** Run `process --years 2019-2026` and `validate --years 2019-2026 --report --report-json` into a scratch `--processed-root` copy of `data/processed` (no labelled entries exist yet) and diff against `data/processed`: every existing CSV and `_overall.json` byte-identical; validation reports identical apart from their timestamp line. Record the diff summary for the final report.
- [ ] **Step 6: Commit** — `feat: process and validate every labelled version`

### Task 4: Identical-data note in validation reports

**Files:**
- Create: `src/armenian_budget/validation/identical.py`
- Modify: `src/armenian_budget/validation/models.py` (`ValidationReport`, `to_markdown`, `to_json`, `to_console_summary`)
- Modify: `src/armenian_budget/validation/registry.py` (`run_validation`)
- Modify: `src/armenian_budget/interfaces/cli/main.py` (`cmd_validate`: `--config`, default `config/sources.yaml`)
- Test: `tests/validation/test_identical_data_note.py` (new)

**Interfaces — consumes:** `list_processed_labels`, `get_processed_paths`, `SourceRegistry.published_by_label`.

**Interfaces — produces:**
- `identical.py`: `find_identical_versions(processed_root: Path, year: int, source_type: SourceType, label: Optional[str], published: Mapping[Optional[str], Optional[datetime.date]]) -> list[tuple[Optional[str], Optional[datetime.date]]]` — the versions whose CSV has the same sha256 as `label`'s CSV, itself included, when there is at least one other; otherwise `[]`. Order: by date ascending, ties by label with the unlabelled version first, undated last.
- `ValidationReport.identical_data: list[tuple[Optional[str], Optional[datetime.date]]]` (default empty).
- `run_validation(year, source_type, processed_root, label: Optional[str] = None, published: Optional[Mapping] = None)`.
- Rendering, only when the list is not empty:
  - Markdown, in the header block: `**Identical data:** EDRAFT (2025-10-01), PARLIAMENT (2025-10-01)`; the unlabelled version is written `(unlabelled)`; an undated one has no parentheses.
  - JSON: top-level `"identical_data": [{"label": "EDRAFT", "published": "2025-10-01"}, {"label": null, "published": null}]`. The key is absent when the list is empty, so existing reports do not change.
- The note never changes check results, counts, `has_errors` or exit codes.
- `cmd_validate` loads the registry from `--config` for the dates; if the file is missing it validates as today and the note is ordered by label only.

- [ ] **Step 1: Write the failing tests**
- `test_no_note_for_single_version`: one CSV → `[]`; Markdown has no `Identical data`; JSON has no `identical_data` key.
- `test_no_note_when_versions_differ`: two different CSVs → `[]` for both.
- `test_group_lists_all_identical_versions`: `EDRAFT` and `PARLIAMENT` same bytes, `DRAFT2` different → for `EDRAFT`: `[("EDRAFT", d1), ("PARLIAMENT", d2)]`; for `DRAFT2`: `[]`.
- `test_group_order`: dates `PARLIAMENT=2025-10-01`, `EDRAFT=2025-10-01`, `X=2025-09-01`, `Y=None`, all identical → `X, EDRAFT, PARLIAMENT, Y`.
- `test_unlabelled_in_group`: unlabelled CSV identical to `DRAFT2` → Markdown line contains `(unlabelled)` and `DRAFT2`.
- `test_note_ignores_label_selection` (Review Focus 5): through `cmd_validate --label EDRAFT` with `PARLIAMENT` on disk → the `EDRAFT` report names both.
- `test_note_does_not_affect_status`: a report with a note has the same `get_error_count()`, `get_warning_count()` and result list as without.
- `test_validate_without_config_file`: `--config` pointing at a missing file → exit code as before, note still listed (label order).

- [ ] **Step 2: Run them, expect failures**
- [ ] **Step 3: Implement**
- [ ] **Step 4: Run them, expect pass; then `pytest -q`**
- [ ] **Step 5: Commit** — `feat: report versions with identical data`

### Task 5: GDP figures for labelled versions

**Files:**
- Modify: `src/armenian_budget/ingestion/gdp_indicators.py`
- Modify: `src/armenian_budget/interfaces/cli/main.py` (`cmd_gdp_extract`, its parser)
- Modify: `skills/armenian-budget-data/scripts/data_availability.py` (only if the test below fails)
- Test: `tests/parser/test_gdp_indicators.py`, `tests/cli/test_gdp_report.py`, `tests/cli/test_data_availability_script.py`

**Interfaces — consumes:** `year_dir_name`, `dataset_stem`, `_select_versions`, `SourceDefinition.label`.

**Interfaces — produces:**
- `find_budget_law_explanatory_note_docx(original_root, extracted_root, sources_config, year, label=None)`: looks only in `budget_laws/<year_dir_name(year, label)>/` and only at the `explanatory_note` file of the entry with that label.
- `extract_gdp_snapshot(..., label: Optional[str] = None)`: a labelled snapshot carries `"label": "<LABEL>"`; an unlabelled snapshot has no `label` key, so existing files stay byte-identical.
- `gdp_snapshot_path(processed_root, year, source_type, label=None)` → `<dataset_stem>_GDP.json`; `write_gdp_snapshot` uses the snapshot's label.
- `load_gdp_snapshots` returns unlabelled snapshots only (skip any snapshot with a `label`).
- `gdp-extract` gets `--label` / `--unlabelled`; default covers the unlabelled version and every label that has a registered `explanatory_note` file for that year. Labels apply to `BUDGET_LAW` only; `SPENDING_Q1234` is unchanged.
- A labelled version with no budget message: logged as skipped, not counted as a failure.

- [ ] **Step 1: Write the failing tests**
  - `test_gdp_snapshot_path_with_label`: `2026_BUDGET_LAW_EDRAFT_GDP.json`; unlabelled unchanged.
  - `test_note_lookup_is_per_label` (Review Focus 6): config with an unlabelled 2026 entry (note `final.docx`) listed after a labelled `EDRAFT` entry (note `draft.docx`), both files on disk in their own folders → unlabelled lookup returns `budget_laws/2026/final.docx`, `label="EDRAFT"` returns `budget_laws/2026_EDRAFT/draft.docx`.
  - `test_labelled_lookup_never_falls_back`: `EDRAFT` folder has no docx, the unlabelled folder has one → `FileNotFoundError` for `label="EDRAFT"`.
  - `test_labelled_snapshot_records_label` and `test_unlabelled_snapshot_has_no_label_key`.
  - `test_load_gdp_snapshots_skips_labelled` (Review Focus 7): processed dir with `2026_BUDGET_LAW_GDP.json` and `2026_BUDGET_LAW_EDRAFT_GDP.json` → one snapshot; the rendered report is identical with and without the labelled file.
  - `test_gdp_extract_default_covers_labelled`, `test_gdp_extract_label`, `test_gdp_extract_skips_version_without_note` (exit 0 when another version succeeded).
  - `test_data_availability_ignores_labelled_gdp`: `2026_BUDGET_LAW_EDRAFT_GDP.json` and `2026_BUDGET_LAW_EDRAFT.csv` in the data root → the script still runs; the labelled CSV appears as its own column `BUDGET_LAW_EDRAFT`; no `BUDGET_LAW_EDRAFT_GDP` breakage.
- [ ] **Step 2: Run them, expect failures**
- [ ] **Step 3: Implement**
- [ ] **Step 4: Run them, expect pass; then `pytest -q`.** Regenerate the existing GDP snapshots into a scratch root (`gdp-extract --years 2019-2026 --processed-root <scratch>`) and confirm each is byte-identical to the committed one.
- [ ] **Step 5: Commit** — `feat: extract GDP figures for labelled versions`

### Task 6: Registry and packaging guards

**Files:**
- Modify: `tests/sources/test_source_config_uniqueness.py`
- Modify: `tests/packaging/test_artifacts_packaging.py`
- Modify only if a test fails: `scripts/build_artifacts.py`

- [ ] **Step 1: Shared-checksum rule.** Checksums may be shared only between entries of the same year and source type whose labels differ; URLs stay unique for every entry. Extract the rule into a function in the test module and add:
  - `test_same_year_versions_may_share_checksum`: synthetic entries `2026/budget_law/EDRAFT` and `2026/budget_law/PARLIAMENT` with one checksum → no conflict.
  - `test_other_shared_checksums_still_conflict`: same checksum across two years, across two source types, and between two entries with the same label → conflict in each case.
  - `test_shared_url_always_conflicts`: same URL on `EDRAFT` and `PARLIAMENT` → conflict.
  `config/checksums.yaml` entries have `name`, `year`, `source_type`; take the label from the `sources.yaml` entry with the same `name`.
- [ ] **Step 2: Packaging.** Add `test_processed_artifact_allowlist_includes_labelled_files`: `2026_BUDGET_LAW_EDRAFT.csv`, `_overall.json`, `_validation.json`, `_validation.md`, `_GDP.json` are all returned by `iter_processed_artifacts`, and `build_data_version` counts the CSV in `primary_csv_count`.
- [ ] **Step 3: Run `pytest tests/sources tests/packaging -q`, expect pass**
- [ ] **Step 4: Commit** — `test: allow labelled versions to share a checksum`

### Task 7: Add the known versions and dates

**Files:**
- Modify: `config/sources.yaml`, `config/checksums.yaml`, `data/extracted/discovery_index.json`
- Create/replace under `data/processed/`: see below

Entries to add. Each has two files: the annexes archive (`<name>_attachments`) and, where a budget message exists, `<name>_explanatory_note` with an explicit `filename` ending in `.docx` (e-gov serves every message as `4Uxerdz.docx`, which the extractor does not recognise by name).

| name | year | label | published | url | note |
|---|---|---|---|---|---|
| `2027_budget_law_draft` | 2027 | `DRAFT` | 2026-10-01 | `https://www.e-gov.am/ajax/gfn_mul.php?file_id=4644032&inst=1429880` | `filename: "3Orenqi havelvac.rar"`; sha256 starts `e546296dd798ca8e` |
| `2026_budget_law_edraft` | 2026 | `EDRAFT` | 2025-10-01 | `https://www.e-draft.am/files/project_file/1/17593198520182.rar` | sha256 starts `3af4834743f8b221` |
| `2026_budget_law_parliament` | 2026 | `PARLIAMENT` | from the page | `https://parliament.am/diskStorage/draft_docs8/K-1160_havelvatsner.rar` | same sha256 as `EDRAFT`; date from `https://www.parliament.am/blueprints/draft-history/15988/`, leave empty if the page shows none |
| `2026_budget_law_draft2` | 2026 | `DRAFT2` | 2025-11-27 | `https://www.e-gov.am/ajax/gfn_mul.php?file_id=4143266&inst=1289483` | set `filename` to the name in the response's `Content-Disposition`; sha256 starts `b3bdc72b2fa666cb` |
| `2025_budget_law_edraft` | 2025 | `EDRAFT` | 2024-10-02 | `https://www.e-draft.am/files/project_file/1/17278710055868.rar` | sha256 starts `734488252b701d29` |

Budget messages (the `explanatory_note` file of each entry):

| entry | url | sha256 starts |
|---|---|---|
| 2027 `DRAFT` | `https://www.e-gov.am/ajax/gfn_mul.php?file_id=4644033&inst=1429880` | `82792c23096f481c` (already saved as `4Uxerdz.docx`) |
| 2026 `EDRAFT` | `https://www.e-draft.am/files/project_doc/1/17593198520187.docx` | `d5bc483f37820691` |
| 2026 `DRAFT2` | `https://www.e-gov.am/ajax/gfn_mul.php?file_id=4143267&inst=1289483` | `403fe16e02c83a75` |
| 2025 `EDRAFT` | `https://www.e-draft.am/files/project_doc/1/17278710055878.docx` | `358206cb8616a897` |
| 2026 `PARLIAMENT` | look on the draft-history page; if there is none, register the annexes only | — |

- [ ] **Step 1: Move the saved 2027 files.** `data/original/budget_laws/2027/` holds five files saved from e-gov.am on 2026-11-22. Move the folder to `data/original/budget_laws/2027_DRAFT/` (gitignored; compare file count and sha256 before and after).
- [ ] **Step 2: Add the four entries, then run** `download`, `extract`, `process`, `validate --report --report-json` and `gdp-extract` for 2025, 2026 and 2027 through the CLI, each with `--source-type BUDGET_LAW` so no spending report is regenerated. If a site refuses the existing downloader, stop that version, leave its entry out and report it.
- [ ] **Step 3: Check against the scratch results** (sha256 prefixes of the CSVs):
  - `2026_BUDGET_LAW_EDRAFT.csv` = `ab4cc61137c2…` = the current `2026_BUDGET_LAW_DRAFT.csv`
  - `2026_BUDGET_LAW_PARLIAMENT.csv` = the same
  - `2026_BUDGET_LAW_DRAFT2.csv` = `906320af84af…` = `2026_BUDGET_LAW.csv`
  - `2027_BUDGET_LAW_DRAFT.csv` = `cb5d990e53f1…`, 823 rows, `overall_total` 4071984639.0
  - `2025_BUDGET_LAW_EDRAFT_overall.json` has `overall_total` 3482409450.9; its validation has no errors
  - Nominal GDP in the new snapshots: 2027 `DRAFT` gives 13614.0 for 2027; 2026 `EDRAFT` and `DRAFT2` give 11933.7 for 2026; 2025 `EDRAFT` gives 11050.1 for 2025
  - `2025_BUDGET_LAW.*`, `2026_BUDGET_LAW.*` (CSV, `_overall.json`, `_GDP.json`) and `gdp_report.html` unchanged
  A mismatch is a stop-and-report, not something to fix.
- [ ] **Step 4: Remove the hand-renamed draft** — `git rm data/processed/2026_BUDGET_LAW_DRAFT.csv data/processed/2026_BUDGET_LAW_DRAFT_overall.json`.
- [ ] **Step 5: Check the notes.** The `EDRAFT` and `PARLIAMENT` reports name each other; the `2026_BUDGET_LAW` and `DRAFT2` reports name `(unlabelled)` and `DRAFT2`; the 2027 report has no note.
- [ ] **Step 6: `published` for existing entries.** For each existing entry take the `Last-Modified` header of its data archive (the first file for multi-file entries; URLs with Armenian characters must be percent-encoded for the request). Record its date only inside these windows, otherwise leave the field out:
  - budget law of year Y: 1 Nov Y−1 to 31 Jan Y
  - MTEP labelled year Y: 1 Jun Y−1 to 30 Sep Y−1
  - spending Q1 / Q12 / Q123 of year Y: within 120 days after 31 Mar / 30 Jun / 30 Sep of Y
  - spending Q1234 of year Y: within 240 days after 31 Dec Y
- [ ] **Step 7: Verify the scope of the data change.** `git status --short data/ config/` shows only: the new labelled files for 2025, 2026 and 2027, the two deleted draft files, regenerated 2026 validation reports for `BUDGET_LAW` (the note only), new index keys `2025/budget_law/EDRAFT`, `2026/budget_law/EDRAFT`, `…/PARLIAMENT`, `…/DRAFT2`, `2027/budget_law/DRAFT`, and the two config files. No other existing index entry, CSV or `_overall.json` changes. Then `pytest -q`.
- [ ] **Step 8: Commit in three commits** — `feat: register 2025 to 2027 budget law drafts` (config + index), `feat!: publish labelled budget law drafts` (data/processed; body says `2026_BUDGET_LAW_DRAFT.*` is now `2026_BUDGET_LAW_EDRAFT.*`), `chore: record known publication dates`.

### Task 8: Older budget-law versions, one bounded pass

Best effort; the result may be "none added".

- [ ] **Step 1: Parliament.** For each budget law 2019–2025, open its law page on `www.parliament.am` (2025 is `/hy/legislations/3/9526`; find the others in the list at `/hy/legislations/3/`), follow "Նախագծի պատմություն" (draft history) and take the annexes archive of the draft as submitted. That is `PARLIAMENT` for that year.
- [ ] **Step 2: Apply the inclusion rule** to each candidate: downloads through the existing downloader, and `process --label PARLIAMENT` succeeds with the existing parser. Register and commit those that pass (config, index, processed files, validation reports), one commit per year: `feat: add <year> budget law parliament draft`.
- [ ] **Step 3: Do not search e-draft.am or e-gov.am for older years.** The 2025 e-draft (project 7738) is already added in Task 7.
- [ ] **Step 4: List in the final report** every year checked, what was found, and why anything was left out (not found, download refused, parse failure with the parser's message).

### Task 9: Documentation

**Files:**
- Modify: `docs/data_schemas.md` (source config fields `label` and `published`; naming `{year}_{SOURCE_TYPE}[_{LABEL}]`; folder layout; the label convention table from the spec; the identical-data note; `_GDP.json` for labelled versions and that the GDP report page shows adopted laws only; that dataset-driven tests cover unlabelled datasets only)
- Modify: `skills/armenian-budget-data/references/datasets.md` (which labelled files exist and that the unlabelled budget law is the adopted one)
- Modify: `docs/roadmap.md` (replace the "version tag" backlog item near line 132 with what was built; do not touch milestones)
- Modify: `CHANGELOG.md` under `Unreleased`, version-neutral: Added (labels, `--label`/`--unlabelled`, `published`, identical-data note, the new datasets) and Changed, marked **BREAKING** (`2026_BUDGET_LAW_DRAFT.*` renamed to `2026_BUDGET_LAW_EDRAFT.*`, data unchanged)
- Modify: CLI help text for the new options

- [ ] **Step 1: Write the docs.** Keep them short (AGENTS.md: document only what the code does not show).
- [ ] **Step 2: Run** `pytest -q`, `ruff check src/ tests/`, `black --check src/ tests/`.
- [ ] **Step 3: Commit** — `docs: document source labels`

### Task 10: Whole-branch review and report

- [ ] **Step 1:** Independent review of `dev..feat/source-labels` against the spec's Goals, Non-goals, Anti-goals and Acceptance, and this plan's Review Focus. Fix findings that break a goal or acceptance line; list the others with a reason.
- [ ] **Step 2:** Final report: commits, test totals, the Task 3 regression diff summary, the Task 7 checksum table, Task 8 findings, review findings, anything left out and why, and the exact command to merge into `dev`.

## Coordinator-owned (not part of the worker's run)

- Merge `feat/source-labels` into `dev` (`git merge --no-ff`), after the owner approves the finished branch.
- Push and release: separate approvals.
