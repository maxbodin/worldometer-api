from typing import Any

from .cache import TTLCache
from .config import (
    BASE_URL,
    COUNTRY_LOOKUP_CACHE_TTL_SECONDS,
    ENERGY_COUNTRY_DATASET_CHOICES,
    ENERGY_COUNTRY_DATASET_SOURCE_TEMPLATES,
    GHG_CO2_COUNTRY_SOURCE_INDEX_PATHS,
    GHG_COUNTRY_DATASET_CHOICES,
    GHG_GREENHOUSE_COUNTRY_SOURCE_INDEX_PATHS,
    FOOD_AGRICULTURE_COUNTRY_SOURCE_INDEX_PATHS,
    FOOD_AGRICULTURE_DATASET_CHOICES,
    MAPS_COUNTRY_SOURCE_INDEX_PATHS,
    MAPS_TYPE_CHOICES,
    GDP_COUNTRY_SOURCE_INDEX_PATHS,
    GDP_DATASET_CHOICES,
    GEOGRAPHY_REGION_DATASET_INDEX,
    POPULATION_PERIOD_TABLE_INDEX,
    REGION_ALIASES,
    REGION_GEOGRAPHY_PATHS,
    REGION_POPULATION_DATASET_INDEX,
    REGION_POPULATION_PATHS,
    TABLE_ROUTES,
    WATER_COUNTRY_SOURCE_TEMPLATE,
)
from .energy_parser import parse_energy_country_summary
from .fetcher import fetch_text
from .food_agriculture_parser import parse_food_agriculture_country_summary
from .gdp_parser import parse_gdp_country_description
from .live_counters_service import LiveCountersService
from .maps_parser import parse_map_type_page, parse_maps_country_page
from .population_country_resolver import PopulationCountryResolver
from .table_parser import normalize_lookup_key, parse_country_source_index
from .table_service import TableService
from .water_parser import parse_water_country_summary


