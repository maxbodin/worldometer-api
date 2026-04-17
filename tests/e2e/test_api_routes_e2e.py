import os
import subprocess
import time
from pathlib import Path
from typing import Any

import httpx
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8787")
START_SERVER_IF_NEEDED = os.getenv("E2E_START_SERVER", "1").strip().lower() not in {
    "0",
    "false",
    "no",
}

REGIONS = [
    "asia",
    "africa",
    "europe",
    "latin-america",
    "northern-america",
    "oceania",
]


def _is_ready(base_url: str, timeout_seconds: float = 2.0) -> bool:
    try:
        response = httpx.get(f"{base_url}/openapi.json", timeout=timeout_seconds)
        return response.status_code == 200
    except Exception:
        return False


def _wait_until_ready(base_url: str, timeout_seconds: float = 60.0) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if _is_ready(base_url):
            return
        time.sleep(0.5)
    raise RuntimeError(f"Worker did not become ready within {timeout_seconds:.0f}s at {base_url}")


@pytest.fixture(scope="session")
def base_url() -> str:
    if _is_ready(DEFAULT_BASE_URL):
        yield DEFAULT_BASE_URL
        return

    if not START_SERVER_IF_NEEDED:
        pytest.skip(
            f"Worker is not reachable at {DEFAULT_BASE_URL}. "
            "Start it manually or set E2E_START_SERVER=1."
        )

    process = subprocess.Popen(
        ["uv", "run", "pywrangler", "dev", "--port", "8787", "--ip", "127.0.0.1"],
        cwd=PROJECT_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        _wait_until_ready(DEFAULT_BASE_URL, timeout_seconds=90.0)
        yield DEFAULT_BASE_URL
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def _get(base_url: str, path: str, *, expected_status: int = 200) -> httpx.Response:
    response = httpx.get(f"{base_url}{path}", timeout=60.0)
    assert response.status_code == expected_status, response.text
    return response


def _get_json(base_url: str, path: str, *, expected_status: int = 200) -> dict[str, Any]:
    response = _get(base_url, path, expected_status=expected_status)
    payload = response.json()
    assert isinstance(payload, dict), payload
    return payload


def _assert_table_payload(payload: dict[str, Any]) -> None:
    assert isinstance(payload.get("source_path"), str)
    assert payload["source_path"].startswith("/")
    assert isinstance(payload.get("rows"), list)
    assert isinstance(payload.get("count"), int)
    assert payload["count"] == len(payload["rows"])
    assert payload["count"] > 0


@pytest.mark.e2e
@pytest.mark.parametrize("path", ["/", "/docs", "/api"])
def test_docs_routes_return_html(base_url: str, path: str) -> None:
    response = _get(base_url, path)
    assert "text/html" in response.headers.get("Content-Type", "")
    assert "Worldometer API Docs" in response.text
    assert "api-reference" in response.text


@pytest.mark.e2e
def test_openapi_spec_contains_expected_routes(base_url: str) -> None:
    payload = _get_json(base_url, "/openapi.json")

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
    }
    assert expected_paths.issubset(set(paths.keys()))


@pytest.mark.e2e
def test_live_route_returns_real_sections(base_url: str) -> None:
    payload = _get_json(base_url, "/live")

    sections_payload = payload.get("data", payload)
    assert isinstance(sections_payload, dict)

    expected_sections = {
        "world_population",
        "government_and_economics",
        "society_and_media",
        "environment",
        "food",
        "water",
        "energy",
        "health",
    }
    assert expected_sections.issubset(set(sections_payload.keys()))
    for section in expected_sections:
        assert isinstance(sections_payload[section], dict)
        assert sections_payload[section], f"{section} should not be empty"


@pytest.mark.e2e
@pytest.mark.parametrize(
    "path",
    [
        "/population/country-codes",
        "/population/countries",
        "/population/largest-cities",
        "/population/by-year",
        "/population/projections",
        "/geography/largest-countries",
        "/geography/world-countries",
        "/energy",
    ],
)
def test_table_routes_return_rows(base_url: str, path: str) -> None:
    payload = _get_json(base_url, path)
    _assert_table_payload(payload)


@pytest.mark.e2e
@pytest.mark.parametrize("period", ["current", "past", "future"])
def test_population_most_populous_period_variants(base_url: str, period: str) -> None:
    payload = _get_json(base_url, f"/population/most-populous?period={period}")
    _assert_table_payload(payload)
    assert payload["period"] == period


