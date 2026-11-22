"""Read the first sheet of a budget workbook.

Some workbooks published by parliament.am are Excel 2003 XML ("SpreadsheetML")
saved with an ``.xls`` name, which pandas cannot open. Those are read with the
standard library; every other file goes to ``pd.read_excel`` unchanged.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

NS = "{urn:schemas-microsoft-com:office:spreadsheet}"

# Numeric character references (decimal and hexadecimal) to control characters
# forbidden in XML 1.0 (1..31 except 9, 10, 13).
_FORBIDDEN_CHAR_REFS = re.compile(
    rb"&#(?:[0-8]|1[124-9]|2[0-9]|3[01]);"
    rb"|&#[xX]0*(?:[0-8]|[bBcCeEfF]|1[0-9a-fA-F]);"
)
_LEADING = b"\xef\xbb\xbf \t\r\n"
_PREFIX_BYTES = 512


def read_first_sheet(path: str | Path) -> pd.DataFrame:
    """Return the first worksheet as a DataFrame with no header row."""
    with open(path, "rb") as handle:
        prefix = handle.read(_PREFIX_BYTES)
        if prefix.lstrip(_LEADING).startswith(b"<?xml"):
            raw = prefix + handle.read()
            try:
                root = ET.fromstring(_FORBIDDEN_CHAR_REFS.sub(b"", raw.lstrip(_LEADING)))
            except ET.ParseError:
                root = None
            if root is not None and root.tag == f"{NS}Workbook":
                return _spreadsheetml_to_df(root)
    return pd.read_excel(path, sheet_name=0, header=None)


def _spreadsheetml_to_df(root: ET.Element) -> pd.DataFrame:
    worksheet = root.find(f"{NS}Worksheet")
    table = worksheet.find(f"{NS}Table") if worksheet is not None else None
    rows: dict[int, dict[int, int | float | str]] = {}
    r = 0
    for row in table.findall(f"{NS}Row") if table is not None else []:
        r = int(row.get(f"{NS}Index", r + 1))
        c = 0
        for cell in row.findall(f"{NS}Cell"):
            c = int(cell.get(f"{NS}Index", c + 1))
            data = cell.find(f"{NS}Data")
            if data is not None:
                text = "".join(data.itertext())
                if data.get(f"{NS}Type") == "Number":
                    value = float(text) if re.search(r"[.eE]", text) else int(text)
                else:
                    value = text
                rows.setdefault(r, {})[c] = value
            c += int(cell.get(f"{NS}MergeAcross", 0))
    if not rows:
        return pd.DataFrame()
    n_rows = max(rows)
    n_cols = max(max(cells) for cells in rows.values())
    return pd.DataFrame(
        [
            [rows.get(i, {}).get(j) for j in range(1, n_cols + 1)]
            for i in range(1, n_rows + 1)
        ]
    )
