
# app/core/cache.py
import redis
import json
import pickle
from typing import Any, Optional
from app.core.config import settings

class CacheManager:
    def __init__(self):
        self.redis_client = redis.from_url(settings.redis_url, decode_responses=False)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            data = self.redis_client.get(key)
            if data:
                return pickle.loads(data)
            return None
        except Exception:
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL"""
        try:
            ttl = ttl or settings.cache_ttl_seconds
            serialized_data = pickle.dumps(value)
            return self.redis_client.setex(key, ttl, serialized_data)
        except Exception:
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception:
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception:
            return 0

cache_manager = CacheManager()
