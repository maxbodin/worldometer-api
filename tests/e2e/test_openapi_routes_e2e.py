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
        "/gdp",
        "/gdp/country/{countryIdentifier}",
        "/food-agriculture",
        "/food-agriculture/undernourishment",
        "/food-agriculture/forest",
        "/food-agriculture/cropland",
        "/food-agriculture/pesticides",
        "/food-agriculture/country/{countryIdentifier}",
        "/ghg-emissions",
        "/ghg-emissions/greenhouse",
        "/ghg-emissions/greenhouse/by-country",
        "/ghg-emissions/greenhouse/by-year",
        "/ghg-emissions/greenhouse/per-capita",
        "/ghg-emissions/co2",
        "/ghg-emissions/co2/by-country",
        "/ghg-emissions/co2/by-year",
        "/ghg-emissions/co2/per-capita",
        "/ghg-emissions/country/{countryIdentifier}",
        "/maps",
        "/maps/country/{countryIdentifier}",
        "/maps/physical/{countryIdentifier}",
        "/maps/political/{countryIdentifier}",
        "/maps/road/{countryIdentifier}",
        "/maps/locator/{countryIdentifier}",
    }
    assert expected_paths.issubset(set(paths.keys()))


@pytest.mark.e2e
def test_openapi_operations_are_grouped_with_tags(base_url: str) -> None:
    payload = get_json(base_url, "/openapi.json")

    tag_names = {tag["name"] for tag in payload.get("tags", [])}
    assert {
        "docs",
        "live",
        "population",
        "geography",
        "energy",
        "water",
        "gdp",
        "food-agriculture",
        "ghg-emissions",
        "maps",
    }.issubset(tag_names)

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
        "/gdp": "gdp",
        "/gdp/country/{countryIdentifier}": "gdp",
        "/food-agriculture": "food-agriculture",
        "/food-agriculture/country/{countryIdentifier}": "food-agriculture",
        "/ghg-emissions": "ghg-emissions",
        "/ghg-emissions/country/{countryIdentifier}": "ghg-emissions",
        "/maps": "maps",
        "/maps/country/{countryIdentifier}": "maps",
    }

    for path, expected_tag in expected_tag_per_path.items():
        operation = payload["paths"][path]["get"]
        assert operation.get("tags") == [expected_tag]


@pytest.mark.e2e
def test_openapi_gdp_route_documents_extended_query_parameters(base_url: str) -> None:
    payload = get_json(base_url, "/openapi.json")

    parameters = payload["paths"]["/gdp"]["get"]["parameters"]
    parameters_by_name = {parameter["name"]: parameter for parameter in parameters}

    assert {"dataset", "source", "region", "year", "metric"}.issubset(parameters_by_name)
    assert parameters_by_name["source"]["schema"]["enum"] == ["imf", "wb"]
    assert parameters_by_name["metric"]["schema"]["enum"] == ["nominal", "ppp"]
