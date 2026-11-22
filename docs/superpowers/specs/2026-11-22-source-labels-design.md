# Source labels: several versions of one document per year

Status: draft for approval. Date: 2026-11-22.

## Why

A budget law exists in several public versions before it is adopted: the
government's draft, the public-consultation copy, the draft submitted to
parliament, a revised draft, and the adopted law. Today the pipeline can hold
exactly one file per year and source type. The only draft we publish
(`2026_BUDGET_LAW_DRAFT.csv`) was renamed by hand in December 2025 and no code
knows about it. Draft files also disappear: the e-gov.am copy of the first 2026
draft is gone and could not be recovered.

We want to keep every version we can get, each parsed by the normal pipeline,
with a name that says where it came from.

## Goals

- Any source entry may carry a **label**. Entries with the same year and source
  type but different labels are separate versions, processed side by side.
- An entry without a label behaves exactly as today. For a budget law the
  unlabelled entry is the adopted law. No existing file is renamed, except the
  hand-renamed 2026 draft (see Data).
- Every labelled version goes through download, extract, discover, process and
  validate with no special path.
- A labelled budget-law version also gets its GDP figures, read from that
  version's own budget message.
- A reader can see which versions of a year hold identical data.
- Each source can record when it was published.

## Non-goals

- `same_as` or any other way to skip parsing a version. Rejected: it needs
  ordering, a comparison step and a config entry with no output. Identical
  versions are simply parsed twice.
- Ordering versions by label. Labels are opaque. `DRAFT2` (27 Nov 2025) is
  later than `EDRAFT` (1 Oct 2025), so label names do not sort by time.
- A new downloader, scraper or site-specific client. Sources are plain URLs in
  `sources.yaml`, fetched by the existing downloader.
- Drafts on the GDP report page. `gdp_report.html` keeps showing unlabelled
  snapshots only.
- A separate backup of originals. The workspace backup covers `data/original/`.
- Replacing the 2026 adopted-law source with parliament's signed copy. Its
  parsed workbook has the same cell values as the current source (1,023 rows,
  0 differences, checked 2026-11-22).
- Recovering lost files or dates with real effort. If a version or a date is
  not easily found, it is left out.

## Anti-goals

- Any change to the bytes of existing unlabelled outputs.
- A label enum in code. A new label must need no code change.
- A version that exists in config but silently produces nothing.

## Decided design

### Config (`config/sources.yaml`)

Two optional fields on a source entry (entry level, shared by its `files`):

```yaml
- name: "2026_budget_law_edraft"
  year: 2026
  source_type: "budget_law"
  label: "EDRAFT"
  published: 2025-10-01
  description: "2026 budget law draft, public consultation copy (e-draft.am project 9166)"
  files: [...]
```

- `label`: matches `^[A-Z0-9]+$`. `GDP` is reserved (it would collide with
  `{year}_{SOURCE_TYPE}_GDP.json`). An invalid or reserved label, or two
  entries with the same year, source type and label but different names, is a
  load error.
- `published`: ISO date. Meaning: **the best evidence of the date the file
  first appeared on that site.** Display only. It never affects file names,
  parsing or which version is "final". An invalid date is a load error.

### Label convention (documentation, not code)

A label names the site a version came from, plus a number for later revisions
on that site.

| Label | Site | Meaning for a budget law |
|---|---|---|
| `DRAFT`, `DRAFT2`, … | e-gov.am | Draft on a government session agenda; `DRAFT2` is the revised draft |
| `EDRAFT`, … | e-draft.am | Public-consultation copy |
| `PARLIAMENT`, … | parliament.am | Draft as submitted to parliament (not the adopted law) |
| *(none)* | minfin.am | Adopted law |

### Outputs

`{year}_{SOURCE_TYPE}[_{LABEL}].csv`, and the same insertion for
`_overall.json`, `_validation.md`, `_validation.json` and `_GDP.json`. Example:
`2026_BUDGET_LAW_EDRAFT.csv`, `2026_BUDGET_LAW_EDRAFT_validation.md`,
`2026_BUDGET_LAW_EDRAFT_GDP.json`.

### Pipeline behaviour

- **Default covers everything.** `download`, `extract`, `discover`, `process`
  and `validate` handle the unlabelled version and every labelled version for
  the requested years and source types. Two new options narrow a run:
  `--label LABEL` selects that one version, and `--unlabelled` selects only
  the unlabelled one.
- **GDP.** `gdp-extract` covers labelled budget-law versions the same way
  (default all, `--label`, `--unlabelled`). Each version reads the budget
  message registered in its own entry, from its own folder; it never falls
  back to another version's file. A version without a budget message gets no
  GDP file, and that is reported, not an error. The GDP snapshot of a labelled
  version records its label.
- **A registered version that fails** is reported the way a failing dataset is
  today (`FAIL` in the processing report, same exit-code rules). Nothing new.
- **Versions never mix on disk.** Each labelled version has its own folder
  under `data/original/` and `data/extracted/`, and discovery for one version
  must never select a workbook belonging to another. Today discovery searches
  `budget_laws/{year}` recursively, so this needs an explicit test.
