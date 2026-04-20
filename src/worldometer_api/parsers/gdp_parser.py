import re
from typing import Any

from bs4 import BeautifulSoup


def parse_gdp_country_description(html: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    description_list = _find_description_list(soup)
    if description_list is None:
        return {}

    items = _extract_description_items(description_list)
    if not items:
        return {}

    title = _extract_source_title(description_list)
    source, year = _extract_source_and_year(title)

    payload: dict[str, Any] = {
        "items": items,
        "text": " ".join(items),
    }
    if title:
        payload["title"] = title
    if source:
        payload["source"] = source
    if year is not None:
        payload["year"] = year

    return payload


def _find_description_list(soup: BeautifulSoup):
    for description_list in soup.find_all("dl"):
        items = _extract_description_items(description_list)
        if not items:
            continue

        text = " ".join(items)
        if "Gross Domestic Product (GDP)" in text and "GDP growth rate" in text:
            return description_list

    return None


def _extract_description_items(description_list: Any) -> list[str]:
    items: list[str] = []
    for item in description_list.find_all("dd"):
        text = _normalize_whitespace(item.get_text(" ", strip=True))
        if text:
            items.append(text)

    return items


def _extract_source_title(description_list: Any) -> str | None:
    heading = description_list.find_previous(["h3", "h4"])
    if heading is None:
        return None

    title = _normalize_whitespace(heading.get_text(" ", strip=True))
    return title or None


def _extract_source_and_year(title: str | None) -> tuple[str | None, int | None]:
    if not title:
        return None, None

    match = re.match(r"^([A-Za-z][A-Za-z .&-]*?)\s*\((\d{4})\)$", title)
    if match is None:
        return None, None

    source = _normalize_whitespace(match.group(1))
    return source or None, int(match.group(2))


def _normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()
