import pytest

from .utils import get


@pytest.mark.e2e
@pytest.mark.parametrize(
    "removed_alias",
    [
        "/api/live",
        "/api/country-codes",
        "/api/population/countries",
        "/api/geography/world-countries",
        "/api/water",
        "/population/country?country=AF",
    ],
)
def test_removed_compatibility_aliases_return_not_found(base_url: str, removed_alias: str) -> None:
    response = get(base_url, removed_alias, expected_status=404)
    payload = response.json()
    assert payload == {"error": "Not found"}
