from js import fetch


async def fetch_text(url: str) -> str:
    response = await fetch(url)
    if not response.ok:
        raise ValueError(f"Failed to fetch {url} (status: {response.status})")
    return str(await response.text())
