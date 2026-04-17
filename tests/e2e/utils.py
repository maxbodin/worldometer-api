from typing import Any

import httpx


def get(base_url: str, path: str, *, expected_status: int = 200) -> httpx.Response:
    response = httpx.get(f"{base_url}{path}", timeout=60.0)
    assert response.status_code == expected_status, response.text
    return response


def get_json(base_url: str, path: str, *, expected_status: int = 200) -> dict[str, Any]:
    response = get(base_url, path, expected_status=expected_status)
    payload = response.json()
    assert isinstance(payload, dict), payload
    return payload


def assert_table_payload(payload: dict[str, Any]) -> None:
    assert isinstance(payload.get("source_path"), str)
    assert payload["source_path"].startswith("/")
    assert isinstance(payload.get("rows"), list)
    assert isinstance(payload.get("count"), int)
    assert payload["count"] == len(payload["rows"])
    assert payload["count"] > 0
