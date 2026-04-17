import pytest

from .utils import get_json


@pytest.mark.e2e
def test_openapi_spec_contains_expected_routes(base_url: str) -> None:
    payload = get_json(base_url, "/openapi.json")

    assert payload["openapi"].startswith("3.")
    assert payload["info"]["title"] == "Worldometer API"

    paths = payload["paths"]
    expected_paths = {
        "/",
        "/docs",
        "/api",
        "/openapi.json",
        "/live",
        "/population/country-codes",
        "/population/countries",
        "/population/most-populous",
        "/population/largest-cities",
        "/population/by-region",
        "/population/by-year",
        "/population/projections",
        "/population/region/{region}",
        "/population/country/{countryIdentifier}",
        "/geography/largest-countries",
        "/geography/world-countries",
        "/geography/region/{region}",
        "/energy",
        "/energy/country/{countryIdentifier}",
        "/water",
        "/water/country/{countryIdentifier}",
    }
    assert expected_paths.issubset(set(paths.keys()))


@pytest.mark.e2e
def test_openapi_operations_are_grouped_with_tags(base_url: str) -> None:
    payload = get_json(base_url, "/openapi.json")

    tag_names = {tag["name"] for tag in payload.get("tags", [])}
    assert {"docs", "live", "population", "geography", "energy", "water"}.issubset(tag_names)

    expected_tag_per_path = {
        "/": "docs",
        "/docs": "docs",
        "/api": "docs",
        "/openapi.json": "docs",
        "/live": "live",
        "/population/country-codes": "population",
        "/geography/world-countries": "geography",
        "/energy": "energy",
        "/water": "water",
        "/water/country/{countryIdentifier}": "water",
    }

    for path, expected_tag in expected_tag_per_path.items():
        operation = payload["paths"][path]["get"]
        assert operation.get("tags") == [expected_tag]
