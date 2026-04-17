import pytest

from .conftest import REGIONS
from .utils import assert_table_payload, get_json


@pytest.mark.e2e
@pytest.mark.parametrize(
    "path",
    [
        "/geography/largest-countries",
        "/geography/world-countries",
    ],
)
def test_geography_table_routes_return_rows(base_url: str, path: str) -> None:
    payload = get_json(base_url, path)
    assert_table_payload(payload)


@pytest.mark.e2e
@pytest.mark.parametrize("region", REGIONS)
def test_geography_region_default_dataset_for_all_regions(base_url: str, region: str) -> None:
    payload = get_json(base_url, f"/geography/region/{region}")
    assert_table_payload(payload)
    assert payload["region"] == region
    assert payload["dataset"] == "countries"


@pytest.mark.e2e
def test_geography_region_dependencies_dataset(base_url: str) -> None:
    payload = get_json(base_url, "/geography/region/asia?dataset=dependencies")
    assert_table_payload(payload)
    assert payload["region"] == "asia"
    assert payload["dataset"] == "dependencies"
