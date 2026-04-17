import re
import unicodedata
from typing import Any

from bs4 import BeautifulSoup


def normalize_header(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_text = ascii_text.lower().strip()
    ascii_text = ascii_text.replace("%", " percent ").replace("#", " rank ")
    ascii_text = re.sub(r"\([^)]*\)", " ", ascii_text)
    ascii_text = re.sub(r"[^a-z0-9]+", "_", ascii_text)
    ascii_text = re.sub(r"_+", "_", ascii_text).strip("_")

    if not ascii_text:
        return "column"

    if ascii_text[0].isdigit():
        return f"col_{ascii_text}"

    return ascii_text


def parse_cell(text: str) -> Any:
    value = text.strip()
    if value == "":
        return None

    if value in {"-", "N/A", "N.A."}:
        return None

    compact = value.replace(",", "").replace(" ", "")
    if re.fullmatch(r"[-+]?\d+", compact):
        try:
            return int(compact)
        except ValueError:
            return value

    if re.fullmatch(r"[-+]?\d+\.\d+", compact):
        try:
            return float(compact)
        except ValueError:
            return value

    return value


def parse_html_tables(html: str) -> list[list[dict[str, Any]]]:
    soup = BeautifulSoup(html, "html.parser")
    parsed_tables: list[list[dict[str, Any]]] = []

    for table in soup.find_all("table"):
        header_cells = table.select("thead tr th")
        if not header_cells:
            first_header_row = table.find("tr")
            header_cells = first_header_row.find_all("th") if first_header_row else []

        headers = [normalize_header(cell.get_text(" ", strip=True)) for cell in header_cells]

        unique_headers: list[str] = []
        seen: dict[str, int] = {}
        for idx, header in enumerate(headers):
            fallback = header or f"column_{idx + 1}"
            count = seen.get(fallback, 0)
            seen[fallback] = count + 1
            unique_headers.append(fallback if count == 0 else f"{fallback}_{count + 1}")

        rows: list[dict[str, Any]] = []
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if not cells:
                continue

            values = [parse_cell(cell.get_text(" ", strip=True)) for cell in cells]
            if not unique_headers:
                unique_headers = [f"column_{i + 1}" for i in range(len(values))]

            if len(values) < len(unique_headers):
                values.extend([None] * (len(unique_headers) - len(values)))

            if len(values) > len(unique_headers):
                for i in range(len(unique_headers), len(values)):
                    unique_headers.append(f"column_{i + 1}")

            rows.append(dict(zip(unique_headers, values)))

        parsed_tables.append(rows)

    return parsed_tables