class WorldometerApiService:
    def __init__(self) -> None:
        cache = TTLCache()
        self._cache = cache
        self._table_service = TableService(cache)
        self._live_service = LiveCountersService(cache)
        self._population_country_resolver = PopulationCountryResolver(self._table_service, cache)

    async def get_live(self) -> dict[str, object]:
        return await self._live_service.get_live_counters()

    async def get_table_route(self, route_key: str) -> dict[str, Any]:
        if route_key not in TABLE_ROUTES:
            raise LookupError("Route not found.")

        source_path, table_index = TABLE_ROUTES[route_key]
        table = await self._table_service.get_titled_table(source_path, table_index)
        rows = table.get("rows") if isinstance(table.get("rows"), list) else []
        table_title = self._as_optional_text(table.get("title"))

        return {
            "route_key": route_key,
            "source_path": source_path,
            "table_index": table_index,
            "table_title": table_title,
            "rows": rows,
            "count": len(rows),
        }

    async def get_population_country(self, country_identifier: str) -> dict[str, Any]:
        match = await self._population_country_resolver.resolve(country_identifier)
        titled_tables = await self._table_service.get_titled_tables(match.source_path)
        tables = self._build_indexed_tables_payload(titled_tables)
        return {
            "country": match.country,
            "country_identifier": country_identifier,
            "matched_by": match.matched_by,
            "source_path": match.source_path,
            "source_url": f"{BASE_URL}{match.source_path}",
            "table_count": len(tables),
            "tables": tables,
        }

    async def get_energy_country(self, country_identifier: str, dataset: str) -> dict[str, Any]:
        match = await self._population_country_resolver.resolve(country_identifier)
        dataset_key = self._validate_choice(dataset, ENERGY_COUNTRY_DATASET_CHOICES, "dataset")

        if dataset_key == "all":
            dataset_keys = list(ENERGY_COUNTRY_DATASET_SOURCE_TEMPLATES.keys())
        else:
            dataset_keys = [dataset_key]

        datasets: list[dict[str, Any]] = []
        for current_dataset in dataset_keys:
            source_path = ENERGY_COUNTRY_DATASET_SOURCE_TEMPLATES[current_dataset].format(
                country_slug=match.country_slug
            )
            datasets.append(
                await self._get_energy_country_dataset_payload(
                    dataset_key=current_dataset,
                    source_path=source_path,
                    country_name=match.country,
                )
            )

        return {
            "country": match.country,
            "country_identifier": country_identifier,
            "matched_by": match.matched_by,
            "country_slug": match.country_slug,
            "dataset": dataset_key,
            "dataset_count": len(datasets),
            "datasets": datasets,
        }

    async def get_water_country(self, country_identifier: str) -> dict[str, Any]:
        match = await self._population_country_resolver.resolve(country_identifier)
        source_path = WATER_COUNTRY_SOURCE_TEMPLATE.format(country_slug=match.country_slug)

        html = await fetch_text(f"{BASE_URL}{source_path}")
        parsed_payload = parse_water_country_summary(html)
        if not parsed_payload:
            raise LookupError(f"Water dataset is not available for country: {match.country}")

        return {
            "country": match.country,
            "country_identifier": country_identifier,
            "matched_by": match.matched_by,
            "country_slug": match.country_slug,
            "source_path": source_path,
            "source_url": f"{BASE_URL}{source_path}",
            **parsed_payload,
        }

    async def get_gdp_overview(self, dataset: str) -> dict[str, Any]:
        dataset_key = self._validate_choice(dataset, GDP_DATASET_CHOICES, "dataset")
        payload = await self.get_table_route(f"gdp/{dataset_key}")
        payload["dataset"] = dataset_key
        return payload

    async def get_gdp_country(self, country_identifier: str) -> dict[str, Any]:
        match = await self._population_country_resolver.resolve(country_identifier)
        source_index = await self._get_gdp_country_source_index()
        source_path = self._resolve_country_source_path(
            country_identifier=country_identifier,
            country_name=match.country,
            country_slug=match.country_slug,
            source_index=source_index,
            dataset_name="GDP",
        )

        html = await self._table_service.get_page_html(source_path)
        description = parse_gdp_country_description(html)

        titled_tables = await self._table_service.get_titled_tables(source_path)
        tables = self._build_indexed_tables_payload(titled_tables)
        if not tables:
            raise LookupError(f"GDP dataset is not available for country: {match.country}")

        return {
            "country": match.country,
            "country_identifier": country_identifier,
            "matched_by": match.matched_by,
            "country_slug": match.country_slug,
            "source_path": source_path,
            "source_url": f"{BASE_URL}{source_path}",
            "description": description,
            "table_count": len(tables),
            "tables": tables,
        }

    async def get_food_agriculture_overview(self, dataset: str) -> dict[str, Any]:
        dataset_key = self._validate_choice(dataset, FOOD_AGRICULTURE_DATASET_CHOICES, "dataset")
        payload = await self.get_table_route(f"food-agriculture/{dataset_key}")
        payload["dataset"] = dataset_key
        return payload

    async def get_food_agriculture_country(self, country_identifier: str) -> dict[str, Any]:
        match = await self._population_country_resolver.resolve(country_identifier)
        source_index = await self._get_food_agriculture_country_source_index()
        source_path = self._resolve_country_source_path(
            country_identifier=country_identifier,
            country_name=match.country,
            country_slug=match.country_slug,
            source_index=source_index,
            dataset_name="Food & Agriculture",
        )

        try:
            html = await fetch_text(f"{BASE_URL}{source_path}")
        except ValueError as exc:
            raise LookupError(
                f"Food & Agriculture dataset is not available for country: {match.country}"
            ) from exc

        parsed_payload = parse_food_agriculture_country_summary(html)
        if not parsed_payload:
            raise LookupError(f"Food & Agriculture dataset is not available for country: {match.country}")

        return {
            "country": match.country,
            "country_identifier": country_identifier,
            "matched_by": match.matched_by,
            "country_slug": match.country_slug,
            "source_path": source_path,
            "source_url": f"{BASE_URL}{source_path}",
            **parsed_payload,
        }

    async def get_ghg_emissions_overview(self, route_key: str) -> dict[str, Any]:
        return await self.get_table_route(route_key)

    async def get_ghg_emissions_country(
        self,
        country_identifier: str,
        dataset: str,
    ) -> dict[str, Any]:
        match = await self._population_country_resolver.resolve(country_identifier)
        dataset_key = self._validate_choice(dataset, GHG_COUNTRY_DATASET_CHOICES, "dataset")

        if dataset_key == "all":
            dataset_keys = ["greenhouse", "co2"]
        else:
            dataset_keys = [dataset_key]

        source_indexes = {
            "greenhouse": await self._get_ghg_greenhouse_country_source_index(),
            "co2": await self._get_ghg_co2_country_source_index(),
        }

        suffixes = {
            "greenhouse": "-greenhouse-gas-emissions",
            "co2": "-co2-emissions",
        }

        datasets: list[dict[str, Any]] = []
        for current_dataset in dataset_keys:
            source_path = self._resolve_country_source_path(
                country_identifier=country_identifier,
                country_name=match.country,
                country_slug=match.country_slug,
                source_index=source_indexes[current_dataset],
                dataset_name=f"GHG {current_dataset}",
                extra_lookup_suffix=suffixes[current_dataset],
            )

            table_entries = self._build_indexed_tables_payload(
                await self._table_service.get_titled_tables(source_path)
            )
            if not table_entries:
                raise LookupError(
                    f"GHG {current_dataset} dataset is not available for country: {match.country}"
                )

            datasets.append(
                {
                    "dataset": current_dataset,
                    "source_path": source_path,
                    "source_url": f"{BASE_URL}{source_path}",
                    "table_count": len(table_entries),
                    "tables": table_entries,
                }
            )

        return {
            "country": match.country,
            "country_identifier": country_identifier,
            "matched_by": match.matched_by,
            "country_slug": match.country_slug,
            "dataset": dataset_key,
            "dataset_count": len(datasets),
            "datasets": datasets,
        }

    async def get_maps_country(self, country_identifier: str) -> dict[str, Any]:
        payload = await self._build_maps_country_payload(country_identifier)
        return {
            "country": payload["country"],
            "country_identifier": payload["country_identifier"],
            "matched_by": payload["matched_by"],
            "country_slug": payload["country_slug"],
            "maps_page_path": payload["maps_page_path"],
            "maps_page_url": payload["maps_page_url"],
            "available_types": payload["available_types"],
            "types": payload["types"],
            "all_image_urls": payload["all_image_urls"],
        }

    async def get_maps_country_type(self, country_identifier: str, map_type: str) -> dict[str, Any]:
        map_type_key = self._validate_choice(map_type, MAPS_TYPE_CHOICES, "map_type")
        if map_type_key == "all":
            raise ValueError("map_type must be one of: physical, political, road, locator")

        payload = await self._build_maps_country_payload(country_identifier)
        type_payload = payload["types"].get(map_type_key)
        if not isinstance(type_payload, dict):
            raise LookupError(
                f"Map type '{map_type_key}' is not available for country: {payload['country']}"
            )

        return {
            "country": payload["country"],
            "country_identifier": payload["country_identifier"],
            "matched_by": payload["matched_by"],
            "country_slug": payload["country_slug"],
            "maps_page_path": payload["maps_page_path"],
            "maps_page_url": payload["maps_page_url"],
            "map_type": map_type_key,
            "map": type_payload,
        }

    async def get_population_most_populous(self, period: str) -> dict[str, Any]:
        period_key = self._validate_choice(period, POPULATION_PERIOD_TABLE_INDEX, "period")
        source_path = "/population/most-populous-countries/"
        rows = await self._table_service.get_table(source_path, POPULATION_PERIOD_TABLE_INDEX[period_key])
        return {
            "source_path": source_path,
            "period": period_key,
            "rows": rows,
            "count": len(rows),
        }

    async def get_population_by_region(self, period: str) -> dict[str, Any]:
        period_key = self._validate_choice(period, POPULATION_PERIOD_TABLE_INDEX, "period")
        source_path = "/world-population/population-by-region/"
        rows = await self._table_service.get_table(source_path, POPULATION_PERIOD_TABLE_INDEX[period_key])
        return {
            "source_path": source_path,
            "period": period_key,
            "rows": rows,
            "count": len(rows),
        }

    async def get_population_region_dataset(self, region: str, dataset: str) -> dict[str, Any]:
        region_key = self._normalize_region(region)
        if region_key not in REGION_POPULATION_PATHS:
            raise LookupError(f"Unknown region: {region}")

        dataset_key = self._validate_choice(dataset, REGION_POPULATION_DATASET_INDEX, "dataset")
        source_path = REGION_POPULATION_PATHS[region_key]
        rows = await self._table_service.get_table(source_path, REGION_POPULATION_DATASET_INDEX[dataset_key])
        return {
            "source_path": source_path,
            "region": region_key,
            "dataset": dataset_key,
            "rows": rows,
            "count": len(rows),
        }

    async def get_geography_region_dataset(self, region: str, dataset: str) -> dict[str, Any]:
        region_key = self._normalize_region(region)
        if region_key not in REGION_GEOGRAPHY_PATHS:
            raise LookupError(f"Unknown region: {region}")

        dataset_key = self._validate_choice(dataset, GEOGRAPHY_REGION_DATASET_INDEX, "dataset")
        source_path = REGION_GEOGRAPHY_PATHS[region_key]
        rows = await self._table_service.get_table(source_path, GEOGRAPHY_REGION_DATASET_INDEX[dataset_key])
        return {
            "source_path": source_path,
            "region": region_key,
            "dataset": dataset_key,
            "rows": rows,
            "count": len(rows),
        }

    def _normalize_region(self, region: str) -> str:
        normalized = region.strip().lower().replace("_", "-")
        return REGION_ALIASES.get(normalized, normalized)

    async def _get_energy_country_dataset_payload(
        self,
        dataset_key: str,
        source_path: str,
        country_name: str,
    ) -> dict[str, Any]:
        try:
            if dataset_key == "energy":
                html = await fetch_text(f"{BASE_URL}{source_path}")
                rows = parse_energy_country_summary(html)
                if not rows:
                    raise LookupError(
                        f"Energy dataset '{dataset_key}' is not available for country: {country_name}"
                    )

                tables = [
                    {
                        "index": 0,
                        "title": None,
                        "count": len(rows),
                        "rows": rows,
                    }
                ]
            else:
                raw_titled_tables = await self._table_service.get_titled_tables(source_path)
                tables = self._build_indexed_tables_payload(raw_titled_tables)
                if not tables:
                    raise LookupError(
                        f"Energy dataset '{dataset_key}' is not available for country: {country_name}"
                    )

            return {
                "dataset": dataset_key,
                "source_path": source_path,
                "source_url": f"{BASE_URL}{source_path}",
                "table_count": len(tables),
                "tables": tables,
            }
        except ValueError as exc:
            raise LookupError(
                f"Energy dataset '{dataset_key}' is not available for country: {country_name}"
            ) from exc

    async def _get_gdp_country_source_index(self) -> dict[str, tuple[str, str]]:
        return await self._build_country_source_index(
            cache_key="gdp:country-source-index",
            source_paths=GDP_COUNTRY_SOURCE_INDEX_PATHS,
            href_prefix="/gdp/",
            slug_suffixes=("-gdp",),
        )

    async def _get_food_agriculture_country_source_index(self) -> dict[str, tuple[str, str]]:
        return await self._build_country_source_index(
            cache_key="food-agriculture:country-source-index",
            source_paths=FOOD_AGRICULTURE_COUNTRY_SOURCE_INDEX_PATHS,
            href_prefix="/food-agriculture/",
            slug_suffixes=("-food-agriculture",),
        )

    async def _get_ghg_greenhouse_country_source_index(self) -> dict[str, tuple[str, str]]:
        return await self._build_country_source_index(
            cache_key="ghg-emissions:greenhouse-country-source-index",
            source_paths=GHG_GREENHOUSE_COUNTRY_SOURCE_INDEX_PATHS,
            href_prefix="/greenhouse-gas-emissions/",
            slug_suffixes=("-greenhouse-gas-emissions",),
        )

    async def _get_ghg_co2_country_source_index(self) -> dict[str, tuple[str, str]]:
        return await self._build_country_source_index(
            cache_key="ghg-emissions:co2-country-source-index",
            source_paths=GHG_CO2_COUNTRY_SOURCE_INDEX_PATHS,
            href_prefix="/co2-emissions/",
            slug_suffixes=("-co2-emissions",),
        )

    async def _get_maps_country_source_index(self) -> dict[str, tuple[str, str]]:
        return await self._build_country_source_index(
            cache_key="maps:country-source-index",
            source_paths=MAPS_COUNTRY_SOURCE_INDEX_PATHS,
            href_prefix="/maps/",
            slug_suffixes=("-maps",),
        )

    async def _build_maps_country_payload(self, country_identifier: str) -> dict[str, Any]:
        match = await self._population_country_resolver.resolve(country_identifier)
        source_index = await self._get_maps_country_source_index()
        maps_page_path = self._resolve_country_source_path(
            country_identifier=country_identifier,
            country_name=match.country,
            country_slug=match.country_slug,
            source_index=source_index,
            dataset_name="Maps",
            extra_lookup_suffix="-maps",
        )

        maps_page_html = await fetch_text(f"{BASE_URL}{maps_page_path}")
        parsed_country_page = parse_maps_country_page(maps_page_html, maps_page_path)

        type_paths = parsed_country_page.get("type_paths")
        if not isinstance(type_paths, dict):
            raise LookupError(f"Maps dataset is not available for country: {match.country}")

        types: dict[str, dict[str, Any]] = {}
        all_image_urls: list[str] = []
        seen_image_urls: set[str] = set()

        for map_type in ("physical", "political", "road"):
            type_path = type_paths.get(map_type)
            if not isinstance(type_path, str) or not type_path:
                continue

            type_payload = await self._build_map_type_payload(type_path)
            types[map_type] = type_payload

            for image_url in type_payload.get("image_urls", []):
                if isinstance(image_url, str) and image_url and image_url not in seen_image_urls:
                    seen_image_urls.add(image_url)
                    all_image_urls.append(image_url)

        images = parsed_country_page.get("images")
        locator_image_url = images.get("locator_map_image_url") if isinstance(images, dict) else None
        if isinstance(locator_image_url, str) and locator_image_url:
            locator_image_url = self._to_absolute_worldometer_url(locator_image_url)
            types["locator"] = {
                "title": "Locator map",
                "image_urls": [locator_image_url],
                "full_map_paths": [],
            }
            if locator_image_url not in seen_image_urls:
                seen_image_urls.add(locator_image_url)
                all_image_urls.append(locator_image_url)

        if not types:
            raise LookupError(f"Maps dataset is not available for country: {match.country}")

        available_types = [
            map_type for map_type in ("physical", "political", "road", "locator") if map_type in types
        ]

        return {
            "country": match.country,
            "country_identifier": country_identifier,
            "matched_by": match.matched_by,
            "country_slug": match.country_slug,
            "maps_page_path": maps_page_path,
            "maps_page_url": f"{BASE_URL}{maps_page_path}",
            "available_types": available_types,
            "types": types,
            "all_image_urls": all_image_urls,
        }

    async def _build_map_type_payload(self, source_path: str) -> dict[str, Any]:
        html = await fetch_text(f"{BASE_URL}{source_path}")
        parsed_payload = parse_map_type_page(html)

        raw_image_urls = parsed_payload.get("image_urls")
        image_urls: list[str] = []
        seen_image_urls: set[str] = set()
        if isinstance(raw_image_urls, list):
            for image_url in raw_image_urls:
                if not isinstance(image_url, str):
                    continue

                normalized_image_url = self._to_absolute_worldometer_url(image_url)
                if not normalized_image_url or normalized_image_url in seen_image_urls:
                    continue

                seen_image_urls.add(normalized_image_url)
                image_urls.append(normalized_image_url)

        full_map_paths = parsed_payload.get("full_map_paths")
        if not isinstance(full_map_paths, list):
            full_map_paths = []

        return {
            "title": parsed_payload.get("title"),
            "source_path": source_path,
            "source_url": f"{BASE_URL}{source_path}",
            "image_urls": image_urls,
            "full_map_paths": full_map_paths,
            "full_map_urls": [f"{BASE_URL}{path}" for path in full_map_paths],
        }

    def _to_absolute_worldometer_url(self, url: str) -> str:
        normalized = url.strip()
        if not normalized:
            return ""

        if normalized.startswith("https://") or normalized.startswith("http://"):
            return normalized

        if normalized.startswith("/"):
            return f"{BASE_URL}{normalized}"

        return normalized

    def _build_indexed_tables_payload(self, titled_tables: list[dict[str, Any]]) -> list[dict[str, Any]]:
        tables: list[dict[str, Any]] = []
        for index, table in enumerate(titled_tables):
            rows = table.get("rows") if isinstance(table.get("rows"), list) else []
            tables.append(
                {
                    "index": index,
                    "title": self._as_optional_text(table.get("title")),
                    "count": len(rows),
                    "rows": rows,
                }
            )

        return tables

    def _as_optional_text(self, value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    async def _build_country_source_index(
        self,
        cache_key: str,
        source_paths: list[str],
        href_prefix: str,
        slug_suffixes: tuple[str, ...] = (),
    ) -> dict[str, tuple[str, str]]:
        cached = self._cache.get(cache_key, COUNTRY_LOOKUP_CACHE_TTL_SECONDS)
        if cached is not None:
            return cached

        index: dict[str, tuple[str, str]] = {}
        for source_path in source_paths:
            html = await fetch_text(f"{BASE_URL}{source_path}")
            parsed = parse_country_source_index(
                html,
                href_prefix,
                slug_suffixes=slug_suffixes,
            )
            for key, value in parsed.items():
                index.setdefault(key, value)

        if not index:
            raise LookupError("Country source index is unavailable")

        return self._cache.set(cache_key, index)

    def _resolve_country_source_path(
        self,
        country_identifier: str,
        country_name: str,
        country_slug: str,
        source_index: dict[str, tuple[str, str]],
        dataset_name: str,
        extra_lookup_suffix: str = "",
    ) -> str:
        candidate_keys: list[str] = []
        for raw_key in (country_name, country_slug, country_identifier):
            normalized = normalize_lookup_key(raw_key)
            if normalized and normalized not in candidate_keys:
                candidate_keys.append(normalized)

        if extra_lookup_suffix:
            suffix_key = normalize_lookup_key(f"{country_slug}{extra_lookup_suffix}")
            if suffix_key and suffix_key not in candidate_keys:
                candidate_keys.append(suffix_key)

        for key in candidate_keys:
            match = source_index.get(key)
            if match is not None:
                _, source_path = match
                return source_path

        raise LookupError(f"{dataset_name} dataset is not available for country: {country_name}")

    def _validate_choice(self, value: str, mapping: dict[str, int], field_name: str) -> str:
        key = value.strip().lower()
        if key not in mapping:
            allowed_values = ", ".join(sorted(mapping.keys()))
            raise ValueError(f"Invalid {field_name}. Allowed values: {allowed_values}")
        return key
