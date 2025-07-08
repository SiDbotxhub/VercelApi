from datetime import datetime, timedelta
from lib.config import Config
import json

class Cache:
    _instance = None
    _cache = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Cache, cls).__new__(cls)
        return cls._instance

    def get(self, key):
        item = self._cache.get(key)
        if item and datetime.now() < item['expires']:
            return item['data']
        return None

    def set(self, key, data):
        self._cache[key] = {
            'data': data,
            'expires': datetime.now() + Config.CACHE_DURATION
        }

    def clear_expired(self):
        now = datetime.now()
        expired_keys = [k for k, v in self._cache.items() if now >= v['expires']]
        for key in expired_keys:
            del self._cache[key]

# Singleton cache instance
cache = Cache()