- **Identical-data note.** When validation runs, the CSVs of the same year and
  source type are compared by checksum. If a version's CSV is identical to
  others, its validation report (Markdown and JSON) carries one line listing
  the whole group, itself included, for example
  `Identical data: EDRAFT (2025-10-01), PARLIAMENT (2025-10-01)`. The group is
  ordered by `published`, oldest first, ties by label; versions without a date
  come last and show no date. The unlabelled version is shown as
  `(unlabelled)`. This note is the only output that shows `published`; it is
  not added to report headers, `DATA_VERSION.json` or any other file. The note is information, not a check: it never
  passes, fails or changes counts.
- **Shared checksums.** `tests/sources/test_source_config_uniqueness.py`
  forbids two entries sharing an archive checksum. Versions of the same year
  and source type with different labels are allowed to share one (2026
  `EDRAFT` and `PARLIAMENT` are the same bytes). URLs stay unique for every
  entry.

## Approaches considered

1. **Label as part of the source identity, every version fully processed**
   (chosen). No special cases after the registry; identity is observed from
   the outputs.
2. **`same_as` references between versions.** Rejected, see Non-goals. Also
   shown to be fragile: for 2026 the adopted-law data exists in three
   publications whose archives differ, and in one case the workbook bytes
   differ, while the values are the same.
3. **A new source type per version** (`BUDGET_LAW_DRAFT` in the enum).
   Rejected: every new label would need a code change and its own schema and
   validation wiring.

## Calls made by the author (not discussed with the owner)

- The field is named `label`, not `version` as the old roadmap note says.
  "Version" already means the package and data release version here.
- On-disk layout: the year folder takes the label suffix, mirroring the file
  names: `budget_laws/2026_EDRAFT/` beside `budget_laws/2026/`. The builder may
  choose another layout if it keeps unlabelled paths unchanged and passes the
  isolation test.
- Discovery index key for a labelled version: `{year}/{source_type}/{LABEL}`.
  Existing keys are unchanged.
- The identical-data note lives in the validation report, not in a new file.
- `published` is set per entry, not per file, and is shown only in that note.
- `--unlabelled` exists so a run can still target the adopted law alone.
- The dataset-driven tests (`tests/conftest.py` finds `{year}_{SOURCE_TYPE}.csv`)
  keep covering unlabelled datasets only. Labelled datasets are covered by
  their validation reports. This is a known limit of this work.

## Data to add with this work

Verified on 2026-11-22 unless noted. "Parses" means the annexes archive was
extracted in scratch and the workbook run through the existing parser. "GDP
reads" means the existing GDP extractor read that version's budget message.

**One rule for every version, in every year:** it is registered in
`sources.yaml` only if it downloads through the existing downloader and parses
with the existing parser unchanged. Anything else is listed in the report and
left out. The same holds for its GDP file: produced only if the budget message
downloads and the existing extractor reads it.

| Year | Label | Source | Published | State |
|---|---|---|---|---|
| 2027 | `DRAFT` | e-gov.am, session of 1 Oct 2026, `inst=1429880` | 2026-10-01 | Live. Parses: 823 rows, total 4,071,984,639.0. GDP reads. Five files already saved in `data/original/budget_laws/2027/` (move to the labelled folder) |
| 2026 | `EDRAFT` | e-draft.am project 9166 | 2025-10-01 | Live. Parses; the CSV is byte-identical to today's `2026_BUDGET_LAW_DRAFT.csv`. GDP reads |
| 2026 | `PARLIAMENT` | `parliament.am/diskStorage/draft_docs8/K-1160_havelvatsner.rar` | to be read from the draft-history page | Live. Archive byte-identical to `EDRAFT`. Budget message not looked for yet |
| 2026 | `DRAFT2` | e-gov.am, session of 27 Nov 2025, `file_id=4143266&inst=1289483` | 2025-11-27 | Live. Parses; the CSV is byte-identical to `2026_BUDGET_LAW.csv`. GDP reads |
| 2025 | `EDRAFT` | e-draft.am project 7738 | 2024-10-02 | Live. Parses since the parser fix `160cf3a` (on `dev`): total 3,482,409,450.9. GDP reads |

- `2026_BUDGET_LAW_DRAFT.csv` and `_overall.json` are replaced by
  `2026_BUDGET_LAW_EDRAFT.*`, produced by the pipeline. The data does not
  change, only the name. This renames a released file and is a breaking change
  for users of that file.
- There is no 2026 `DRAFT`: the first e-gov draft (25 Sep 2025) is lost.
- GDP figures seen in scratch: the 2026 `EDRAFT` and `DRAFT2` messages give the
  same nominal-GDP series as the adopted 2026 law. The 2025 `EDRAFT` differs
  from the adopted 2025 law (2025: 11,050.1 against 10,891.5 bn dram).
- **Older years, best effort.** One pass over parliament.am and e-draft.am for
  the 2019–2025 budget laws, under the rule above. e-draft's search does not
  filter; projects were found by scanning project numbers.
