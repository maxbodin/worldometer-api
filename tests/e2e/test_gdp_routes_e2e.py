import pytest

from .conftest import GDP_ALLOWED_REGIONS
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
    ("path", "expected_source", "expected_metric"),
    [
        (
            "/gdp?dataset=by-country&source=wb&region=worldwide&year=2024",
            "wb",
            "nominal",
        ),
        (
            "/gdp?dataset=by-country&source=wb&region=worldwide&year=2024&metric=ppp",
            "wb",
            "ppp",
        ),
        (
            "/gdp?dataset=by-country&source=imf&region=worldwide&year=2027",
            "imf",
            "nominal",
        ),
    ],
)
def test_gdp_overview_by_country_supports_additional_query_parameters(
    base_url: str,
    path: str,
    expected_source: str,
    expected_metric: str,
) -> None:
    payload = get_json(base_url, path)

    assert_table_payload(payload)
    assert payload["dataset"] == "by-country"
    assert payload["route_key"] == "gdp/by-country"
    assert payload["parameters"]["source"] == expected_source
    assert payload["parameters"]["metric"] == expected_metric
    assert payload["parameters"]["region"] == "worldwide"
    assert payload["parameters"]["year"] in {"2024", "2027"}
    assert f"source={expected_source}" in payload["source_path"]
    assert "region=worldwide" in payload["source_path"]
    assert "| Source:" in payload["table_title"]
    assert "| Metric:" in payload["table_title"]


@pytest.mark.e2e
@pytest.mark.parametrize(
    (
        "path",
        "expected_region",
        "expected_year",
        "expected_metric",
        "expected_metric_label",
    ),
    [
        (
            "/gdp?dataset=per-capita&source=imf&region=asia&year=2026&metric=nominal",
            "asia",
            "2026",
            "nominal",
            "Nominal GDP",
        ),
        (
            "/gdp?dataset=per-capita&source=imf&region=asia&year=2026&metric=ppp",
            "asia",
            "2026",
            "ppp",
            "PPP GDP",
        ),
        (
            "/gdp?dataset=per-capita&source=imf&region=asia&year=2027&metric=ppp",
            "asia",
            "2027",
            "ppp",
            "PPP GDP",
        ),
        (
            "/gdp?dataset=per-capita&source=imf&region=worldwide&year=2027&metric=ppp",
            "worldwide",
            "2027",
            "ppp",
            "PPP GDP",
        ),
        (
            "/gdp?dataset=per-capita&source=imf&region=northern-america&year=2027&metric=ppp",
            "northern-america",
            "2027",
            "ppp",
            "PPP GDP",
        ),
    ],
)
def test_gdp_overview_per_capita_supports_additional_query_parameters(
    base_url: str,
    path: str,
    expected_region: str,
    expected_year: str,
    expected_metric: str,
    expected_metric_label: str,
) -> None:
    payload = get_json(base_url, path)

    assert_table_payload(payload)
    assert payload["dataset"] == "per-capita"
    assert payload["route_key"] == "gdp/per-capita"
    assert payload["parameters"] == {
        "source": "imf",
        "region": expected_region,
        "year": expected_year,
        "metric": expected_metric,
    }
    assert payload["source_path"].startswith("/gdp/gdp-per-capita/")
    assert "source=imf" in payload["source_path"]
    assert f"region={expected_region}" in payload["source_path"]
    assert f"year={expected_year}" in payload["source_path"]
    assert f"metric={expected_metric}" in payload["source_path"]
    assert "Source: IMF" in payload["table_title"]
    assert f"Metric: {expected_metric_label}" in payload["table_title"]


@pytest.mark.e2e
@pytest.mark.parametrize("region", GDP_ALLOWED_REGIONS)
def test_gdp_overview_region_accepts_only_documented_region_values(
    base_url: str,
    region: str,
) -> None:
    payload = get_json(
        base_url,
        f"/gdp?dataset=per-capita&source=imf&region={region}&year=2027&metric=ppp",
    )

    assert_table_payload(payload)
    assert payload["parameters"]["region"] == region


@pytest.mark.e2e
@pytest.mark.parametrize(
    "region",
    [
        "latin-america",
        "north-america",
        "america",
    ],
)
def test_gdp_overview_region_rejects_unsupported_values(base_url: str, region: str) -> None:
    payload = get_json(
        base_url,
        f"/gdp?dataset=per-capita&source=imf&region={region}&year=2027&metric=ppp",
        expected_status=400,
    )

    assert "Invalid region" in payload.get("error", "")
    for allowed_region in GDP_ALLOWED_REGIONS:
        assert allowed_region in payload["error"]




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

    assert any("China GDP Projections (IMF)" in str(table.get("title")) for table in payload["tables"])
    assert all("title" in table for table in payload["tables"])


@pytest.mark.e2e
def test_gdp_country_table_titles_include_source_and_metric_context(base_url: str) -> None:
    payload = get_json(base_url, "/gdp/country/russia")

    titles = [str(table.get("title", "")) for table in payload["tables"]]

    assert all("| Source:" in title and "| Metric:" in title for title in titles if title)
    assert any("Source: IMF" in title and "Metric: Nominal GDP" in title for title in titles)
    assert any("Source: IMF" in title and "Metric: PPP GDP" in title for title in titles)
    assert any("Source: WB" in title and "Metric: Nominal GDP" in title for title in titles)


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
