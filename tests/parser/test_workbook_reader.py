"""Tests for reading Excel 2003 XML (SpreadsheetML) workbooks."""

from __future__ import annotations

import pandas as pd
import pytest

from armenian_budget.core.enums import SourceType
from armenian_budget.ingestion.parsers import (
    flatten_budget_excel_2019_2024,
    workbook_reader,
)
from armenian_budget.ingestion.parsers.workbook_reader import read_first_sheet

NS = "urn:schemas-microsoft-com:office:spreadsheet"


def _workbook(body: str) -> str:
    return (
        '<?xml version="1.0"?>\n'
        f'<Workbook xmlns="{NS}" xmlns:ss="{NS}">'
        f"<Worksheet ss:Name=\"S\"><Table>{body}</Table></Worksheet></Workbook>"
    )


def _write(tmp_path, text: str, name: str = "book.xls"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def _cell(value, kind: str = "String") -> str:
    return f'<Cell><Data ss:Type="{kind}">{value}</Data></Cell>'


def test_xml_cell_positions(tmp_path):
    body = (
        f"<Row>{_cell('a')}</Row>"
        f'<Row ss:Index="3">{_cell("b")}'
        f'<Cell ss:Index="4"><Data ss:Type="String">c</Data></Cell>'
        f'<Cell ss:MergeAcross="2"><Data ss:Type="String">d</Data></Cell>'
        f"{_cell('e')}</Row>"
    )
    df = read_first_sheet(_write(tmp_path, _workbook(body)))

    assert df.shape == (3, 8)
    assert df.iloc[0, 0] == "a"
    assert df.iloc[0, 1:].isna().all()
    assert df.iloc[1].isna().all()
    # b at col 1, c at index 4, d right after c (col 5) spanning 5-7, e at col 8
    assert df.iloc[2, 0] == "b"
    assert df.iloc[2, 3] == "c"
    assert df.iloc[2, 4] == "d"
    assert df.iloc[2, 7] == "e"
    assert list(df.columns) == list(range(8))


def test_xml_number_types(tmp_path):
    body = (
        "<Row>"
        f"{_cell('11001', 'Number')}{_cell('12.5', 'Number')}"
        f"{_cell('1E3', 'Number')}{_cell('007')}"
        "</Row>"
    )
    df = read_first_sheet(_write(tmp_path, _workbook(body)))

    # Column dtypes show the Python type each cell was parsed to.
    assert df[0].dtype == "int64" and df[0][0] == 11001
    assert df[1].dtype == "float64" and df[1][0] == 12.5
    assert df[2].dtype == "float64" and df[2][0] == 1000.0
    assert df[3][0] == "007"


def test_xml_control_character_refs_removed(tmp_path):
    body = f"<Row>{_cell('a&#1;b&#30;c&#9;d')}</Row>"
    df = read_first_sheet(_write(tmp_path, _workbook(body)))

    assert df.iloc[0, 0] == "abc\td"


def test_non_xml_goes_to_pandas(tmp_path, monkeypatch):
    path = tmp_path / "book.xlsx"
    source = pd.DataFrame([["x", 1], ["y", 2.5]])
    source.to_excel(path, index=False, header=False)
    expected = pd.read_excel(path, sheet_name=0, header=None)

    calls = []
    real = pd.read_excel

    def spy(*args, **kwargs):
        calls.append((args, kwargs))
        return real(*args, **kwargs)

    monkeypatch.setattr(workbook_reader.pd, "read_excel", spy)
    result = read_first_sheet(path)

    pd.testing.assert_frame_equal(result, expected)
    assert calls == [((path,), {"sheet_name": 0, "header": None})]


def _budget_law_table() -> list[list]:
    return [
        ["", "", "ԸՆԴԱՄԵՆԸ", 1000000],
        ["", "", "State Body 1", 600000],
        [1001, "", "Program 1", 300000],
        ["", "", "Program Name", ""],
        ["", "", "ծրագրինպատակը", ""],
        ["", "", "Program Goal", ""],
        ["", "", "վերջնականարդյունքինկարագրությունը", ""],
        ["", "", "Result Description", ""],
        ["", "", "Ծրագրի միջոցառումներ", ""],
        ["", 1001001, "Subprogram 1", 150000],
        ["", "", "Subprogram Name", ""],
        ["", "", "միջոցառմաննկարագրությունը", ""],
        ["", "", "Subprogram Description", ""],
        ["", "", "միջոցառմանտեսակը", ""],
        ["", "", "Subprogram Type", ""],
    ]


def _spreadsheetml(table: list[list]) -> str:
    rows = []
    for row in table:
        cells = []
        for idx, value in enumerate(row, start=1):
            if value == "":
                continue
            kind = "String" if isinstance(value, str) else "Number"
            cells.append(
                f'<Cell ss:Index="{idx}"><Data ss:Type="{kind}">{value}</Data></Cell>'
            )
        rows.append(f"<Row>{''.join(cells)}</Row>")
    return _workbook("".join(rows))


def test_xml_workbook_parses_like_xlsx(tmp_path):
    table = _budget_law_table()
    xlsx = tmp_path / "book.xlsx"
    pd.DataFrame(table).to_excel(xlsx, index=False, header=False)
    xml = _write(tmp_path, _spreadsheetml(table), "book.xls")

    from_xlsx = flatten_budget_excel_2019_2024(xlsx, SourceType.BUDGET_LAW)
    from_xml = flatten_budget_excel_2019_2024(xml, SourceType.BUDGET_LAW)

    assert len(from_xml[0]) > 0
    pd.testing.assert_frame_equal(from_xlsx[0], from_xml[0])
    assert from_xlsx[1] == from_xml[1] == {"overall_total": 1000000.0}
    assert from_xlsx[2] == from_xml[2]
    assert from_xlsx[3] == from_xml[3]


def test_other_xml_is_not_claimed(tmp_path, monkeypatch):
    path = _write(tmp_path, '<?xml version="1.0"?><other><Table/></other>')
    calls = []

    def fake(*args, **kwargs):
        calls.append((args, kwargs))
        raise ValueError("pandas was asked")

    monkeypatch.setattr(workbook_reader.pd, "read_excel", fake)
    with pytest.raises(ValueError, match="pandas was asked"):
        read_first_sheet(path)
    assert calls == [((path,), {"sheet_name": 0, "header": None})]
