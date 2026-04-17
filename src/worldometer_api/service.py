from typing import Any

from .cache import TTLCache
from .config import (
    BASE_URL,
    GEOGRAPHY_REGION_DATASET_INDEX,
    POPULATION_PERIOD_TABLE_INDEX,
    REGION_ALIASES,
    REGION_GEOGRAPHY_PATHS,
    REGION_POPULATION_DATASET_INDEX,
    REGION_POPULATION_PATHS,
    TABLE_ROUTES,
)
from .live_counters_service import LiveCountersService
from .population_country_resolver import PopulationCountryResolver
from .table_service import TableService


class WorldometerApiService:
    def __init__(self) -> None:
        cache = TTLCache()
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

    def _validate_choice(self, value: str, mapping: dict[str, int], field_name: str) -> str:
        key = value.strip().lower()
        if key not in mapping:
            allowed_values = ", ".join(sorted(mapping.keys()))
            raise ValueError(f"Invalid {field_name}. Allowed values: {allowed_values}")
        return key
