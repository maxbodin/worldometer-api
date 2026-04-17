import pytest

from .utils import assert_table_payload, get_json


@pytest.mark.e2e
def test_food_agriculture_overview_default_dataset_returns_rows(base_url: str) -> None:
    payload = get_json(base_url, "/food-agriculture")
    assert_table_payload(payload)
    assert payload["dataset"] == "undernourishment"
    assert payload["route_key"] == "food-agriculture/undernourishment"


@pytest.mark.e2e
@pytest.mark.parametrize("dataset", ["undernourishment", "forest", "cropland", "pesticides"])
def test_food_agriculture_overview_dataset_query_variants(base_url: str, dataset: str) -> None:
    payload = get_json(base_url, f"/food-agriculture?dataset={dataset}")
    assert_table_payload(payload)
    assert payload["dataset"] == dataset
    assert payload["route_key"] == f"food-agriculture/{dataset}"


@pytest.mark.e2e
@pytest.mark.parametrize(
    ("path", "expected_dataset"),
    [
        ("/food-agriculture/undernourishment", "undernourishment"),
        ("/food-agriculture/forest", "forest"),
        ("/food-agriculture/cropland", "cropland"),
        ("/food-agriculture/pesticides", "pesticides"),
    ],
)
def test_food_agriculture_named_overview_routes(
    base_url: str,
    path: str,
    expected_dataset: str,
) -> None:
    payload = get_json(base_url, path)
    assert_table_payload(payload)
    assert payload["dataset"] == expected_dataset


@pytest.mark.e2e
@pytest.mark.parametrize(
    ("identifier", "expected_match"),
    [
        ("AF", "alpha2"),
        ("AFG", "alpha3"),
        ("afghanistan", "name"),
    ],
)
def test_food_agriculture_country_lookup_supports_name_and_alpha_codes(
    base_url: str,
    identifier: str,
    expected_match: str,
) -> None:
    payload = get_json(base_url, f"/food-agriculture/country/{identifier}")

    assert payload["country"] == "Afghanistan"
    assert payload["country_identifier"] == identifier
    assert payload["matched_by"] == expected_match
    assert payload["country_slug"] == "afghanistan"
    assert payload["source_path"] == "/food-agriculture/afghanistan-food-agriculture/"
    assert payload["source_url"].endswith("/food-agriculture/afghanistan-food-agriculture/")

    sections = payload.get("sections")
    assert isinstance(sections, dict)
    assert {"undernourished", "forest", "cropland"}.issubset(set(sections.keys()))

    for section_name, section_payload in sections.items():
        assert isinstance(section_name, str)
        assert isinstance(section_payload, dict)
        assert section_payload.get("cards") or section_payload.get("latest_series_point")


@pytest.mark.e2e
def test_food_agriculture_country_route_includes_pesticides_when_available(base_url: str) -> None:
    payload = get_json(base_url, "/food-agriculture/country/IN")

    assert payload["country"] == "India"
    assert payload["source_path"] == "/food-agriculture/india-food-agriculture/"
    sections = payload["sections"]
    assert "pesticides" in sections

    pesticides = sections["pesticides"]
    assert isinstance(pesticides, dict)
    assert pesticides.get("cards") or pesticides.get("latest_series_point")


@pytest.mark.e2e
def test_food_agriculture_country_route_handles_optional_undernourishment_section(base_url: str) -> None:
    payload = get_json(base_url, "/food-agriculture/country/US")

    assert payload["country"] == "United States"
    assert payload["source_path"] == "/food-agriculture/us-food-agriculture/"
    sections = payload["sections"]

    assert "forest" in sections
    assert "cropland" in sections
    assert "pesticides" in sections
