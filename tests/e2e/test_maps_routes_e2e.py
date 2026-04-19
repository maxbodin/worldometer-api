import pytest

from .utils import assert_table_payload, get_json


@pytest.mark.e2e
def test_maps_overview_route_returns_rows(base_url: str) -> None:
    payload = get_json(base_url, "/maps")
    assert_table_payload(payload)


@pytest.mark.e2e
@pytest.mark.parametrize(
    ("identifier", "expected_match"),
    [
        ("AF", "alpha2"),
        ("AFG", "alpha3"),
        ("afghanistan", "name"),
    ],
)
def test_maps_country_lookup_supports_name_and_alpha_codes(
    base_url: str,
    identifier: str,
    expected_match: str,
) -> None:
    payload = get_json(base_url, f"/maps/country/{identifier}")

    assert payload["country"] == "Afghanistan"
    assert payload["country_identifier"] == identifier
    assert payload["matched_by"] == expected_match
    assert payload["country_slug"] == "afghanistan"
    assert payload["maps_page_path"] == "/maps/afghanistan-maps/"
    assert payload["maps_page_url"].endswith("/maps/afghanistan-maps/")

    assert isinstance(payload.get("available_types"), list)
    assert {"physical", "political", "road", "locator"}.issubset(set(payload["available_types"]))

    assert isinstance(payload.get("types"), dict)
    assert isinstance(payload.get("all_image_urls"), list)
    assert payload["all_image_urls"]


@pytest.mark.e2e
@pytest.mark.parametrize(
    ("map_type", "source_path_fragment"),
    [
        ("physical", "-map/"),
        ("political", "-political-map/"),
        ("road", "-road-map/"),
    ],
)
def test_maps_country_type_routes_return_map_metadata(
    base_url: str,
    map_type: str,
    source_path_fragment: str,
) -> None:
    payload = get_json(base_url, f"/maps/{map_type}/AF")

    assert payload["country"] == "Afghanistan"
    assert payload["map_type"] == map_type

    map_payload = payload["map"]
    assert isinstance(map_payload, dict)
    assert isinstance(map_payload.get("image_urls"), list)
    assert map_payload["image_urls"]
    assert source_path_fragment in map_payload["source_path"]


@pytest.mark.e2e
def test_maps_locator_route_returns_locator_image(base_url: str) -> None:
    payload = get_json(base_url, "/maps/locator/AF")

    assert payload["country"] == "Afghanistan"
    assert payload["map_type"] == "locator"

    map_payload = payload["map"]
    assert isinstance(map_payload, dict)
    assert isinstance(map_payload.get("image_urls"), list)
    assert map_payload["image_urls"]
    assert any("locator-map" in image_url for image_url in map_payload["image_urls"])


@pytest.mark.e2e
def test_maps_country_route_supports_short_slug_resolution(base_url: str) -> None:
    payload = get_json(base_url, "/maps/country/US")

    assert payload["country"] == "United States"
    assert payload["maps_page_path"] == "/maps/us-maps/"


@pytest.mark.e2e
@pytest.mark.parametrize(
    ("identifier", "expected_match"),
    [
        ("FR", "alpha2"),
        ("FRA", "alpha3"),
        ("france", "name"),
    ],
)
def test_maps_country_lookup_supports_requested_france_examples(
    base_url: str,
    identifier: str,
    expected_match: str,
) -> None:
    payload = get_json(base_url, f"/maps/country/{identifier}")

    assert payload["country"] == "France"
    assert payload["country_identifier"] == identifier
    assert payload["matched_by"] == expected_match
    assert payload["maps_page_path"] == "/maps/france-maps/"


@pytest.mark.e2e
def test_maps_country_route_returns_expected_afghanistan_image_sources(base_url: str) -> None:
    payload = get_json(base_url, "/maps/country/AF")

    assert "https://www.worldometers.info/img/maps_c/AF-map.gif" in payload["all_image_urls"]
    assert "https://www.worldometers.info/img/maps_cl/AF-locator-map.gif" in payload["all_image_urls"]
