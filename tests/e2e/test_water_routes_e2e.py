import pytest

from .utils import assert_table_payload, get_json


@pytest.mark.e2e
def test_water_overview_route_returns_rows(base_url: str) -> None:
    payload = get_json(base_url, "/water")
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
def test_water_country_lookup_supports_name_and_alpha_codes(
    base_url: str,
    identifier: str,
    expected_match: str,
) -> None:
    payload = get_json(base_url, f"/water/country/{identifier}")

    assert payload["country"] == "Afghanistan"
    assert payload["country_identifier"] == identifier
    assert payload["matched_by"] == expected_match
    assert payload["country_slug"] == "afghanistan"
    assert payload["source_path"] == "/water/afghanistan-water/"

    sections = payload.get("sections")
    assert isinstance(sections, dict)

    precipitation = sections.get("precipitation")
    resources = sections.get("resources")
    water_use = sections.get("water_use")
    safe_drinking_water = sections.get("safe_drinking_water")

    assert isinstance(precipitation, dict)
    assert isinstance(resources, dict)
    assert isinstance(water_use, dict)
    assert isinstance(safe_drinking_water, dict)

    assert precipitation.get("depth") or precipitation.get("volume")
    assert resources.get("renewable_total") or resources.get("per_capita")
    assert water_use.get("latest_by_sector") is not None
    assert safe_drinking_water.get("no_access_people") or safe_drinking_water.get(
        "latest_no_access_people"
    )


@pytest.mark.e2e
def test_water_country_route_supports_another_country_source(base_url: str) -> None:
    payload = get_json(base_url, "/water/country/albania")

    assert payload["country"] == "Albania"
    assert payload["matched_by"] == "name"
    assert payload["country_slug"] == "albania"
    assert payload["source_path"] == "/water/albania-water/"
    assert isinstance(payload.get("sections"), dict)
