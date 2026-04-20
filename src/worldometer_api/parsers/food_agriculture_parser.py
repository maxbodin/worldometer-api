import json
import re
from typing import Any

from bs4 import BeautifulSoup


SECTION_ID_TO_KEY: dict[str, str] = {
    "undernourished": "undernourished",
    "forest": "forest",
    "cropland": "cropland",
    "pest": "pesticides",
}

CARD_SELECTOR = "div.not-prose.rounded.border.bg-white.text-center.shadow-sm"


def parse_food_agriculture_country_summary(html: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    sections: dict[str, dict[str, Any]] = {}

    for section_id, section_key in SECTION_ID_TO_KEY.items():
        section = soup.find(id=section_id)
        if section is None:
            continue

        payload: dict[str, Any] = {}
        title_element = section.find(["h2", "h3"])
        if title_element is not None:
            title = title_element.get_text(" ", strip=True)
            if title:
                payload["title"] = title

        cards = _extract_cards(section)
        if cards:
            payload["cards"] = cards

        latest_series_point = _extract_latest_series_point(section)
        if latest_series_point is not None:
            payload["latest_series_point"] = latest_series_point

        if payload:
            sections[section_key] = payload

    if not sections:
        return {}

    return {"sections": sections}


def _extract_cards(section: Any) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []

    for card in section.select(CARD_SELECTOR):
        title_element = card.select_one("div.uppercase")
        label = title_element.get_text(" ", strip=True) if title_element is not None else ""

        values = [
            value.get_text(" ", strip=True)
            for value in card.select("span.text-2xl.font-bold, span.text-xl.font-bold")
            if value.get_text(" ", strip=True)
        ]
        values = _dedupe(values)

        card_text = card.get_text(" ", strip=True)
        if not label and not values and not card_text:
            continue

        payload: dict[str, Any] = {}
        if label:
            payload["label"] = label
        if values:
            payload["values"] = values
        if card_text:
            payload["description"] = card_text

        global_rank = _extract_global_rank(card_text)
        if global_rank is not None:
            payload["global_rank"] = global_rank

        world_share = _extract_world_share(card_text)
        if world_share is not None:
            payload["world_share"] = world_share

        cards.append(payload)

    return cards


def _extract_latest_series_point(section: Any) -> dict[str, Any] | None:
    for script in section.find_all("script"):
        script_text = script.string or script.get_text("\n", strip=False)
        if not script_text:
            continue

        for match in re.finditer(r"const data = (\[.*?\]);", script_text, re.DOTALL):
            try:
                parsed = json.loads(match.group(1))
            except json.JSONDecodeError:
                continue

            if not isinstance(parsed, list):
                continue

            latest_point = _find_latest_point(parsed)
            if latest_point is not None:
                return latest_point

    return None


def _find_latest_point(points: list[Any]) -> dict[str, Any] | None:
    latest: dict[str, Any] | None = None
    latest_year: int | None = None

    for point in points:
        if not isinstance(point, dict):
            continue

        year = _parse_int(point.get("year"))
        if year is None:
            continue

        values = {key: value for key, value in point.items() if key != "year" and value is not None}
        if not values:
            continue

        if latest_year is None or year > latest_year:
            latest_year = year
            latest = {
                "year": year,
                "values": values,
            }

    return latest


def _extract_global_rank(text: str) -> int | None:
    match = re.search(r"Global\s+Rank\s*:\s*#?(\d+)", text, re.IGNORECASE)
    if match is None:
        return None

    return int(match.group(1))


def _extract_world_share(text: str) -> str | None:
    match = re.search(r"Share\s+of\s+World\s+[^:]+:\s*([\d.]+%)", text, re.IGNORECASE)
    if match is None:
        return None

    return match.group(1)


def _parse_int(value: Any) -> int | None:
    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    if isinstance(value, str):
        compact = value.strip()
        if compact.isdigit():
            return int(compact)

    return None


def _dedupe(values: list[str]) -> list[str]:
    unique: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        unique.append(value)
    return unique
