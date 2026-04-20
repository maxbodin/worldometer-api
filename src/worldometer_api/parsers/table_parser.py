import re
import unicodedata
from typing import Any

from bs4 import BeautifulSoup


def _normalize_ascii(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return normalized.encode("ascii", "ignore").decode("ascii").lower().strip()


def normalize_header(text: str) -> str:
    ascii_text = _normalize_ascii(text)
    ascii_text = ascii_text.replace("%", " percent ").replace("#", " rank ")
    ascii_text = re.sub(r"\([^)]*\)", " ", ascii_text)
    ascii_text = re.sub(r"[^a-z0-9]+", "_", ascii_text)
    ascii_text = re.sub(r"_+", "_", ascii_text).strip("_")

    if not ascii_text:
        return "column"

    if ascii_text[0].isdigit():
        return f"col_{ascii_text}"

    return ascii_text


def normalize_lookup_key(text: str) -> str:
    ascii_text = _normalize_ascii(text)
    return re.sub(r"[^a-z0-9]+", "", ascii_text)


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
    titled_tables = parse_html_tables_with_titles(html)
    return [table["rows"] for table in titled_tables]


def parse_html_tables_with_titles(html: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    parsed_tables: list[dict[str, Any]] = []

    for table in soup.find_all("table"):
        title = _extract_table_title(table)
        context = _extract_table_context(table, title)
        parsed_tables.append(
            {
                "title": title,
                "source": context["source"],
                "metric": context["metric"],
                "rows": _parse_table_rows(table),
            }
        )

    return parsed_tables


def _extract_table_title(table: Any) -> str | None:
    heading = table.find_previous(["h1", "h2", "h3", "h4"])
    if heading is None:
        return None

    title = heading.get_text(" ", strip=True)
    return title or None


def _extract_table_context(table: Any, title: str | None) -> dict[str, str | None]:
    source: str | None = None
    metric: str | None = None

    for element in [table, *table.parents]:
        x_show = element.get("x-show") if hasattr(element, "get") else None
        if not isinstance(x_show, str) or not x_show.strip():
            continue

        for raw_token in re.findall(r"['\"]([a-zA-Z][a-zA-Z0-9_-]*)['\"]", x_show):
            token = normalize_lookup_key(raw_token)
            if source is None and token == "imf":
                source = "imf"
                continue

            if source is None and token in {"wb", "worldbank"}:
                source = "wb"
                continue

            if metric is None and token in {"nominal", "ppp"}:
                metric = token

        if source is not None and metric is not None:
            break

    title_key = normalize_lookup_key(title or "")
    if source is None:
        if "imf" in title_key:
            source = "imf"
        elif "worldbank" in title_key or title_key.endswith("wb"):
            source = "wb"

    if metric is None:
        if "ppp" in title_key:
            metric = "ppp"
        elif "nominal" in title_key:
            metric = "nominal"

    if metric is None:
        header_text = " ".join(th.get_text(" ", strip=True) for th in table.find_all("th"))
        header_key = normalize_lookup_key(header_text)
        if "ppp" in header_key:
            metric = "ppp"

    if metric is None:
        metric = "nominal"

    return {
        "source": source,
        "metric": metric,
    }


def _parse_table_rows(table: Any) -> list[dict[str, Any]]:
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

    return rows


def parse_population_country_links(html: str) -> dict[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if table is None:
        return {}

    country_links: dict[str, str] = {}
    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 2:
            continue

        country_cell = cells[1]
        country_name = country_cell.get_text(" ", strip=True)
        link = country_cell.find("a", href=True)

        if not country_name or link is None:
            continue

        href = str(link["href"]).strip()
        if not href:
            continue

        if not href.startswith("/"):
            href = f"/{href}"

        country_links[country_name] = href

    return country_links


def parse_country_source_index(
    html: str,
    href_prefix: str,
    slug_suffixes: tuple[str, ...] = ("-gdp", "-food-agriculture"),
) -> dict[str, tuple[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    index: dict[str, tuple[str, str]] = {}

    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if not cells:
            continue

        link = None
        link_label = ""
        for candidate in row.find_all("a", href=True):
            href = str(candidate["href"]).strip()
            if href.startswith(href_prefix):
                link = href
                link_label = candidate.get_text(" ", strip=True)
                break

        if link is None:
            continue

        country_cell_index = 1 if len(cells) > 1 else 0
        country_name = cells[country_cell_index].get_text(" ", strip=True) or link_label
        if not country_name:
            continue

        source_path = link.split("#", 1)[0].split("?", 1)[0].strip()
        if not source_path:
            continue

        if not source_path.startswith("/"):
            source_path = f"/{source_path}"

        key_variants: list[str] = []
        normalized_name = normalize_lookup_key(country_name)
        if normalized_name:
            key_variants.append(normalized_name)

        row_id = row.get("id")
        if isinstance(row_id, str):
            normalized_row_id = normalize_lookup_key(row_id)
            if normalized_row_id:
                key_variants.append(normalized_row_id)

        slug = source_path.rstrip("/").split("/")[-1]
        normalized_slug = normalize_lookup_key(slug)
        if normalized_slug:
            key_variants.append(normalized_slug)

        for suffix in slug_suffixes:
            if slug.endswith(suffix):
                normalized_without_suffix = normalize_lookup_key(slug[: -len(suffix)])
                if normalized_without_suffix:
                    key_variants.append(normalized_without_suffix)

        for key in key_variants:
            index.setdefault(key, (country_name, source_path))

    return index
