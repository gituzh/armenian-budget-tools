"""Extract GDP and macro indicator tables from budget source documents."""

from __future__ import annotations

import csv
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any
from urllib.parse import unquote
from zipfile import ZipFile

from armenian_budget.sources.registry import SourceRegistry


WORD_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
MACRO_DOC_RE = re.compile(r"Մակրոտնտեսական.*հարկաբյուջետային.*ցուց", re.IGNORECASE)
YEAR_RE = re.compile(r"(20\d{2})")
GDP_SOURCE_TYPES = ("BUDGET_LAW", "SPENDING_Q1234")
SPENDING_GDP_BUDGET_STATUSES = {"պետական բյուջե", "ծրագիր", "կանխ.", "սպասում"}


@dataclass(frozen=True)
class MacroIndicatorRecord:
    report_year: int
    target_year: int
    scenario: str
    indicator: str
    unit: str
    value: float | None
    source_path: str


@dataclass(frozen=True)
class DocxTable:
    table_index: int
    rows: list[list[str]]
    preceding_paragraphs: list[str]


def find_macro_indicator_docx(extracted_root: Path, report_year: int) -> Path:
    """Find the annual macro/fiscal indicators DOCX for a report year."""

    year_root = extracted_root / "spending_reports" / str(report_year) / "Q1234"
    if not year_root.exists():
        raise FileNotFoundError(f"annual spending report not extracted: {year_root}")

    candidates = [
        path
        for path in year_root.rglob("*.docx")
        if not path.name.startswith("~$") and MACRO_DOC_RE.search(path.name)
    ]
    if not candidates:
        raise FileNotFoundError(f"macro/fiscal indicators DOCX not found for {report_year}")
    if len(candidates) > 1:
        candidates.sort(key=lambda path: (len(path.parts), str(path)))
    return candidates[0]


def find_budget_law_explanatory_note_docx(
    original_root: Path,
    extracted_root: Path,
    sources_config: Path,
    year: int,
) -> Path:
    """Find the budget-law explanatory note DOCX configured for a year."""

    expected_filename = _configured_explanatory_note_filename(sources_config, year)
    candidates: list[Path] = []
    if expected_filename:
        candidates.extend(
            [
                original_root / "budget_laws" / str(year) / expected_filename,
                extracted_root / "budget_laws" / str(year) / expected_filename,
            ]
        )
    for candidate in candidates:
        if candidate.exists() and candidate.suffix.lower() == ".docx":
            return candidate

    year_roots = [
        original_root / "budget_laws" / str(year),
        extracted_root / "budget_laws" / str(year),
    ]
    fallback_candidates: list[Path] = []
    for year_root in year_roots:
        if not year_root.exists():
            continue
        fallback_candidates.extend(
            path
            for path in year_root.rglob("*.docx")
            if not path.name.startswith("~$")
            and ("բացատրագիր" in path.name or "ուղերձ" in path.name)
        )
    if fallback_candidates:
        fallback_candidates.sort(key=lambda path: (len(path.parts), str(path)))
        return fallback_candidates[0]

    if expected_filename and Path(expected_filename).suffix.lower() != ".docx":
        raise ValueError(
            f"budget-law explanatory note is not DOCX for {year}: {expected_filename}"
        )
    raise FileNotFoundError(f"budget-law explanatory note DOCX not found for {year}")


def extract_macro_indicators_from_docx(
    docx_path: Path, report_year: int
) -> list[MacroIndicatorRecord]:
    """Extract the macro/fiscal indicators table from one annual report DOCX."""

    rows = _find_indicator_table(_read_docx_tables(docx_path))
    if not rows:
        raise ValueError(f"macro/fiscal indicators table not found: {docx_path}")

    headers = rows[0][1:]
    records: list[MacroIndicatorRecord] = []
    for row in rows[1:]:
        if not row or not row[0].strip():
            continue
        indicator, unit = _split_indicator_and_unit(row[0])
        for header, raw_value in zip(headers, row[1:]):
            target_year = _parse_year(header)
            if target_year is None:
                continue
            records.append(
                MacroIndicatorRecord(
                    report_year=report_year,
                    target_year=target_year,
                    scenario=_parse_scenario(header),
                    indicator=indicator,
                    unit=unit,
                    value=_parse_number(raw_value),
                    source_path=str(docx_path),
                )
            )
    return records


