from dataclasses import dataclass

from .cache import TTLCache
from .config import (
    BASE_URL,
    COUNTRY_CODES_SOURCE_PATH,
    COUNTRY_LOOKUP_CACHE_TTL_SECONDS,
    POPULATION_BY_COUNTRY_SOURCE_PATH,
)
from .fetcher import fetch_text
from .parsers.table_parser import normalize_lookup_key, parse_population_country_links
from .table_service import TableService


@dataclass(frozen=True)
class PopulationCountryMatch:
    country: str
    source_path: str
    matched_by: str

    @property
    def country_slug(self) -> str:
        source_slug = self.source_path.rstrip("/").split("/")[-1]
        if source_slug.endswith("-population"):
            return source_slug[: -len("-population")]
        return source_slug


class PopulationCountryResolver:
    def __init__(self, table_service: TableService, cache: TTLCache) -> None:
        self._table_service = table_service
        self._cache = cache

    async def resolve(self, country_identifier: str) -> PopulationCountryMatch:
        normalized_identifier = normalize_lookup_key(country_identifier)
        if not normalized_identifier:
            raise ValueError("country identifier is required")

        source_index = await self._get_population_source_index()
        direct_match = source_index.get(normalized_identifier)
        if direct_match is not None:
            country, source_path = direct_match
            return PopulationCountryMatch(country=country, source_path=source_path, matched_by="name")

        code_index = await self._get_country_code_index()
        code_match = code_index.get(normalized_identifier)
        if code_match is not None:
            country_name, code_type = code_match
            source_match = source_index.get(normalize_lookup_key(country_name))
            if source_match is None:
                raise LookupError(f"Population source path not found for country: {country_name}")

            country, source_path = source_match
            return PopulationCountryMatch(country=country, source_path=source_path, matched_by=code_type)

        raise LookupError(f"Unknown country identifier: {country_identifier}")

    async def _get_population_source_index(self) -> dict[str, tuple[str, str]]:
        cache_key = "population:country-source-index"
        cached = self._cache.get(cache_key, COUNTRY_LOOKUP_CACHE_TTL_SECONDS)
        if cached is not None:
            return cached

        html = await fetch_text(f"{BASE_URL}{POPULATION_BY_COUNTRY_SOURCE_PATH}")
        country_links = parse_population_country_links(html)

        index: dict[str, tuple[str, str]] = {}
        for country_name, source_path in country_links.items():
            normalized_name = normalize_lookup_key(country_name)
            if normalized_name:
                index[normalized_name] = (country_name, source_path)

            slug = source_path.rstrip("/").split("/")[-1]
            if slug:
                normalized_slug = normalize_lookup_key(slug)
                if normalized_slug:
                    index.setdefault(normalized_slug, (country_name, source_path))

                if slug.endswith("-population"):
                    normalized_slug_without_suffix = normalize_lookup_key(slug[: -len("-population")])
                    if normalized_slug_without_suffix:
                        index.setdefault(normalized_slug_without_suffix, (country_name, source_path))

        return self._cache.set(cache_key, index)

    async def _get_country_code_index(self) -> dict[str, tuple[str, str]]:
        cache_key = "population:country-code-index"
        cached = self._cache.get(cache_key, COUNTRY_LOOKUP_CACHE_TTL_SECONDS)
        if cached is not None:
            return cached

        rows = await self._table_service.get_table(COUNTRY_CODES_SOURCE_PATH, 0)
        index: dict[str, tuple[str, str]] = {}

        for row in rows:
            country_name = self._as_text(
                self._first_present(
                    row,
                    (
                        "country_or_dependency",
                        "country",
                    ),
                )
            )
            if not country_name:
                continue

            alpha2 = self._as_text(
                self._first_present(
                    row,
                    (
                        "col_2_letter_iso",
                        "two_letter_iso",
                        "alpha2",
                    ),
                )
            )
            alpha3 = self._as_text(
                self._first_present(
                    row,
                    (
                        "col_3_letter_iso",
                        "three_letter_iso",
                        "alpha3",
                    ),
                )
            )

            if alpha2:
                index[normalize_lookup_key(alpha2)] = (country_name, "alpha2")

            if alpha3:
                index[normalize_lookup_key(alpha3)] = (country_name, "alpha3")

        return self._cache.set(cache_key, index)

    def _as_text(self, value: object | None) -> str:
        if value is None:
            return ""
        return str(value).strip()

    def _first_present(self, row: dict[str, object], preferred_keys: tuple[str, ...]) -> object | None:
        for key in preferred_keys:
            if key in row:
                return row[key]

        normalized_row = {normalize_lookup_key(key): value for key, value in row.items()}
        for key in preferred_keys:
            normalized_key = normalize_lookup_key(key)
            if normalized_key in normalized_row:
                return normalized_row[normalized_key]

        return None
