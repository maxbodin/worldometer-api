from typing import Any

from .cache import TTLCache
from .config import BASE_URL, TABLE_CACHE_TTL_SECONDS
from .fetcher import fetch_text
from .parsers.table_parser import parse_html_tables_with_titles


class TableService:
    def __init__(self, cache: TTLCache) -> None:
        self._cache = cache

    async def get_page_html(self, path: str) -> str:
        cache_key = f"html:{path}"
        cached = self._cache.get(cache_key, TABLE_CACHE_TTL_SECONDS)
        if cached is not None:
            return cached

        html = await fetch_text(f"{BASE_URL}{path}")
        return self._cache.set(cache_key, html)

    async def get_titled_tables(self, path: str) -> list[dict[str, Any]]:
        cache_key = f"tables:titled:{path}"
        cached = self._cache.get(cache_key, TABLE_CACHE_TTL_SECONDS)
        if cached is not None:
            return cached

        html = await self.get_page_html(path)
        tables = parse_html_tables_with_titles(html)
        return self._cache.set(cache_key, tables)

    async def get_tables(self, path: str) -> list[list[dict[str, Any]]]:
        titled_tables = await self.get_titled_tables(path)
        return [table.get("rows", []) for table in titled_tables]

    async def get_titled_table(self, path: str, table_index: int = 0) -> dict[str, Any]:
        tables = await self.get_titled_tables(path)
        if table_index >= len(tables):
            raise ValueError(
                f"Table index {table_index} is not available on {path}. Found {len(tables)} table(s)."
            )

        return tables[table_index]

    async def get_table(self, path: str, table_index: int = 0) -> list[dict[str, Any]]:
        table = await self.get_titled_table(path, table_index)
        rows = table.get("rows")
        if isinstance(rows, list):
            return rows
        return []
