from html import escape
from typing import Any


SCALAR_API_REFERENCE_JS_URL = "https://cdn.jsdelivr.net/npm/@scalar/api-reference@1.52.2"


def build_openapi_spec() -> dict[str, Any]:
    paths: dict[str, dict[str, Any]] = {
            "/": {
                "get": {
                    "summary": "OpenAPI documentation page",
                    "responses": {"200": {"description": "Scalar documentation UI"}},
                }
            },
            "/docs": {
                "get": {
                    "summary": "OpenAPI documentation page",
                    "responses": {"200": {"description": "Scalar documentation UI"}},
                }
            },
            "/api": {
                "get": {
                    "summary": "OpenAPI documentation page",
                    "responses": {"200": {"description": "Scalar documentation UI"}},
                }
            },
            "/openapi.json": {
                "get": {
                    "summary": "OpenAPI specification",
                    "responses": {"200": {"description": "OpenAPI document"}},
                }
            },
            "/live": {
                "get": {
                    "summary": "Live counters",
                    "responses": {
                        "200": {
                            "description": "Live counters grouped by section",
                        }
                    },
                }
            },
            "/population/country-codes": {
                "get": {
                    "summary": "Country codes",
                    "responses": {"200": {"description": "Country codes table"}},
                }
            },
            "/population/countries": {
                "get": {
                    "summary": "Countries by population",
                    "responses": {"200": {"description": "Population-by-country table"}},
                }
            },
            "/population/largest-cities": {
                "get": {
                    "summary": "Largest cities",
                    "responses": {"200": {"description": "Largest cities table"}},
                }
            },
            "/population/by-year": {
                "get": {
                    "summary": "Population by year",
                    "responses": {"200": {"description": "Historical world population table"}},
                }
            },
            "/population/projections": {
                "get": {
                    "summary": "Population projections",
                    "responses": {"200": {"description": "Projected world population table"}},
                }
            },
            "/geography/largest-countries": {
                "get": {
                    "summary": "Largest countries",
                    "responses": {"200": {"description": "Largest countries table"}},
                }
            },
            "/geography/world-countries": {
                "get": {
                    "summary": "World countries",
                    "responses": {"200": {"description": "World countries table"}},
                }
            },
            "/energy": {
                "get": {
                    "summary": "Energy consumption by country",
                    "responses": {"200": {"description": "Energy consumption table"}},
                }
            },
            "/water": {
                "get": {
                    "summary": "Water use by country",
                    "responses": {"200": {"description": "Water use table by country"}},
                }
            },
            "/population/most-populous": {
                "get": {
                    "summary": "Most populous countries",
                    "parameters": [
                        {
                            "name": "period",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string", "enum": ["current", "past", "future"], "default": "current"},
                        }
                    ],
                    "responses": {"200": {"description": "Most populous countries data by period"}, "400": {"description": "Invalid period"}},
                }
            },
            "/population/by-region": {
                "get": {
                    "summary": "Population by region",
                    "parameters": [
                        {
                            "name": "period",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string", "enum": ["current", "past", "future"], "default": "current"},
                        }
                    ],
                    "responses": {"200": {"description": "Population by region and period"}, "400": {"description": "Invalid period"}},
                }
            },
            "/population/region/{region}": {
                "get": {
                    "summary": "Region-specific population datasets",
                    "parameters": [
                        {
                            "name": "region",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "string",
                                "enum": [
                                    "asia",
                                    "africa",
                                    "europe",
                                    "latin-america",
                                    "northern-america",
                                    "oceania",
                                ],
                            },
                        },
                        {
                            "name": "dataset",
                            "in": "query",
                            "required": False,
                            "schema": {
                                "type": "string",
                                "enum": ["subregions", "historical", "forecast"],
                                "default": "subregions",
                            },
                        },
                    ],
                    "responses": {
                        "200": {"description": "Region population dataset"},
                        "400": {"description": "Invalid dataset"},
                        "404": {"description": "Unknown region"},
                    },
                }
            },
            "/population/country/{countryIdentifier}": {
                "get": {
                    "summary": "Country population data",
                    "description": "Resolve by country name, ISO2, or ISO3 alpha code.",
                    "parameters": [
                        {
                            "name": "countryIdentifier",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "examples": {
                                "countryName": {"value": "afghanistan"},
                                "alpha2": {"value": "AF"},
                                "alpha3": {"value": "AFG"},
                            },
                        }
                    ],
                    "responses": {
                        "200": {"description": "Country population datasets parsed from country page"},
                        "404": {"description": "Country not found"},
                    },
                }
            },
            "/energy/country/{countryIdentifier}": {
                "get": {
                    "summary": "Country energy datasets",
                    "description": "Resolve by country name, ISO2, or ISO3 alpha code.",
                    "parameters": [
                        {
                            "name": "countryIdentifier",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "examples": {
                                "countryName": {"value": "china"},
                                "alpha2": {"value": "CN"},
                                "alpha3": {"value": "CHN"},
                            },
                        },
                        {
                            "name": "dataset",
                            "in": "query",
                            "required": False,
                            "schema": {
                                "type": "string",
                                "enum": ["all", "energy", "electricity", "gas", "oil", "coal"],
                                "default": "all",
                            },
                        },
                    ],
                    "responses": {
                        "200": {"description": "Country energy datasets parsed from source pages"},
                        "400": {"description": "Invalid dataset"},
                        "404": {"description": "Country or dataset not found"},
                    },
                }
            },
            "/water/country/{countryIdentifier}": {
                "get": {
                    "summary": "Country water datasets",
                    "description": "Resolve by country name, ISO2, or ISO3 alpha code.",
                    "parameters": [
                        {
                            "name": "countryIdentifier",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "examples": {
                                "countryName": {"value": "afghanistan"},
                                "alpha2": {"value": "AF"},
                                "alpha3": {"value": "AFG"},
                            },
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Country water sections parsed from source page"
                        },
                        "404": {"description": "Country not found"},
                    },
                }
            },
            "/geography/region/{region}": {
                "get": {
                    "summary": "Region-specific geography datasets",
                    "parameters": [
                        {
                            "name": "region",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "string",
                                "enum": [
                                    "asia",
                                    "africa",
                                    "europe",
                                    "latin-america",
                                    "northern-america",
                                    "oceania",
                                ],
                            },
                        },
                        {
                            "name": "dataset",
                            "in": "query",
                            "required": False,
                            "schema": {
                                "type": "string",
                                "enum": ["countries", "dependencies"],
                                "default": "countries",
                            },
                        },
                    ],
                    "responses": {
                        "200": {"description": "Region geography dataset"},
                        "400": {"description": "Invalid dataset"},
                        "404": {"description": "Unknown region"},
                    },
                }
            },
        }

    _attach_operation_tags(paths)

    return {
        "openapi": "3.1.0",
        "info": {
            "title": "Worldometer API",
            "version": "1.0.0",
            "description": "Lightweight Cloudflare Worker API exposing live, geography, population, energy, and water worldometer data.",
        },
        "servers": [{"url": "/"}],
        "tags": _build_openapi_tags(),
        "paths": paths,
    }


