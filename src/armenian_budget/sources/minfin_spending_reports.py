from __future__ import annotations

import json
import ssl
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote, urljoin, urlparse

import httpx
from bs4 import BeautifulSoup


PAGE_URL = "https://minfin.am/hy/page/hy_hashvetvutyunner"
CHECK_YEAR_URL = "https://minfin.am/hy/main/check_year/"
FILES_BASE_URL = "https://minfin.am/website/images/files/"
REPORTS_URL = "https://minfin.am/hy/main/get_reports/"
DOWNLOAD_EXTENSIONS = {"csv", "doc", "docx", "pdf", "rar", "xls", "xlsx", "zip"}
PERIODS = {
    "1": ("Q1", "spending_q1", "1-ին եռամսյակ"),
    "2": ("Q12", "spending_q12", "1-ին կիսամյակ"),
    "3": ("Q123", "spending_q123", "Ինն ամիսներ"),
    "4": ("Q1234", "spending_q1234", "Տարեկան"),
}


def minfin_ssl_context() -> ssl.SSLContext:
    """Create an SSL context compatible with minfin.am's legacy TLS setup."""
    context = ssl.create_default_context()
    context.set_ciphers("DEFAULT@SECLEVEL=1")
    context.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
    return context


def extract_year_ids(html: str) -> list[tuple[int, int]]:
    soup = BeautifulSoup(html, "html.parser")
    year_select = soup.find("select", id="yearSelect")
    if year_select is None:
        raise RuntimeError("yearSelect not found on minfin.am reports page")

    years: list[tuple[int, int]] = []
    for option in year_select.find_all("option"):
        value = option.get("value")
        data_id = option.get("data-id")
        if not value or not data_id:
            continue
        years.append((int(value), int(data_id)))
    return years


def build_file_url(filename: str) -> str:
    return FILES_BASE_URL + quote(filename, safe="/%")


def build_year_file_url(year: int, filename: str) -> str:
    return f"https://minfin.am/website/images/files_{year}/" + quote(
        filename, safe="/%"
    )


def file_format(filename: str) -> str:
    suffix = Path(filename).suffix.lower().lstrip(".")
    return suffix or "bin"


def file_name_from_url(url: str) -> str:
    return unquote(Path(urlparse(url).path).name)


def clean_text(value: str) -> str:
    return " ".join(value.split())


def download_item(name: str, url: str, source: str, **extra: Any) -> dict[str, Any]:
    filename = file_name_from_url(url)
    item = {
        "name": clean_text(name) or filename,
        "file_name": filename,
        "file_format": file_format(filename),
        "download_url": url,
        "source": source,
    }
    item.update(extra)
    return item


def is_download_url(url: str) -> bool:
    return file_format(file_name_from_url(url)) in DOWNLOAD_EXTENSIONS


def extract_detail_page_downloads(html: str, page_url: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    scope = soup.select_one(".docs") or soup
    downloads_by_url: dict[str, dict[str, Any]] = {}

    for anchor in scope.find_all("a", href=True):
        url = urljoin(page_url, anchor["href"])
        if not is_download_url(url):
            continue
        name = clean_text(anchor.get_text(" ", strip=True))
        item = download_item(name, url, "detail_page")
        existing = downloads_by_url.get(url)
        if existing is None or (not existing["name"] and item["name"]):
            downloads_by_url[url] = item

    return list(downloads_by_url.values())


def extract_ajax_report_downloads(
    client: httpx.Client,
    year: int,
    page_year_id: int,
    periodicity: int,
    ajax_headers: dict[str, str],
) -> list[dict[str, Any]]:
    response = client.post(
        REPORTS_URL,
        data={"val": str(page_year_id), "periodicity": str(periodicity)},
        headers=ajax_headers,
    )
    response.raise_for_status()

    downloads: list[dict[str, Any]] = []
    for row in response.json():
        payload = json.loads(row["text_hy"])
        title = payload.get("title") or ""
        title_file = payload.get("title_file")
        section = str(row.get("shorttext_hy") or payload.get("category") or "")

        if title_file:
            downloads.append(
                download_item(
                    title,
                    build_year_file_url(year, str(title_file)),
                    "ajax_report",
                    section=section,
                    level=0,
                )
            )

        for key, child in (payload.get("texts") or {}).items():
            child_file = child.get("file")
            if not child_file:
                continue
            downloads.append(
                download_item(
                    child.get("title") or "",
                    build_year_file_url(year, str(child_file)),
                    "ajax_report",
                    section=section,
                    tree_key=key,
                    level=str(key).count("-"),
                )
            )

    return downloads


def list_minfin_spending_reports(
    years: set[int] | None = None,
) -> list[dict[str, Any]]:
    page_headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
        ),
    }
    ajax_headers = {
        **page_headers,
        "X-Requested-With": "XMLHttpRequest",
        "Referer": PAGE_URL,
    }

    with httpx.Client(
        headers=page_headers,
        verify=minfin_ssl_context(),
        follow_redirects=True,
        timeout=30,
    ) as client:
        page = client.get(PAGE_URL)
        page.raise_for_status()
        year_ids = extract_year_ids(page.text)

        reports: list[dict[str, Any]] = []
        for year, page_year_id in year_ids:
            if years is not None and year not in years:
                continue

            response = client.post(
                CHECK_YEAR_URL,
                data={"val": str(year)},
                headers=ajax_headers,
            )
            response.raise_for_status()
            for item in response.json():
                periodicity = str(item["periodicity"])
                quarter, source_type, period_label = PERIODS[periodicity]
                filename = str(item["file"])
                page_url = item.get("url") or ""
                downloads: list[dict[str, Any]] = []

                if page_url:
                    detail_page = client.get(page_url)
                    detail_page.raise_for_status()
                    downloads = extract_detail_page_downloads(
                        detail_page.text, str(detail_page.url)
                    )
                elif year > 2024 or (year == 2024 and periodicity == "4"):
                    downloads.append(
                        download_item(
                            "Ամբողջական փաթեթ",
                            build_file_url(filename),
                            "period_package",
                        )
                    )
                    downloads.extend(
                        extract_ajax_report_downloads(
                            client,
                            year,
                            page_year_id,
                            int(periodicity),
                            ajax_headers,
                        )
                    )
                else:
                    downloads.append(
                        download_item(
                            period_label,
                            build_file_url(filename),
                            "period_file",
                        )
                    )

                reports.append(
                    {
                        "year": year,
                        "page_year_id": page_year_id,
                        "quarter": quarter,
                        "source_type": source_type,
                        "periodicity": int(periodicity),
                        "period_label_hy": period_label,
                        "file_name": filename,
                        "file_format": file_format(filename),
                        "download_url": build_file_url(filename),
                        "page_url": page_url,
                        "downloads": downloads,
                    }
                )

    return sorted(reports, key=lambda row: (row["year"], row["periodicity"]))
