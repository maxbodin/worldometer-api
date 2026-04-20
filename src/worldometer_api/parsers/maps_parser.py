from typing import Any

from bs4 import BeautifulSoup


def parse_maps_country_page(html: str, country_maps_path: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")

    type_paths = _extract_map_type_paths(soup)
    images = _extract_map_images(soup)

    available_types: list[str] = []
    for map_type in ("physical", "political", "road"):
        if type_paths.get(map_type):
            available_types.append(map_type)

    if images.get("locator_map_image_url"):
        available_types.append("locator")

    return {
        "maps_page_path": country_maps_path,
        "title": _extract_title(soup),
        "type_paths": type_paths,
        "images": images,
        "available_types": available_types,
    }


def parse_map_type_page(html: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")

    image_urls = _extract_all_map_images(soup)
    full_map_paths = _extract_full_map_paths(soup)

    return {
        "title": _extract_title(soup),
        "image_urls": image_urls,
        "full_map_paths": full_map_paths,
    }


def _extract_title(soup: BeautifulSoup) -> str | None:
    title_element = soup.find("h1")
    if title_element is None:
        return None

    title = title_element.get_text(" ", strip=True)
    return title or None


def _extract_map_type_paths(soup: BeautifulSoup) -> dict[str, str]:
    paths: dict[str, str] = {}

    for anchor in soup.find_all("a", href=True):
        href = _normalize_path(anchor["href"])
        if href is None:
            continue

        if href.endswith("-political-map/"):
            paths.setdefault("political", href)
            continue

        if href.endswith("-road-map/"):
            paths.setdefault("road", href)
            continue

        if href.endswith("-map/") and not href.endswith("-maps/"):
            paths.setdefault("physical", href)

    return paths


def _extract_map_images(soup: BeautifulSoup) -> dict[str, str | None]:
    country_map: str | None = None
    locator_map: str | None = None

    for image in soup.find_all("img", src=True):
        src = str(image["src"]).strip()
        if not src:
            continue

        if country_map is None and "/img/maps_c/" in src and src.endswith("-map.gif"):
            country_map = src

        if locator_map is None and "/img/maps_cl/" in src and src.endswith("-locator-map.gif"):
            locator_map = src

        if country_map and locator_map:
            break

    return {
        "country_map_image_url": country_map,
        "locator_map_image_url": locator_map,
    }


def _extract_all_map_images(soup: BeautifulSoup) -> list[str]:
    image_urls: list[str] = []
    seen: set[str] = set()

    for image in soup.find_all("img", src=True):
        src = str(image["src"]).strip()
        if not src or src in seen:
            continue

        if "/img/maps_c/" in src or "/img/maps_cl/" in src:
            seen.add(src)
            image_urls.append(src)

    return image_urls


def _extract_full_map_paths(soup: BeautifulSoup) -> list[str]:
    paths: list[str] = []
    seen: set[str] = set()

    for anchor in soup.find_all("a", href=True):
        href = _normalize_path(anchor["href"])
        if href is None or not href.endswith("-full/"):
            continue

        if href in seen:
            continue

        seen.add(href)
        paths.append(href)

    return paths


def _normalize_path(raw_href: Any) -> str | None:
    href = str(raw_href).strip()
    if not href:
        return None

    href = href.split("#", 1)[0].split("?", 1)[0]
    if not href.startswith("/"):
        return None

    if not href.startswith("/maps/"):
        return None

    return href
