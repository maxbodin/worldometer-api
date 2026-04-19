import pytest

from .utils import assert_table_payload, get_json


@pytest.mark.e2e
def test_ghg_emissions_default_route_returns_rows(base_url: str) -> None:
    payload = get_json(base_url, "/ghg-emissions")
    assert_table_payload(payload)


@pytest.mark.e2e
@pytest.mark.parametrize(
    "path",
    [
        "/ghg-emissions/greenhouse",
        "/ghg-emissions/greenhouse/by-country",
        "/ghg-emissions/greenhouse/by-year",
        "/ghg-emissions/greenhouse/per-capita",
        "/ghg-emissions/co2",
        "/ghg-emissions/co2/by-country",
        "/ghg-emissions/co2/by-year",
        "/ghg-emissions/co2/per-capita",
    ],
)
def test_ghg_emissions_overview_routes_return_rows(base_url: str, path: str) -> None:
    payload = get_json(base_url, path)
    assert_table_payload(payload)


@pytest.mark.e2e
@pytest.mark.parametrize(
    ("identifier", "expected_match"),
    [
        ("CN", "alpha2"),
        ("CHN", "alpha3"),
        ("china", "name"),
    ],
)
def test_ghg_emissions_country_lookup_supports_name_and_alpha_codes(
    base_url: str,
    identifier: str,
    expected_match: str,
) -> None:
    payload = get_json(base_url, f"/ghg-emissions/country/{identifier}")

    assert payload["country"] == "China"
    assert payload["country_identifier"] == identifier
    assert payload["matched_by"] == expected_match
    assert payload["country_slug"] == "china"
    assert payload["dataset"] == "all"
    assert payload["dataset_count"] == len(payload["datasets"])
    assert payload["dataset_count"] == 2

    dataset_names = {entry["dataset"] for entry in payload["datasets"]}
    assert dataset_names == {"greenhouse", "co2"}

    for entry in payload["datasets"]:
        assert entry["source_path"].startswith("/")
        assert entry["source_url"].startswith("https://")
        assert entry["table_count"] == len(entry["tables"])
        assert entry["table_count"] > 0


@pytest.mark.e2e
@pytest.mark.parametrize("dataset", ["all", "greenhouse", "co2"])
def test_ghg_emissions_country_dataset_variants(base_url: str, dataset: str) -> None:
    payload = get_json(base_url, f"/ghg-emissions/country/china?dataset={dataset}")

    assert payload["country"] == "China"
    assert payload["dataset"] == dataset
    assert payload["dataset_count"] == len(payload["datasets"])

    if dataset == "all":
        assert payload["dataset_count"] == 2
    else:
        assert payload["dataset_count"] == 1
        assert payload["datasets"][0]["dataset"] == dataset


@pytest.mark.e2e
def test_ghg_emissions_country_route_supports_short_slugs_from_group_indexes(base_url: str) -> None:
    payload = get_json(base_url, "/ghg-emissions/country/US")

    assert payload["country"] == "United States"
    dataset_paths = {entry["dataset"]: entry["source_path"] for entry in payload["datasets"]}
    assert dataset_paths["greenhouse"] == "/greenhouse-gas-emissions/us-greenhouse-gas-emissions/"
    assert dataset_paths["co2"] == "/co2-emissions/us-co2-emissions/"


@pytest.mark.e2e
@pytest.mark.parametrize(
    ("identifier", "expected_country", "expected_match", "expected_slug"),
    [
        ("palau", "Palau", "name", "palau"),
        ("PLW", "Palau", "alpha3", "palau"),
        ("china", "China", "name", "china"),
    ],
)
def test_ghg_emissions_country_routes_cover_requested_country_source_pages(
    base_url: str,
    identifier: str,
    expected_country: str,
    expected_match: str,
    expected_slug: str,
) -> None:
    payload = get_json(base_url, f"/ghg-emissions/country/{identifier}?dataset=all")

    assert payload["country"] == expected_country
    assert payload["matched_by"] == expected_match

    dataset_paths = {entry["dataset"]: entry["source_path"] for entry in payload["datasets"]}
    assert dataset_paths["greenhouse"] == (
        f"/greenhouse-gas-emissions/{expected_slug}-greenhouse-gas-emissions/"
    )
    assert dataset_paths["co2"] == f"/co2-emissions/{expected_slug}-co2-emissions/"
