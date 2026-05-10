from __future__ import annotations

import re
from typing import Any
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from armenian_budget.sources.minfin_spending_reports import (
    clean_text,
    download_item,
    extract_detail_page_downloads,
    is_download_url,
    minfin_ssl_context,
)


PAGE_URL = "https://minfin.am/hy/page/petakan_byuj/"
BUDGET_YEAR_PATTERN = re.compile(r"(20\d{2})")


def extract_budget_year_pages(html: str, page_url: str = PAGE_URL) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    pages_by_url: dict[str, dict[str, Any]] = {}

    for anchor in soup.find_all("a", href=True):
        title = clean_text(anchor.get_text(" ", strip=True))
        match = BUDGET_YEAR_PATTERN.search(title)
        if match is None:
            continue

        url = urljoin(page_url, anchor["href"])
        if "/hy/page/petakan_byuje_" not in url:
            continue

        pages_by_url[url] = {
            "year": int(match.group(1)),
            "name": title,
            "page_url": url,
        }

    return sorted(pages_by_url.values(), key=lambda row: row["year"])


def budget_download_name(anchor: Any, page_url: str) -> str:
    name = clean_text(anchor.get_text(" ", strip=True))
    url = urljoin(page_url, anchor["href"])

    for container_name in ("li", "p"):
        container = anchor.find_parent(container_name)
        if container is None:
            continue

        download_anchors = [
            item
            for item in container.find_all("a", href=True)
            if is_download_url(urljoin(page_url, item["href"]))
        ]
        download_urls = {urljoin(page_url, item["href"]) for item in download_anchors}
        if download_urls == {url}:
            separator = "" if len(download_anchors) == 1 else " "
            container_name_text = clean_text(container.get_text(separator, strip=True))
            if len(container_name_text) > len(name):
                return container_name_text

    return name


def extract_budget_page_downloads(html: str, page_url: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    scope = soup.select_one(".app_block") or soup.select_one(".content")
    if scope is None:
        return [
            {**item, "source": "budget_page"}
            for item in extract_detail_page_downloads(html, page_url)
        ]

    downloads_by_url: dict[str, dict[str, Any]] = {}
    for anchor in scope.find_all("a", href=True):
        url = urljoin(page_url, anchor["href"])
        if not is_download_url(url):
            continue

        name = budget_download_name(anchor, page_url)
        item = download_item(name, url, "budget_page")
        existing = downloads_by_url.get(url)
        if existing is None or len(item["name"]) > len(existing["name"]):
            downloads_by_url[url] = item

    return list(downloads_by_url.values())


def list_minfin_budget(years: set[int] | None = None) -> list[dict[str, Any]]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
        ),
    }

    with httpx.Client(
        headers=headers,
        verify=minfin_ssl_context(),
        follow_redirects=True,
        timeout=30,
    ) as client:
        page = client.get(PAGE_URL)
        page.raise_for_status()
        year_pages = extract_budget_year_pages(page.text, str(page.url))

        budget_records: list[dict[str, Any]] = []
        for year_page in year_pages:
            year = int(year_page["year"])
            if years is not None and year not in years:
                continue

            detail_page = client.get(year_page["page_url"])
            detail_page.raise_for_status()
            downloads = extract_budget_page_downloads(
                detail_page.text,
                str(detail_page.url),
            )
            budget_records.append(
                {
                    **year_page,
                    "source_type": "budget_law",
                    "downloads": downloads,
                }
            )

    return budget_records