- **`published` for existing entries, best effort.** The server's
  `Last-Modified` is available for most minfin links and is usually right
  (2025 budget law: 5 Dec 2024). Fill it in where it is plausible. Leave it
  empty where it is clearly a re-upload (for example 2021 Q1 shows 7 Oct 2024)
  or missing.
- Validation reports are regenerated only for years that gain a version.
  Validation failures in drafts are reported, not fixed.

## Left to the builder

- How commands enumerate the versions of a year (from `sources.yaml` or from
  folders), and the internal representation of a version.
- Per-site download details (`filename` for e-gov links, request headers). If
  a site cannot be fetched by the existing downloader, stop and report; do not
  add a client.
- Whether a labelled version needs a discovery pattern in
  `config/parsers.yaml`. The global pattern selected the right workbook for
  the four versions above.
- Wording of the docs: label convention and naming in `docs/data_schemas.md`,
  the `armenian-budget-data` skill's dataset reference, the roadmap backlog
  item this delivers (replace it with what was built), and a version-neutral
  `Unreleased` changelog entry that names the rename as breaking.

## Acceptance

- With no labelled entries in config, every command behaves as before and the
  full test suite passes.
- After the data step, `git status` under `data/processed/` shows only: new
  labelled files, the 2026 draft rename, and regenerated validation reports
  for the affected years. No unlabelled CSV or `_overall.json` changes.
- Tests cover: label and date validation in the registry; output names;
  discovery isolation in both directions; default runs covering all versions
  and `--label` restricting to one; the identical-data note (grouping, order,
  undated last, absent when nothing matches); the shared-checksum rule; and
  the release artifact allowlist including labelled files.
- The 2026 report for `EDRAFT` names `EDRAFT` and `PARLIAMENT` as identical,
  and the report for the adopted law names `(unlabelled)` and `DRAFT2`.

## Amendments after the first build (owner feedback, 2026-11-22)

These override anything above that says otherwise.

1. **`sources.yaml` is the list of labelled versions.** A labelled version
   exists only if it is registered. Commands take labelled versions from the
   registry, never from folders. A labelled folder on disk with no entry
   (`2020_PARLIAMENT` today) is skipped with one warning naming it, and nothing
   is written for it. Nothing on disk is deleted. The unlabelled version is
   found as before. This replaces "Left to the builder: how commands enumerate
   the versions".
2. **XML spreadsheets are read.** Some workbooks are Excel 2003 XML
   ("SpreadsheetML") saved with an `.xls` name; pandas cannot open them. They
   are read by a small standard-library reader, no new dependency. Every other
   file is read exactly as before. This lifts "existing parser unchanged" for
   this one case; outputs of all existing datasets must stay byte-identical.
3. **Revised parliament drafts are added as `PARLIAMENT2`.** The annexes
   parliament.am publishes for the second reading (file names with `lr`).
   Further revisions would be `PARLIAMENT3`, and so on.
4. **PDF sources are a documented limit, not work.** No PDF reading. Listed
   under known limitations in the docs: the 2020 `PARLIAMENT` programme table
   (PDF only), the budget message of every `PARLIAMENT`/`PARLIAMENT2` version
   (PDF only, so no GDP file), and 2019 (no draft history on parliament.am).

Measured in scratch on 2026-11-22 (existing parser; the 2021 `PARLIAMENT`
workbook through a 25-line XML reader, script in the plan):

| Year | Label | Archive | Result |
|---|---|---|---|
| 2021 | `PARLIAMENT` | `draft_docs7/K-752/K-752_orenqi_havelvacner.rar` | XML workbook. 746 rows, total 1,843,133,616.39, 0 errors |
| 2020 | `PARLIAMENT2` | `draft_docs7/K-306lr_havelvatsner.rar` | 802 rows; CSV byte-identical to `2020_BUDGET_LAW.csv` |
| 2021 | `PARLIAMENT2` | `draft_docs7/K-752lr/K-752lr_orenq_havelvacner.rar` | 752 rows; identical to `2021_BUDGET_LAW.csv` |
| 2022 | `PARLIAMENT2` | `draft_docs8/K-059lr_havelvatsner.rar` | 801 rows; identical to `2022_BUDGET_LAW.csv` |
| 2023 | `PARLIAMENT2` | `draft_docs8/K-382lr_orenqi_havelvatsner.rar` | 853 rows; identical to `2023_BUDGET_LAW.csv` |
| 2024 | `PARLIAMENT2` | `draft_docs8/K-669lr_havelvatsner.rar` | 857 rows; identical to `2024_BUDGET_LAW.csv` |
| 2025 | `PARLIAMENT2` | `draft_docs8/K-932lr_havelvatsner.rar` | 827 rows; identical to `2025_BUDGET_LAW.csv` |
| 2026 | `PARLIAMENT2` | `draft_docs8/K-1160lr_havelvatsner.rar` | Archive byte-identical to `DRAFT2`; CSV identical to `2026_BUDGET_LAW.csv` |

All URLs are under `https://parliament.am/diskStorage/`. Every revised draft
holds the same data as the adopted law of its year.