def _build_openapi_tags() -> list[dict[str, str]]:
    return [
        {"name": "docs", "description": "Documentation and OpenAPI routes"},
        {"name": "live", "description": "Real-time counters"},
        {"name": "population", "description": "Population routes"},
        {"name": "geography", "description": "Geography routes"},
        {"name": "energy", "description": "Energy routes"},
        {"name": "water", "description": "Water routes"},
    ]


def _infer_tag_for_path(path: str) -> str:
    if path in {"/", "/docs", "/api", "/openapi.json"}:
        return "docs"
    if path == "/live":
        return "live"
    if path.startswith("/population/"):
        return "population"
    if path.startswith("/geography/"):
        return "geography"
    if path.startswith("/energy"):
        return "energy"
    if path.startswith("/water"):
        return "water"
    return "docs"


def _attach_operation_tags(paths: dict[str, dict[str, Any]]) -> None:
    for path, operations in paths.items():
        tag = _infer_tag_for_path(path)
        for operation in operations.values():
            if isinstance(operation, dict):
                operation.setdefault("tags", [tag])


def build_docs_html(spec_path: str = "/openapi.json") -> str:
    safe_spec_path = escape(spec_path, quote=True)
    return f"""
<!DOCTYPE html>
<html lang=\"en\">
    <head>
        <meta charset=\"UTF-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
        <title>Worldometer API Docs</title>
        <style>
            body {{ margin: 0; }}
        </style>
    </head>
    <body>
        <script id=\"api-reference\" data-url=\"{safe_spec_path}\"></script>
        <script src=\"{SCALAR_API_REFERENCE_JS_URL}\" defer></script>
    </body>
</html>
""".strip()
