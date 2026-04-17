from typing import Any

from .cache import TTLCache
from .config import (
    BASE_URL,
    COUNTRY_LOOKUP_CACHE_TTL_SECONDS,
    ENERGY_COUNTRY_DATASET_CHOICES,
    ENERGY_COUNTRY_DATASET_SOURCE_TEMPLATES,
    FOOD_AGRICULTURE_COUNTRY_SOURCE_INDEX_PATHS,
    FOOD_AGRICULTURE_DATASET_CHOICES,
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
from .live_counters_service import LiveCountersService
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
        rows = await self._table_service.get_table(source_path, table_index)
        return {
            "route_key": route_key,
            "source_path": source_path,
            "rows": rows,
            "count": len(rows),
        }

    async def get_population_country(self, country_identifier: str) -> dict[str, Any]:
        match = await self._population_country_resolver.resolve(country_identifier)
        tables = await self._table_service.get_tables(match.source_path)
        return {
            "country": match.country,
            "country_identifier": country_identifier,
            "matched_by": match.matched_by,
            "source_path": match.source_path,
            "source_url": f"{BASE_URL}{match.source_path}",
            "table_count": len(tables),
            "tables": [
                {
                    "index": index,
                    "count": len(rows),
                    "rows": rows,
                }
                for index, rows in enumerate(tables)
            ],
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

        tables = await self._table_service.get_tables(source_path)
        if not tables:
            raise LookupError(f"GDP dataset is not available for country: {match.country}")

        return {
            "country": match.country,
            "country_identifier": country_identifier,
            "matched_by": match.matched_by,
            "country_slug": match.country_slug,
            "source_path": source_path,
            "source_url": f"{BASE_URL}{source_path}",
            "table_count": len(tables),
            "tables": [
                {
                    "index": index,
                    "count": len(rows),
                    "rows": rows,
                }
                for index, rows in enumerate(tables)
            ],
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
                        "count": len(rows),
                        "rows": rows,
                    }
                ]
            else:
                raw_tables = await self._table_service.get_tables(source_path)
                if not raw_tables:
                    raise LookupError(
                        f"Energy dataset '{dataset_key}' is not available for country: {country_name}"
                    )

                tables = [
                    {
                        "index": index,
                        "count": len(rows),
                        "rows": rows,
                    }
                    for index, rows in enumerate(raw_tables)
                ]

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
        )

    async def _get_food_agriculture_country_source_index(self) -> dict[str, tuple[str, str]]:
        return await self._build_country_source_index(
            cache_key="food-agriculture:country-source-index",
            source_paths=FOOD_AGRICULTURE_COUNTRY_SOURCE_INDEX_PATHS,
            href_prefix="/food-agriculture/",
        )

    async def _build_country_source_index(
        self,
        cache_key: str,
        source_paths: list[str],
        href_prefix: str,
    ) -> dict[str, tuple[str, str]]:
        cached = self._cache.get(cache_key, COUNTRY_LOOKUP_CACHE_TTL_SECONDS)
        if cached is not None:
            return cached

        index: dict[str, tuple[str, str]] = {}
        for source_path in source_paths:
            html = await fetch_text(f"{BASE_URL}{source_path}")
            parsed = parse_country_source_index(html, href_prefix)
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
    ) -> str:
        candidate_keys: list[str] = []
        for raw_key in (country_name, country_slug, country_identifier):
            normalized = normalize_lookup_key(raw_key)
            if normalized and normalized not in candidate_keys:
                candidate_keys.append(normalized)

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
