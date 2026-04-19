from urllib.parse import parse_qs, unquote, urlparse

from workers import Response

from .http import error_response, html_response, json_response
from .openapi import build_docs_html, build_openapi_spec
from .service import WorldometerApiService


class ApiRouter:
    def __init__(self) -> None:
        self._service = WorldometerApiService()

    async def handle(self, request) -> Response:
        url = urlparse(request.url)
        path = url.path.rstrip("/") or "/"
        query = parse_qs(url.query)

        try:
            if path in {"/", "/docs", "/api"}:
                return html_response(build_docs_html("/openapi.json"))

            if path == "/openapi.json":
                return json_response(build_openapi_spec())

            if path == "/live":
                return json_response(await self._service.get_live())

            payload = await self._dispatch_group_route(path, query)
            if payload is not None:
                return json_response(payload)

            return error_response("Not found", status=404)

        except LookupError as exc:
            return error_response(str(exc), status=404)
        except ValueError as exc:
            return error_response(str(exc), status=400)
        except Exception as exc:
            return error_response("Internal server error", status=500, details=str(exc))

    async def _dispatch_group_route(
        self, path: str, query: dict[str, list[str]]
    ) -> dict[str, object] | None:
        segments = [segment for segment in path.split("/") if segment]
        if not segments:
            return None

        group = segments[0]
        route_segments = segments[1:]

        if group == "population":
            return await self._handle_population_routes(route_segments, query)

        if group == "geography":
            return await self._handle_geography_routes(route_segments, query)

        if group == "energy":
            return await self._handle_energy_routes(route_segments, query)

        if group == "water":
            return await self._handle_water_routes(route_segments, query)

        if group == "gdp":
            return await self._handle_gdp_routes(route_segments, query)

        if group == "food-agriculture":
            return await self._handle_food_agriculture_routes(route_segments, query)

        if group == "ghg-emissions":
            return await self._handle_ghg_emissions_routes(route_segments, query)

        if group == "maps":
            return await self._handle_maps_routes(route_segments, query)

        return None

    async def _handle_population_routes(
        self, segments: list[str], query: dict[str, list[str]]
    ) -> dict[str, object] | None:
        if segments == ["country-codes"]:
            return await self._service.get_table_route("population/country-codes")

        if segments == ["countries"]:
            return await self._service.get_table_route("population/countries")

        if segments == ["largest-cities"]:
            return await self._service.get_table_route("population/largest-cities")

        if segments == ["by-year"]:
            return await self._service.get_table_route("population/by-year")

        if segments == ["projections"]:
            return await self._service.get_table_route("population/projections")

        if segments == ["most-populous"]:
            period = self._query_value(query, "period", "current")
            return await self._service.get_population_most_populous(period)

        if segments == ["by-region"]:
            period = self._query_value(query, "period", "current")
            return await self._service.get_population_by_region(period)

        if len(segments) == 2 and segments[0] == "region":
            dataset = self._query_value(query, "dataset", "subregions")
            return await self._service.get_population_region_dataset(segments[1], dataset)

        if len(segments) == 2 and segments[0] == "country":
            country_identifier = unquote(segments[1])
            return await self._service.get_population_country(country_identifier)

        return None

    async def _handle_geography_routes(
        self, segments: list[str], query: dict[str, list[str]]
    ) -> dict[str, object] | None:
        if segments == ["largest-countries"]:
            return await self._service.get_table_route("geography/largest-countries")

        if segments == ["world-countries"]:
            return await self._service.get_table_route("geography/world-countries")

        if len(segments) == 2 and segments[0] == "region":
            dataset = self._query_value(query, "dataset", "countries")
            return await self._service.get_geography_region_dataset(segments[1], dataset)

        return None

    async def _handle_energy_routes(
        self, segments: list[str], query: dict[str, list[str]]
    ) -> dict[str, object] | None:
        if not segments:
            return await self._service.get_table_route("energy/overview")

        if len(segments) == 2 and segments[0] == "country":
            country_identifier = unquote(segments[1])
            dataset = self._query_value(query, "dataset", "all")
            return await self._service.get_energy_country(country_identifier, dataset)

        return None

    async def _handle_water_routes(
        self, segments: list[str], query: dict[str, list[str]]
    ) -> dict[str, object] | None:
        if not segments:
            return await self._service.get_table_route("water/overview")

        if len(segments) == 2 and segments[0] == "country":
            country_identifier = unquote(segments[1])
            return await self._service.get_water_country(country_identifier)

        return None

    async def _handle_gdp_routes(
        self, segments: list[str], query: dict[str, list[str]]
    ) -> dict[str, object] | None:
        if not segments:
            dataset = self._query_value(query, "dataset", "by-country")
            return await self._service.get_gdp_overview(dataset)

        if segments == ["by-country"]:
            return await self._service.get_gdp_overview("by-country")

        if segments == ["per-capita"]:
            return await self._service.get_gdp_overview("per-capita")

        if len(segments) == 2 and segments[0] == "country":
            country_identifier = unquote(segments[1])
            return await self._service.get_gdp_country(country_identifier)

        return None

    async def _handle_food_agriculture_routes(
        self, segments: list[str], query: dict[str, list[str]]
    ) -> dict[str, object] | None:
        if not segments:
            dataset = self._query_value(query, "dataset", "undernourishment")
            return await self._service.get_food_agriculture_overview(dataset)

        if len(segments) == 1 and segments[0] in {
            "undernourishment",
            "forest",
            "cropland",
            "pesticides",
        }:
            return await self._service.get_food_agriculture_overview(segments[0])

        if len(segments) == 2 and segments[0] == "country":
            country_identifier = unquote(segments[1])
            return await self._service.get_food_agriculture_country(country_identifier)

        return None

    async def _handle_ghg_emissions_routes(
        self, segments: list[str], query: dict[str, list[str]]
    ) -> dict[str, object] | None:
        if not segments:
            return await self._service.get_ghg_emissions_overview("ghg-emissions/greenhouse/overview")

        if segments == ["greenhouse"]:
            return await self._service.get_ghg_emissions_overview("ghg-emissions/greenhouse/overview")

        if segments == ["greenhouse", "by-country"]:
            return await self._service.get_ghg_emissions_overview("ghg-emissions/greenhouse/by-country")

        if segments == ["greenhouse", "by-year"]:
            return await self._service.get_ghg_emissions_overview("ghg-emissions/greenhouse/by-year")

        if segments == ["greenhouse", "per-capita"]:
            return await self._service.get_ghg_emissions_overview("ghg-emissions/greenhouse/per-capita")

        if segments == ["co2"]:
            return await self._service.get_ghg_emissions_overview("ghg-emissions/co2/overview")

        if segments == ["co2", "by-country"]:
            return await self._service.get_ghg_emissions_overview("ghg-emissions/co2/by-country")

        if segments == ["co2", "by-year"]:
            return await self._service.get_ghg_emissions_overview("ghg-emissions/co2/by-year")

        if segments == ["co2", "per-capita"]:
            return await self._service.get_ghg_emissions_overview("ghg-emissions/co2/per-capita")

        if len(segments) == 2 and segments[0] == "country":
            country_identifier = unquote(segments[1])
            dataset = self._query_value(query, "dataset", "all")
            return await self._service.get_ghg_emissions_country(country_identifier, dataset)

        return None

    async def _handle_maps_routes(
        self, segments: list[str], query: dict[str, list[str]]
    ) -> dict[str, object] | None:
        if not segments:
            return await self._service.get_table_route("maps/overview")

        if len(segments) == 2 and segments[0] == "country":
            country_identifier = unquote(segments[1])
            return await self._service.get_maps_country(country_identifier)

        if len(segments) == 2 and segments[0] in {"physical", "political", "road", "locator"}:
            country_identifier = unquote(segments[1])
            return await self._service.get_maps_country_type(country_identifier, segments[0])

        return None

    def _query_value(self, query: dict[str, list[str]], key: str, default: str) -> str:
        return query.get(key, [default])[0]
