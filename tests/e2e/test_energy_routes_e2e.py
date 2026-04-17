import pytest

from .utils import assert_table_payload, get_json


@pytest.mark.e2e
def test_energy_overview_route_returns_rows(base_url: str) -> None:
    payload = get_json(base_url, "/energy")
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
def test_energy_country_lookup_supports_name_and_alpha_codes(
    base_url: str,
    identifier: str,
    expected_match: str,
) -> None:
    payload = get_json(base_url, f"/energy/country/{identifier}")

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
    payload = get_json(base_url, f"/energy/country/china?dataset={dataset}")

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
