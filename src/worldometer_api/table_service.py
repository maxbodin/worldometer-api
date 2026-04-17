from typing import Any

from .cache import TTLCache
from .config import BASE_URL, TABLE_CACHE_TTL_SECONDS
from .fetcher import fetch_text
from .table_parser import parse_html_tables


class TableService:
    def __init__(self, cache: TTLCache) -> None:
        self._cache = cache

    async def get_tables(self, path: str) -> list[list[dict[str, Any]]]:
        cache_key = f"tables:{path}"
        cached = self._cache.get(cache_key, TABLE_CACHE_TTL_SECONDS)
        if cached is not None:
            return cached

        html = await fetch_text(f"{BASE_URL}{path}")
        tables = parse_html_tables(html)
        return self._cache.set(cache_key, tables)

    async def get_table(self, path: str, table_index: int = 0) -> list[dict[str, Any]]:
        tables = await self.get_tables(path)
        if table_index >= len(tables):
            raise ValueError(
                f"Table index {table_index} is not available on {path}. Found {len(tables)} table(s)."
            )

        return tables[table_index]
