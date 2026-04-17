import time
from dataclasses import dataclass
from typing import Any


@dataclass
class CacheEntry:
    value: Any
    created_at: float


class TTLCache:
    def __init__(self) -> None:
        self._store: dict[str, CacheEntry] = {}

    def get(self, key: str, ttl_seconds: int) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None

        if time.time() - entry.created_at > ttl_seconds:
            self._store.pop(key, None)
            return None

        return entry.value

    def set(self, key: str, value: Any) -> Any:
        self._store[key] = CacheEntry(value=value, created_at=time.time())
        return value

    def clear(self) -> None:
        self._store.clear()
