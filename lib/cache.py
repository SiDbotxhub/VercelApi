from datetime import datetime, timedelta
from lib.config import Config
import json
from typing import Any, Dict, Optional
import asyncio

class Cache:
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}  # Fixed: Removed extra ]
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Dict[str, Any]]:  # Fixed: Removed extra ]
        async with self._lock:
            item = self._cache.get(key)
            if item and datetime.now() < item['expires']:
                return item['data']
            return None

    async def set(self, key: str, data: Dict[str, Any]) -> None:  # Fixed: Removed extra ]
        async with self._lock:
            self._cache[key] = {
                'data': data,
                'expires': datetime.now() + Config.CACHE_DURATION
            }

    async def clear_expired(self) -> None:
        async with self._lock:
            now = datetime.now()
            self._cache = {
                k: v for k, v in self._cache.items() 
                if now < v['expires']
            }

# Singleton cache instance
cache = Cache()
