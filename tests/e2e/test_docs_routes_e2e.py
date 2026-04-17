import pytest

from .utils import get


@pytest.mark.e2e
@pytest.mark.parametrize("path", ["/", "/docs", "/api"])
def test_docs_routes_return_html(base_url: str, path: str) -> None:
    response = get(base_url, path)
    assert "text/html" in response.headers.get("Content-Type", "")
    assert "Worldometer API Docs" in response.text
    assert "api-reference" in response.text
