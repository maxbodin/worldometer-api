import os
import subprocess
import time
from pathlib import Path

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
