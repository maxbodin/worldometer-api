import pytest

from .conftest import REGIONS
from .utils import assert_table_payload, get_json


@pytest.mark.e2e
@pytest.mark.parametrize(
    "path",
    [
        "/population/country-codes",
        "/population/countries",
        "/population/largest-cities",
        "/population/by-year",
        "/population/projections",
    ],
)
def test_population_table_routes_return_rows(base_url: str, path: str) -> None:
    payload = get_json(base_url, path)
    assert_table_payload(payload)


@pytest.mark.e2e
@pytest.mark.parametrize("period", ["current", "past", "future"])
def test_population_most_populous_period_variants(base_url: str, period: str) -> None:
    payload = get_json(base_url, f"/population/most-populous?period={period}")
    assert_table_payload(payload)
    assert payload["period"] == period


@pytest.mark.e2e
@pytest.mark.parametrize("period", ["current", "past", "future"])
def test_population_by_region_period_variants(base_url: str, period: str) -> None:
    payload = get_json(base_url, f"/population/by-region?period={period}")
    assert_table_payload(payload)
    assert payload["period"] == period


@pytest.mark.e2e
@pytest.mark.parametrize("region", REGIONS)
def test_population_region_default_dataset_for_all_regions(base_url: str, region: str) -> None:
    payload = get_json(base_url, f"/population/region/{region}")
    assert_table_payload(payload)
    assert payload["region"] == region
    assert payload["dataset"] == "subregions"


@pytest.mark.e2e
@pytest.mark.parametrize("dataset", ["subregions", "historical", "forecast"])
def test_population_region_dataset_variants(base_url: str, dataset: str) -> None:
    payload = get_json(base_url, f"/population/region/asia?dataset={dataset}")
    assert_table_payload(payload)
    assert payload["region"] == "asia"
    assert payload["dataset"] == dataset


@pytest.mark.e2e
@pytest.mark.parametrize(
    ("identifier", "expected_match"),
    [
        ("AF", "alpha2"),
        ("AFG", "alpha3"),
        ("afghanistan", "name"),
    ],
)
def test_population_country_lookup_supports_name_and_alpha_codes(
    base_url: str,
    identifier: str,
    expected_match: str,
) -> None:
    payload = get_json(base_url, f"/population/country/{identifier}")

    assert payload["country"] == "Afghanistan"
    assert payload["country_identifier"] == identifier
    assert payload["matched_by"] == expected_match
    assert payload["source_path"] == "/world-population/afghanistan-population/"
    assert payload["source_url"].endswith("/world-population/afghanistan-population/")

    assert isinstance(payload.get("table_count"), int)
    assert payload["table_count"] > 0
    assert isinstance(payload.get("tables"), list)
    assert payload["table_count"] == len(payload["tables"])

    for table in payload["tables"]:
        assert isinstance(table.get("index"), int)
        assert isinstance(table.get("rows"), list)
        assert isinstance(table.get("count"), int)
        assert table["count"] == len(table["rows"])
