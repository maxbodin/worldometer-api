import json
import re
from typing import Any

from bs4 import BeautifulSoup

from .table_parser import normalize_lookup_key


def parse_water_country_summary(html: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    cards = _extract_metric_cards(soup)

    resources_series = _extract_script_data(soup, "Renewable water resources per capita")
    water_use_series = _extract_script_data(
        soup, "Agricultural, Municipal, and Industrial Water Withdrawal"
    )
    no_access_series = _extract_script_data(
        soup, "Historical Chart of People with no access to safe drinking water"
    )

    page_text = soup.get_text(" ", strip=True)

    sections = {
        "precipitation": {
            "depth": cards.get("waterprecipitationindepth"),
            "volume": cards.get("waterprecipitationinvolume"),
        },
        "resources": {
            "renewable_total": cards.get("renewablewaterresources"),
            "per_capita": cards.get("waterresourcespercapita"),
            "dependency": cards.get("waterdependency"),
            "latest_per_capita": _latest_series_value(resources_series, "resources"),
        },
        "water_use": {
            "latest_by_sector": _latest_water_use_values(water_use_series),
        },
        "safe_drinking_water": {
            "no_access_people": cards.get("donthaveaccesstosafedrinkingwater"),
            "no_access_share": _extract_no_access_share(page_text),
            "latest_no_access_people": _latest_series_value(no_access_series, "people"),
        },
    }

    if not _contains_any_values(sections):
        return {}

    return {"sections": sections}


def _extract_metric_cards(soup: BeautifulSoup) -> dict[str, dict[str, str]]:
    cards: dict[str, dict[str, str]] = {}

    for card in soup.select("div.not-prose.rounded.border.bg-white.text-center.shadow-sm"):
        title_element = card.select_one("div.uppercase")
        value_element = card.select_one("div.text-2xl.font-bold")

        if title_element is None or value_element is None:
            continue

        title = title_element.get_text(" ", strip=True)
        normalized_title = normalize_lookup_key(title)
        if not normalized_title:
            continue

        cards[normalized_title] = {
            "label": title,
            "value": value_element.get_text(" ", strip=True),
            "description": _extract_card_description(card),
        }

    return cards


def _extract_card_description(card) -> str:
    description_elements = card.select("div.text-center")
    if not description_elements:
        return ""

    # Prefer the last text-center block which usually contains explanatory text.
    return description_elements[-1].get_text(" ", strip=True)


def _extract_script_data(soup: BeautifulSoup, title_snippet: str) -> list[dict[str, Any]]:
    for script in soup.find_all("script"):
        script_text = script.string or script.get_text("\n", strip=False)
        if not script_text or title_snippet not in script_text:
            continue

        match = re.search(r"const data = (\[.*?\]);", script_text, re.DOTALL)
        if match is None:
            continue

        try:
            parsed = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue

        if isinstance(parsed, list):
            return [entry for entry in parsed if isinstance(entry, dict)]

    return []


def _latest_series_value(series: list[dict[str, Any]], field: str) -> dict[str, Any] | None:
    for entry in sorted(series, key=lambda item: int(item.get("year", 0)), reverse=True):
        value = entry.get(field)
        if value is not None:
            return {
                "year": entry.get("year"),
                "value": value,
            }

    return None


def _latest_water_use_values(series: list[dict[str, Any]]) -> dict[str, Any] | None:
    for entry in sorted(series, key=lambda item: int(item.get("year", 0)), reverse=True):
        total = entry.get("total")
        municipal = entry.get("municipal")
        industrial = entry.get("industrial")
        agriculture = entry.get("agriculture")

        if total is None and municipal is None and industrial is None and agriculture is None:
            continue

        return {
            "year": entry.get("year"),
            "total_billion_m3": total,
            "municipal_billion_m3": municipal,
            "industrial_billion_m3": industrial,
            "agriculture_billion_m3": agriculture,
        }

    return None


def _extract_no_access_share(page_text: str) -> dict[str, Any] | None:
    collapsed_text = re.sub(r"\s+", " ", page_text)
    match = re.search(
        r"([\d.]+%)\s+of the population of\s+.+?\((\d{4})\)",
        collapsed_text,
        re.IGNORECASE,
    )
    if match is None:
        return None

    return {
        "share": match.group(1),
        "year": int(match.group(2)),
    }


def _contains_any_values(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, (str, int, float, bool)):
        return True
    if isinstance(value, list):
        return any(_contains_any_values(item) for item in value)
    if isinstance(value, dict):
        return any(_contains_any_values(item) for item in value.values())
    return False
