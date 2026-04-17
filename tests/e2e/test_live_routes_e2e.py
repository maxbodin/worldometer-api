import pytest

from .utils import get_json


@pytest.mark.e2e
def test_live_route_returns_real_sections(base_url: str) -> None:
    payload = get_json(base_url, "/live")

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