def extract_gdp_snapshot(
    *,
    year: int,
    source_type: str,
    original_root: Path,
    extracted_root: Path,
    sources_config: Path,
) -> dict[str, Any]:
    """Extract one GDP/macro indicator JSON snapshot."""

    normalized_source_type = source_type.upper()
    if normalized_source_type == "BUDGET_LAW":
        docx_path = find_budget_law_explanatory_note_docx(
            original_root,
            extracted_root,
            sources_config,
            year,
        )
        table = _find_budget_law_gdp_table(_read_docx_table_blocks(docx_path))
        if table is None:
            raise ValueError(f"budget-law GDP table not found: {docx_path.name}")
        rows = table.rows
        records = _budget_law_gdp_records(rows, year)
        caption = _table_caption(table)
        table_title = _caption_title(caption)
        table_index = table.table_index
    elif normalized_source_type == "SPENDING_Q1234":
        docx_path = find_macro_indicator_docx(extracted_root, year)
        table = _find_spending_gdp_table(_read_docx_table_blocks(docx_path))
        if table is None:
            raise ValueError(f"spending-report GDP table not found: {docx_path.name}")
        rows = table.rows
        records = _spending_gdp_records(rows)
        caption = _table_caption(table)
        table_title = _caption_title(caption)
        table_index = table.table_index
    else:
        raise ValueError(f"unsupported GDP source type: {source_type}")

    return {
        "year": year,
        "source_type": normalized_source_type,
        "metric_set": "GDP",
        "source_file": docx_path.name,
        "tables": [
            {
                "caption": caption,
                "table_title": table_title,
                "table_index": table_index,
                "records": records,
            }
        ],
    }


