import pytest

from .utils import assert_table_payload, get_json


@pytest.mark.e2e
def test_gdp_overview_default_dataset_returns_rows(base_url: str) -> None:
    payload = get_json(base_url, "/gdp")
    assert_table_payload(payload)
    assert payload["dataset"] == "by-country"
    assert payload["route_key"] == "gdp/by-country"
    assert isinstance(payload.get("table_title"), str)
    assert payload["table_title"]


@pytest.mark.e2e
@pytest.mark.parametrize("dataset", ["by-country", "per-capita"])
def test_gdp_overview_dataset_query_variants(base_url: str, dataset: str) -> None:
    payload = get_json(base_url, f"/gdp?dataset={dataset}")
    assert_table_payload(payload)
    assert payload["dataset"] == dataset
    assert payload["route_key"] == f"gdp/{dataset}"




@pytest.mark.e2e
@pytest.mark.parametrize(
    ("identifier", "expected_match"),
    [
        ("CN", "alpha2"),
        ("CHN", "alpha3"),
        ("china", "name"),
    ],
)
def test_gdp_country_lookup_supports_name_and_alpha_codes(
    base_url: str,
    identifier: str,
    expected_match: str,
) -> None:
    payload = get_json(base_url, f"/gdp/country/{identifier}")

    assert payload["country"] == "China"
    assert payload["country_identifier"] == identifier
    assert payload["matched_by"] == expected_match
    assert payload["country_slug"] == "china"
    assert payload["source_path"] == "/gdp/china-gdp/"
    assert payload["source_url"].endswith("/gdp/china-gdp/")

    assert isinstance(payload.get("table_count"), int)
    assert payload["table_count"] > 0
    assert isinstance(payload.get("tables"), list)
    assert payload["table_count"] == len(payload["tables"])

    description = payload.get("description")
    assert isinstance(description, dict)
    assert isinstance(description.get("title"), str)
    assert isinstance(description.get("source"), str)
    assert isinstance(description.get("items"), list)
    assert description["items"]
    assert isinstance(description.get("text"), str)
    assert description["text"]

    assert any(table["count"] > 0 for table in payload["tables"])
    for table in payload["tables"]:
        assert isinstance(table["index"], int)
        assert "title" in table
        assert isinstance(table["rows"], list)
        assert isinstance(table["count"], int)
        assert table["count"] == len(table["rows"])


@pytest.mark.e2e
def test_gdp_country_route_uses_group_specific_country_slug_mapping(base_url: str) -> None:
    payload = get_json(base_url, "/gdp/country/US")

    assert payload["country"] == "United States"
    assert payload["matched_by"] in {"name", "alpha2"}
    assert payload["source_path"] == "/gdp/us-gdp/"


@pytest.mark.e2e
def test_gdp_country_tables_include_titles(base_url: str) -> None:
    payload = get_json(base_url, "/gdp/country/china")

    assert any(table.get("title") == "China GDP Projections (IMF)" for table in payload["tables"])
    assert all("title" in table for table in payload["tables"])


@pytest.mark.e2e
@pytest.mark.parametrize(
    ("identifier", "expected_source"),
    [
        ("monaco", "WB"),
        ("china", "IMF"),
    ],
)
def test_gdp_country_description_includes_summary_items(
    base_url: str,
    identifier: str,
    expected_source: str,
) -> None:
    payload = get_json(base_url, f"/gdp/country/{identifier}")

    description = payload["description"]
    assert description["source"] == expected_source
    assert any("Nominal (current) Gross Domestic Product (GDP)" in item for item in description["items"])
    assert any("GDP growth rate" in item for item in description["items"])
    assert any("GDP per Capita" in item for item in description["items"])
