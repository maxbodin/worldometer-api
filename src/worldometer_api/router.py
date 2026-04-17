from urllib.parse import parse_qs, urlparse

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

            if path == "/api/live":
                return json_response(await self._service.get_live())

            if path in {
                "/api/country-codes",
                "/api/population/countries",
                "/api/population/largest-cities",
                "/api/population/by-year",
                "/api/population/projections",
                "/api/geography/largest-countries",
                "/api/geography/world-countries",
            }:
                return json_response(await self._service.get_table_route(path))

            if path == "/api/population/most-populous":
                period = query.get("period", ["current"])[0]
                return json_response(await self._service.get_population_most_populous(period))

            if path == "/api/population/by-region":
                period = query.get("period", ["current"])[0]
                return json_response(await self._service.get_population_by_region(period))

            segments = [segment for segment in path.split("/") if segment]
            if len(segments) == 4 and segments[:3] == ["api", "population", "region"]:
                region = segments[3]
                dataset = query.get("dataset", ["subregions"])[0]
                return json_response(await self._service.get_population_region_dataset(region, dataset))

            if len(segments) == 4 and segments[:3] == ["api", "geography", "region"]:
                region = segments[3]
                dataset = query.get("dataset", ["countries"])[0]
                return json_response(await self._service.get_geography_region_dataset(region, dataset))

            return error_response("Not found", status=404)

        except LookupError as exc:
            return error_response(str(exc), status=404)
        except ValueError as exc:
            return error_response(str(exc), status=400)
        except Exception as exc:
            return error_response("Internal server error", status=500, details=str(exc))