def write_gdp_snapshot(snapshot: dict[str, Any], processed_root: Path) -> Path:
    """Write one GDP JSON snapshot using the processed-data naming convention."""

    output_path = gdp_snapshot_path(
        processed_root,
        int(snapshot["year"]),
        str(snapshot["source_type"]),
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as json_file:
        json.dump(snapshot, json_file, ensure_ascii=False, indent=2)
        json_file.write("\n")
    return output_path


def gdp_snapshot_path(processed_root: Path, year: int, source_type: str) -> Path:
    return processed_root / f"{year}_{source_type.upper()}_GDP.json"


def load_gdp_snapshots(
    processed_root: Path,
    years: list[int] | None = None,
    source_type: str | None = None,
) -> list[dict[str, Any]]:
    """Load GDP JSON snapshots from processed outputs."""

    years_set = set(years) if years else None
    source_type_upper = source_type.upper() if source_type else None
    snapshots: list[dict[str, Any]] = []
    for path in sorted(processed_root.glob("*_GDP.json")):
        try:
            with path.open("r", encoding="utf-8") as json_file:
                snapshot = json.load(json_file)
        except (OSError, ValueError, TypeError):
            continue
        if years_set is not None and int(snapshot.get("year", 0)) not in years_set:
            continue
        if source_type_upper and snapshot.get("source_type") != source_type_upper:
            continue
        snapshots.append(snapshot)
    snapshots.sort(key=_gdp_snapshot_display_key)
    return snapshots


def write_gdp_html_report(snapshots: list[dict[str, Any]], output_path: Path) -> None:
    """Write a colored HTML review report for GDP snapshots."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as html_file:
        html_file.write(_render_gdp_html(snapshots))


def extract_macro_indicator_history(
    extracted_root: Path, years: list[int]
) -> tuple[list[MacroIndicatorRecord], list[str]]:
    """Extract all available annual macro indicator tables for the requested years."""

    records: list[MacroIndicatorRecord] = []
    warnings: list[str] = []
    for year in years:
        try:
            docx_path = find_macro_indicator_docx(extracted_root, year)
            records.extend(extract_macro_indicators_from_docx(docx_path, year))
        except (FileNotFoundError, ValueError) as exc:
            warnings.append(f"{year}: {exc}")
    return records, warnings


def write_macro_indicator_csv(records: list[MacroIndicatorRecord], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "report_year",
        "target_year",
        "scenario",
        "indicator",
        "unit",
        "value",
        "source_path",
    ]
    with output_path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            row = {
                "report_year": record.report_year,
                "target_year": record.target_year,
                "scenario": record.scenario,
                "indicator": record.indicator,
                "unit": record.unit,
                "value": "" if record.value is None else record.value,
                "source_path": record.source_path,
            }
            writer.writerow(row)


def _read_docx_tables(docx_path: Path) -> list[list[list[str]]]:
    with ZipFile(docx_path) as archive:
        document_xml = archive.read("word/document.xml")

    root = ET.fromstring(document_xml)
    tables: list[list[list[str]]] = []
    for table in root.findall(".//w:tbl", WORD_NS):
        rows: list[list[str]] = []
        for table_row in table.findall("./w:tr", WORD_NS):
            cells = []
            for table_cell in table_row.findall("./w:tc", WORD_NS):
                text = " ".join(
                    text_node.text or ""
                    for text_node in table_cell.findall(".//w:t", WORD_NS)
                )
                cells.append(_clean_text(text))
            rows.append(cells)
        tables.append(rows)
    return tables


def _read_docx_table_blocks(docx_path: Path) -> list[DocxTable]:
    with ZipFile(docx_path) as archive:
        document_xml = archive.read("word/document.xml")

    root = ET.fromstring(document_xml)
    body = root.find("w:body", WORD_NS)
    if body is None:
        return []

    tables: list[DocxTable] = []
    preceding_paragraphs: list[str] = []
    table_index = 0
    for child in body:
        tag = child.tag.rsplit("}", 1)[-1]
        if tag == "p":
            text = _element_text(child)
            if text:
                preceding_paragraphs.append(text)
                preceding_paragraphs = preceding_paragraphs[-10:]
        elif tag == "tbl":
            rows: list[list[str]] = []
            for table_row in child.findall("./w:tr", WORD_NS):
                cells = [
                    _element_text(table_cell)
                    for table_cell in table_row.findall("./w:tc", WORD_NS)
                ]
                rows.append(cells)
            tables.append(
                DocxTable(
                    table_index=table_index,
                    rows=rows,
                    preceding_paragraphs=list(preceding_paragraphs),
                )
            )
            table_index += 1
    return tables


def _find_indicator_table(tables: list[list[list[str]]]) -> list[list[str]]:
    for table in tables:
        joined = "\n".join(" | ".join(row) for row in table)
        if "Անվանական ՀՆԱ" in joined and "ՀՆԱ-ի իրական աճ" in joined:
            return table
    return []


def _find_spending_gdp_table(tables: list[DocxTable]) -> DocxTable | None:
    for table in tables:
        joined = "\n".join(" | ".join(row) for row in table.rows)
        if "Անվանական ՀՆԱ" in joined and "ՀՆԱ-ի իրական աճ" in joined:
            return table
    return None


def _find_budget_law_gdp_table(tables: list[DocxTable]) -> DocxTable | None:
    for table in tables:
        joined = "\n".join(" | ".join(row) for row in table.rows)
        if (
            "Հիմնական մակրոտնտեսական ցուցանիշներ" in joined
            and "Անվանական ՀՆԱ" in joined
            and ("Տնտեսական աճ" in joined or "ՀՆԱ-ի իրական աճ" in joined)
        ):
            return table
    return None


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _element_text(element: ET.Element) -> str:
    return _clean_text(
        " ".join(text_node.text or "" for text_node in element.findall(".//w:t", WORD_NS))
    )


def _parse_year(header: str) -> int | None:
    match = YEAR_RE.search(header.replace(" ", ""))
    return int(match.group(1)) if match else None


def _parse_scenario(header: str) -> str:
    normalized = header.replace(" ", "")
    if "պետականբյուջե" in normalized:
        return "budget_plan"
    if "փաստ" in normalized:
        return "actual"
    return "history"


def _parse_status_label(header: str) -> str:
    normalized = header.replace(" ", "").lower()
    if "պետականբյուջե" in normalized:
        return "պետական բյուջե"
    if "սպասում" in normalized:
        return "սպասում"
    if "ծրագիր" in normalized:
        return "ծրագիր"
    if "կանխ" in normalized:
        return "կանխ."
    if "փաստ" in normalized:
        return "փաստ"
    return "պատմական"


def _split_indicator_and_unit(label: str) -> tuple[str, str]:
    if "," not in label:
        return label.strip(), ""
    indicator, unit = label.rsplit(",", 1)
    return indicator.strip(), unit.strip()


def _parse_number(value: str) -> float | None:
    cleaned = value.replace("\u00a0", " ").strip()
    if not cleaned or cleaned in {"...", "…", "-"}:
        return None
    negative = cleaned.startswith("(") and cleaned.endswith(")")
    cleaned = cleaned.strip("()")
    cleaned = cleaned.replace(",", "").replace(" ", "")
    try:
        number = float(cleaned)
    except ValueError:
        return None
    return -number if negative else number


def _budget_law_gdp_records(rows: list[list[str]], snapshot_year: int) -> list[dict[str, Any]]:
    if len(rows) < 2:
        return []

    year_header_index = _budget_law_year_header_index(rows)
    if year_header_index is None:
        return []

    years = [_parse_year(cell) for cell in rows[year_header_index][1:]]
    records: list[dict[str, Any]] = []
    for row in rows[year_header_index + 1 :]:
        if len(row) < 2 or not row[0].strip():
            continue
        if not any(_parse_number(value) is not None for value in row[1:]):
            continue
        indicator, unit = _split_indicator_and_unit(row[0])
        for target_year, raw_value in zip(years, row[1:]):
            if target_year is None:
                continue
            records.append(
                {
                    "target_year": target_year,
                    "status": _budget_law_status(target_year, snapshot_year),
                    "indicator": indicator,
                    "unit": unit,
                    "value": _parse_number(raw_value),
                }
            )
    return records


def _budget_law_year_header_index(rows: list[list[str]]) -> int | None:
    best_index: int | None = None
    best_year_count = 0
    for index, row in enumerate(rows[:4]):
        year_count = sum(1 for cell in row[1:] if _parse_year(cell) is not None)
        if year_count > best_year_count:
            best_index = index
            best_year_count = year_count
    return best_index if best_year_count > 0 else None


def _budget_law_status(target_year: int, snapshot_year: int) -> str:
    if target_year < snapshot_year - 1:
        return "փաստ"
    if target_year == snapshot_year - 1:
        return "սպասում"
    if target_year == snapshot_year:
        return "ծրագիր"
    return "կանխ."


def _spending_gdp_records(rows: list[list[str]]) -> list[dict[str, Any]]:
    if not rows:
        return []

    headers = rows[0][1:]
    records: list[dict[str, Any]] = []
    for row in rows[1:]:
        if len(row) < 2 or not row[0].strip():
            continue
        indicator, unit = _split_indicator_and_unit(row[0])
        for header, raw_value in zip(headers, row[1:]):
            target_year = _parse_year(header)
            if target_year is None:
                continue
            records.append(
                {
                    "target_year": target_year,
                    "status": _parse_status_label(header),
                    "indicator": indicator,
                    "unit": unit,
                    "value": _parse_number(raw_value),
                }
            )
    return records


def _configured_explanatory_note_filename(
    sources_config: Path,
    year: int,
) -> str | None:
    registry = SourceRegistry(sources_config)
    for source in registry.filter(year=year, source_types=["budget_law"]):
        if "explanatory_note" not in source.name:
            continue
        if source.filename:
            return Path(source.filename).name
        if source.url:
            return _source_url_filename(source.url)
    return None


def _source_url_filename(url: str) -> str:
    filename = url.split("?", 1)[0].rstrip("/").split("/")[-1]
    return unquote(filename)


def _table_caption(table: DocxTable) -> str:
    for paragraph in reversed(table.preceding_paragraphs):
        if "Աղյուսակ" in paragraph:
            return paragraph
    return ""


def _caption_title(caption: str) -> str:
    return re.sub(r"^Աղյուսակ\s*\S+\s*\.?\s*", "", caption).strip()


def _render_gdp_html(snapshots: list[dict[str, Any]]) -> str:
    explorer = _render_nominal_gdp_explorer(snapshots)
    table = _render_nominal_gdp_report_table(snapshots)
    return f"""<!doctype html>
<html lang="hy">
<head>
  <meta charset="utf-8">
  <title>GDP report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #1f2933; }}
    h1 {{ font-size: 24px; margin: 0 0 24px; }}
    h2 {{ font-size: 18px; margin: 28px 0 6px; }}
    .meta {{ color: #5c6b73; font-size: 13px; margin: 0 0 12px; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 28px; font-size: 13px; }}
    th, td {{ border: 1px solid #d7dee3; padding: 7px 8px; vertical-align: top; }}
    th {{ background: #f4f7f9; text-align: left; position: sticky; top: 0; }}
    td.num {{ text-align: right; white-space: nowrap; }}
    .status {{ display: block; color: #52616a; font-size: 11px; margin-top: 2px; }}
    .status-actual {{ background: #edf7ed; }}
    .status-expected {{ background: #fff7df; }}
    .status-planned {{ background: #eaf3ff; }}
    .status-forecast {{ background: #f1ecfa; }}
    .status-history {{ background: #f7f8fa; }}
    .missing {{ color: #9aa5ad; }}
    .source {{ min-width: 150px; font-weight: 600; }}
    .file {{ color: #5c6b73; font-size: 12px; max-width: 320px; overflow-wrap: anywhere; }}
    .cell-value {{ border-radius: 4px; display: block; margin: 2px 0; padding: 4px 5px; }}
    .gdp-explorer {{
      border: 1px solid #d7dee3;
      margin: 0 0 28px;
      padding: 16px;
    }}
    .gdp-explorer h2 {{ margin-top: 0; }}
    .chart-wrap {{ overflow-x: auto; }}
    .gdp-chart {{ display: block; min-width: 760px; width: 100%; height: 420px; }}
    .series-line {{ fill: none; stroke-width: 2.2; opacity: 0.24; }}
    .series-point {{ stroke: #ffffff; stroke-width: 1.4; opacity: 0.36; }}
    .series-active .series-line {{ opacity: 1; stroke-width: 3.2; }}
    .series-active .series-point {{ opacity: 1; }}
    .series-muted .series-line {{ opacity: 0.09; }}
    .series-muted .series-point {{ opacity: 0.14; }}
    .axis {{ stroke: #9aa5ad; stroke-width: 1; }}
    .grid {{ stroke: #e7ecef; stroke-width: 1; }}
    .tick {{ fill: #52616a; font-size: 12px; }}
    .chart-note {{ fill: #52616a; font-size: 12px; }}
    .chart-controls {{
      align-items: center;
      border-top: 1px solid #d7dee3;
      display: flex;
      gap: 8px;
      margin-top: 12px;
      padding-top: 12px;
    }}
    .chart-controls button {{
      background: #ffffff;
      border: 1px solid #bcccdc;
      color: #243b53;
      cursor: pointer;
      font-size: 18px;
      height: 32px;
      line-height: 1;
      width: 36px;
    }}
    .chart-controls button:hover {{ background: #f4f7f9; }}
    .chart-controls button:focus {{ outline: 2px solid #627d98; outline-offset: 2px; }}
    .chart-current {{ font-size: 13px; font-weight: 700; min-width: 180px; }}
    .detail-panel {{
      display: grid;
      gap: 12px;
      grid-template-columns: minmax(180px, 260px) 1fr;
      margin-top: 12px;
      padding-top: 12px;
    }}
    .detail-title {{ font-weight: 700; margin-bottom: 4px; }}
    .detail-file {{ color: #5c6b73; font-size: 12px; overflow-wrap: anywhere; }}
    .detail-values {{ display: flex; flex-wrap: wrap; gap: 6px; }}
    .detail-value {{ border-radius: 4px; padding: 5px 7px; font-size: 12px; }}
    .detail-year {{ font-weight: 700; margin-right: 4px; }}
    tr[data-series-id] {{ cursor: pointer; }}
    tr[data-series-id]:hover {{ background: #f8fafc; }}
    tr[data-series-id]:focus {{ outline: 2px solid #627d98; outline-offset: -2px; }}
    tr.is-selected {{ background: #eef5fb; outline: 2px solid #334e68; outline-offset: -2px; }}
  </style>
</head>
<body>
  <h1>GDP report</h1>
  {explorer}
  {table}
</body>
</html>
"""


def _render_nominal_gdp_explorer(snapshots: list[dict[str, Any]]) -> str:
    series = _nominal_gdp_series(snapshots)
    if not series:
        return ""

    payload = json.dumps(series, ensure_ascii=False).replace("</", "<\\/")
    return f"""
  <section class="gdp-explorer" aria-label="Nominal GDP source snapshot explorer">
    <h2>Nominal GDP source snapshots</h2>
    <p class="meta">Use the controls below the chart or a table row to inspect one source while keeping every snapshot visible.</p>
    <div class="chart-wrap">
      <svg id="gdp-chart" class="gdp-chart" viewBox="0 0 960 420" role="img" aria-label="Nominal GDP values by source snapshot"></svg>
    </div>
    <div class="chart-controls" aria-label="Nominal GDP source controls">
      <button type="button" id="gdp-prev" aria-label="Previous source">↑</button>
      <button type="button" id="gdp-next" aria-label="Next source">↓</button>
      <span id="gdp-current" class="chart-current"></span>
    </div>
    <div id="gdp-detail" class="detail-panel" aria-live="polite"></div>
  </section>
  <script id="gdp-series-data" type="application/json">{payload}</script>
  <script>
  (() => {{
    const series = JSON.parse(document.getElementById("gdp-series-data").textContent);
    const svg = document.getElementById("gdp-chart");
    const detail = document.getElementById("gdp-detail");
    const current = document.getElementById("gdp-current");
    const prev = document.getElementById("gdp-prev");
    const next = document.getElementById("gdp-next");
    const ns = "http://www.w3.org/2000/svg";
    const width = 960;
    const height = 420;
    const margin = {{ top: 24, right: 28, bottom: 48, left: 72 }};
    const plotWidth = width - margin.left - margin.right;
    const plotHeight = height - margin.top - margin.bottom;
    const years = [...new Set(series.flatMap((item) => item.records.map((record) => record.year)))].sort((a, b) => a - b);
    const values = series.flatMap((item) => item.records.map((record) => record.value));
    const minYear = Math.min(...years);
    const maxYear = Math.max(...years);
    const minValue = Math.min(...values);
    const maxValue = Math.max(...values);
    const yPad = Math.max((maxValue - minValue) * 0.08, 100);
    const yMin = minValue - yPad;
    const yMax = maxValue + yPad;
    const colors = {{ BUDGET_LAW: "#2f6f9f", SPENDING_Q1234: "#8a5a9e" }};
    const statusColors = {{
      "փաստ": "#2f855a",
      "սպասում": "#b7791f",
      "ծրագիր": "#2b6cb0",
      "պետական բյուջե": "#2b6cb0",
      "կանխ.": "#805ad5"
    }};

    function xScale(year) {{
      if (maxYear === minYear) return margin.left + plotWidth / 2;
      return margin.left + ((year - minYear) / (maxYear - minYear)) * plotWidth;
    }}

    function yScale(value) {{
      return margin.top + ((yMax - value) / (yMax - yMin)) * plotHeight;
    }}

    function createSvg(name, attrs = {{}}, text = "") {{
      const node = document.createElementNS(ns, name);
      Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value));
      if (text) node.textContent = text;
      return node;
    }}

    function formatNumber(value) {{
      return new Intl.NumberFormat("en-US", {{ maximumFractionDigits: 1 }}).format(value);
    }}

    function pathFor(records) {{
      return records
        .map((record, index) => `${{index === 0 ? "M" : "L"}} ${{xScale(record.year)}} ${{yScale(record.value)}}`)
        .join(" ");
    }}

    function drawAxes() {{
      const yTicks = 5;
      for (let index = 0; index <= yTicks; index += 1) {{
        const value = yMin + ((yMax - yMin) * index) / yTicks;
        const y = yScale(value);
        svg.appendChild(createSvg("line", {{ class: "grid", x1: margin.left, x2: width - margin.right, y1: y, y2: y }}));
        svg.appendChild(createSvg("text", {{ class: "tick", x: margin.left - 10, y: y + 4, "text-anchor": "end" }}, formatNumber(value)));
      }}
      years.forEach((year) => {{
        const x = xScale(year);
        svg.appendChild(createSvg("line", {{ class: "grid", x1: x, x2: x, y1: margin.top, y2: height - margin.bottom }}));
        svg.appendChild(createSvg("text", {{ class: "tick", x, y: height - 18, "text-anchor": "middle" }}, String(year)));
      }});
      svg.appendChild(createSvg("line", {{ class: "axis", x1: margin.left, x2: width - margin.right, y1: height - margin.bottom, y2: height - margin.bottom }}));
      svg.appendChild(createSvg("line", {{ class: "axis", x1: margin.left, x2: margin.left, y1: margin.top, y2: height - margin.bottom }}));
      svg.appendChild(createSvg("text", {{ class: "chart-note", x: margin.left, y: 14 }}, "մլրդ դրամ"));
    }}

    function renderDetail(selected) {{
      const valuesHtml = selected.records.map((record) => {{
        const cls = statusColors[record.status] ? "" : " status-history";
        return `<span class="detail-value${{cls}}" style="background:${{statusColors[record.status] || "#f7f8fa"}}22"><span class="detail-year">${{record.year}}</span>${{formatNumber(record.value)}} <span class="status">${{record.status}}</span></span>`;
      }}).join("");
      detail.innerHTML = `
        <div>
          <div class="detail-title">${{selected.label}}</div>
          <div class="detail-file">${{selected.source_file || ""}}</div>
        </div>
        <div class="detail-values">${{valuesHtml}}</div>
      `;
    }}

    function selectSeries(id) {{
      const selected = series.find((item) => item.id === id) || series[0];
      selectedSeriesId = selected.id;
      current.textContent = selected.label;
      svg.querySelectorAll("[data-series-id]").forEach((node) => {{
        const match = node.dataset.seriesId === selected.id;
        node.classList.toggle("series-active", match);
        node.classList.toggle("series-muted", !match);
      }});
      document.querySelectorAll("tr[data-series-id]").forEach((node) => {{
        const match = node.dataset.seriesId === selected.id;
        node.classList.toggle("is-selected", match);
      }});
      renderDetail(selected);
    }}

    function stepSeries(delta) {{
      const selectedIndex = series.findIndex((item) => item.id === selectedSeriesId);
      const nextIndex = (selectedIndex + delta + series.length) % series.length;
      selectSeries(series[nextIndex].id);
    }}

    let selectedSeriesId = series[series.length - 1].id;
    drawAxes();
    series.forEach((item) => {{
      const group = createSvg("g", {{ "data-series-id": item.id }});
      const color = colors[item.source_type] || "#334e68";
      const line = createSvg("path", {{
        class: "series-line",
        d: pathFor(item.records),
        stroke: color,
        "stroke-dasharray": item.source_type === "SPENDING_Q1234" ? "6 5" : "0"
      }});
      line.appendChild(createSvg("title", {{}}, item.label));
      group.appendChild(line);
      item.records.forEach((record) => {{
        const point = createSvg("circle", {{
          class: "series-point",
          cx: xScale(record.year),
          cy: yScale(record.value),
          r: 4.6,
          fill: statusColors[record.status] || color
        }});
        point.appendChild(createSvg("title", {{}}, `${{item.label}}\\n${{record.year}}: ${{formatNumber(record.value)}} (${{record.status}})`));
        group.appendChild(point);
      }});
      svg.appendChild(group);
    }});
    prev.addEventListener("click", () => stepSeries(-1));
    next.addEventListener("click", () => stepSeries(1));
    document.addEventListener("click", (event) => {{
      if (!(event.target instanceof Element)) return;
      const row = event.target.closest("tr[data-series-id]");
      if (row) selectSeries(row.dataset.seriesId);
    }});
    document.addEventListener("keydown", (event) => {{
      if (event.key !== "Enter" && event.key !== " ") return;
      if (!(event.target instanceof Element)) return;
      const row = event.target.closest("tr[data-series-id]");
      if (!row) return;
      event.preventDefault();
      selectSeries(row.dataset.seriesId);
    }});
    selectSeries(selectedSeriesId);
    document.addEventListener("DOMContentLoaded", () => selectSeries(selectedSeriesId));
  }})();
  </script>
"""


def _nominal_gdp_series(snapshots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    series = []
    for index, snapshot in enumerate(sorted(snapshots, key=_gdp_snapshot_display_key)):
        records = _nominal_gdp_records(snapshot)
        if not records:
            continue
        series.append(
            {
                "id": f"series-{index}",
                "label": f"{snapshot['year']} {snapshot['source_type']}",
                "source_type": str(snapshot["source_type"]),
                "source_file": str(snapshot.get("source_file", "")),
                "records": [
                    {
                        "year": int(record["target_year"]),
                        "status": str(record.get("status", "")),
                        "value": float(record["value"]),
                    }
                    for record in records
                    if record.get("value") is not None
                ],
            }
        )
    return [item for item in series if item["records"]]


def _render_nominal_gdp_report_table(snapshots: list[dict[str, Any]]) -> str:
    rows = [
        (index, snapshot, _nominal_gdp_records(snapshot))
        for index, snapshot in enumerate(sorted(snapshots, key=_gdp_snapshot_display_key))
        if _nominal_gdp_records(snapshot)
    ]
    if not rows:
        return "<p>No nominal GDP snapshots found.</p>"

    years = sorted(
        {
            int(record["target_year"])
            for _index, _snapshot, records in rows
            for record in records
        }
    )
    header = "".join(f"<th>{year}</th>" for year in years)
    body_rows = []
    for index, snapshot, records in rows:
        records_by_year: dict[int, list[dict[str, Any]]] = {}
        for record in records:
            records_by_year.setdefault(int(record["target_year"]), []).append(record)
        cells = []
        for year in years:
            year_records = records_by_year.get(year, [])
            if not year_records:
                cells.append('<td class="num missing">-</td>')
                continue
            values = "".join(_render_gdp_value(record) for record in year_records)
            cells.append(f'<td class="num">{values}</td>')
        source = f"{snapshot['year']} {snapshot['source_type']}"
        source_file = str(snapshot.get("source_file", ""))
        body_rows.append(
            f'<tr data-series-id="series-{index}" tabindex="0">'
            f'<td class="source">{escape(source)}</td>'
            f'<td class="file">{escape(source_file)}</td>'
            + "".join(cells)
            + "</tr>"
        )
    return (
        "<table><thead><tr><th>Source</th><th>Source file</th>"
        + header
        + "</tr></thead><tbody>"
        + "".join(body_rows)
        + "</tbody></table>"
    )


def _nominal_gdp_records(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for table in snapshot.get("tables", []):
        for record in table.get("records", []):
            if str(record.get("indicator")) == "Անվանական ՀՆԱ":
                if _skip_nominal_gdp_report_record(snapshot, record):
                    continue
                records.append(record)
    records.sort(key=lambda record: (int(record["target_year"]), str(record.get("status", ""))))
    return records


def _gdp_snapshot_display_key(snapshot: dict[str, Any]) -> tuple[int, int, int, str]:
    year = int(snapshot["year"])
    source_type = str(snapshot["source_type"])
    comparison_year = year + 1 if source_type == "SPENDING_Q1234" else year
    source_order = 1 if source_type == "SPENDING_Q1234" else 0
    return (comparison_year, source_order, year, source_type)


def _skip_nominal_gdp_report_record(
    snapshot: dict[str, Any], record: dict[str, Any]
) -> bool:
    return (
        snapshot.get("source_type") == "SPENDING_Q1234"
        and record.get("status") in SPENDING_GDP_BUDGET_STATUSES
    )


def _render_gdp_value(record: dict[str, Any]) -> str:
    value = record.get("value")
    if value is None:
        formatted = "-"
    else:
        formatted = _format_number(float(value))
    status = str(record.get("status", ""))
    status_class = _status_css_class(status)
    return (
        f'<span class="cell-value {status_class}">{escape(formatted)}'
        f'<span class="status">{escape(status)}</span></span>'
    )


def _render_records_table(records: list[dict[str, Any]]) -> str:
    columns = _report_columns(records)
    year_counts: dict[int, int] = {}
    for target_year, _status in columns:
        year_counts[target_year] = year_counts.get(target_year, 0) + 1

    rows_by_indicator: dict[tuple[str, str], dict[tuple[int, str], dict[str, Any]]] = {}
    for record in records:
        key = (str(record["indicator"]), str(record.get("unit", "")))
        column_key = (int(record["target_year"]), str(record.get("status", "")))
        rows_by_indicator.setdefault(key, {})[column_key] = record

    header = "".join(
        _render_column_header(target_year, status, year_counts[target_year] > 1)
        for target_year, status in columns
    )
    body_rows = []
    for (indicator, unit), values_by_year in rows_by_indicator.items():
        cells = []
        for column in columns:
            record = values_by_year.get(column)
            if record is None or record.get("value") is None:
                cells.append('<td class="num missing">-</td>')
                continue
            value = _format_number(float(record["value"]))
            status = str(record.get("status", ""))
            status_class = _status_css_class(status)
            cells.append(
                f'<td class="num {status_class}">{escape(value)}'
                f'<span class="status">{escape(status)}</span></td>'
            )
        body_rows.append(
            "<tr>"
            f"<td>{escape(indicator)}</td><td>{escape(unit)}</td>"
            + "".join(cells)
            + "</tr>"
        )
    return (
        "<table><thead><tr><th>Indicator</th><th>Unit</th>"
        + header
        + "</tr></thead><tbody>"
        + "".join(body_rows)
        + "</tbody></table>"
    )


def _report_columns(records: list[dict[str, Any]]) -> list[tuple[int, str]]:
    columns: list[tuple[int, str]] = []
    seen: set[tuple[int, str]] = set()
    for record in records:
        column = (int(record["target_year"]), str(record.get("status", "")))
        if column in seen:
            continue
        columns.append(column)
        seen.add(column)
    return columns


def _render_column_header(target_year: int, status: str, show_status: bool) -> str:
    if not show_status:
        return f"<th>{target_year}</th>"
    return (
        f"<th>{target_year}"
        f'<span class="status">{escape(status)}</span>'
        "</th>"
    )


def _format_number(value: float) -> str:
    if value.is_integer():
        return f"{int(value):,}"
    return f"{value:,.3f}".rstrip("0").rstrip(".")


def _status_css_class(status: str) -> str:
    if status == "փաստ":
        return "status-actual"
    if status == "սպասում":
        return "status-expected"
    if status in {"ծրագիր", "պետական բյուջե"}:
        return "status-planned"
    if status == "կանխ.":
        return "status-forecast"
    return "status-history"
