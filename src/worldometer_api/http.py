import json
from typing import Any

from workers import Response


def json_response(payload: Any, status: int = 200) -> Response:
    return Response(
        json.dumps(payload, ensure_ascii=False),
        status=status,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )


def error_response(message: str, status: int = 400, details: Any | None = None) -> Response:
    payload: dict[str, Any] = {"error": message}
    if details is not None:
        payload["details"] = details
    return json_response(payload, status=status)


def html_response(content: str, status: int = 200) -> Response:
    return Response(
        content,
        status=status,
        headers={"Content-Type": "text/html; charset=utf-8"},
    )