@pytest.mark.e2e
@pytest.mark.parametrize("period", ["current", "past", "future"])
def test_population_by_region_period_variants(base_url: str, period: str) -> None:
    payload = _get_json(base_url, f"/population/by-region?period={period}")
    _assert_table_payload(payload)
    assert payload["period"] == period


@pytest.mark.e2e
@pytest.mark.parametrize("region", REGIONS)
def test_population_region_default_dataset_for_all_regions(base_url: str, region: str) -> None:
    payload = _get_json(base_url, f"/population/region/{region}")
    _assert_table_payload(payload)
    assert payload["region"] == region
    assert payload["dataset"] == "subregions"


@pytest.mark.e2e
@pytest.mark.parametrize("dataset", ["subregions", "historical", "forecast"])
def test_population_region_dataset_variants(base_url: str, dataset: str) -> None:
    payload = _get_json(base_url, f"/population/region/asia?dataset={dataset}")
    _assert_table_payload(payload)
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
    payload = _get_json(base_url, f"/population/country/{identifier}")

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


@pytest.mark.e2e
@pytest.mark.parametrize("region", REGIONS)
def test_geography_region_default_dataset_for_all_regions(base_url: str, region: str) -> None:
    payload = _get_json(base_url, f"/geography/region/{region}")
    _assert_table_payload(payload)
    assert payload["region"] == region
    assert payload["dataset"] == "countries"


@pytest.mark.e2e
def test_geography_region_dependencies_dataset(base_url: str) -> None:
    payload = _get_json(base_url, "/geography/region/asia?dataset=dependencies")
    _assert_table_payload(payload)
    assert payload["region"] == "asia"
    assert payload["dataset"] == "dependencies"


@pytest.mark.e2e
@pytest.mark.parametrize(
    ("identifier", "expected_match"),
    [
        ("CN", "alpha2"),
        ("CHN", "alpha3"),
        ("china", "name"),
    ],
)
def test_energy_country_lookup_supports_name_and_alpha_codes(
    base_url: str,
    identifier: str,
    expected_match: str,
) -> None:
    payload = _get_json(base_url, f"/energy/country/{identifier}")

    assert payload["country"] == "China"
    assert payload["country_identifier"] == identifier
    assert payload["matched_by"] == expected_match
    assert payload["country_slug"] == "china"
    assert payload["dataset"] == "all"
    assert payload["dataset_count"] == len(payload["datasets"])
    assert payload["dataset_count"] == 5

    dataset_names = {entry["dataset"] for entry in payload["datasets"]}
    assert dataset_names == {"energy", "electricity", "gas", "oil", "coal"}


@pytest.mark.e2e
@pytest.mark.parametrize("dataset", ["all", "energy", "electricity", "gas", "oil", "coal"])
def test_energy_country_dataset_variants(base_url: str, dataset: str) -> None:
    payload = _get_json(base_url, f"/energy/country/china?dataset={dataset}")

    assert payload["country"] == "China"
    assert payload["dataset"] == dataset
    assert payload["dataset_count"] == len(payload["datasets"])

    if dataset == "all":
        assert payload["dataset_count"] == 5
    else:
        assert payload["dataset_count"] == 1

    for entry in payload["datasets"]:
        assert isinstance(entry["source_path"], str)
        assert entry["source_path"].startswith("/")
        assert entry["source_url"].startswith("https://")
        assert isinstance(entry["table_count"], int)
        assert entry["table_count"] > 0
        assert isinstance(entry["tables"], list)
        assert entry["table_count"] == len(entry["tables"])

        for table in entry["tables"]:
            assert isinstance(table["index"], int)
            assert isinstance(table["rows"], list)
            assert isinstance(table["count"], int)
            assert table["count"] == len(table["rows"])


@pytest.mark.e2e
@pytest.mark.parametrize(
    "removed_alias",
    [
        "/api/live",
        "/api/country-codes",
        "/api/population/countries",
        "/api/geography/world-countries",
        "/population/country?country=AF",
    ],
)
def test_removed_compatibility_aliases_return_not_found(base_url: str, removed_alias: str) -> None:
    response = _get(base_url, removed_alias, expected_status=404)
    payload = response.json()
    assert payload == {"error": "Not found"}
