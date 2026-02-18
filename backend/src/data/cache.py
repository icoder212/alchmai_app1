"""Redis caching implementation with in-memory TTL fallback"""
import json
import time
import redis
from typing import Optional, Callable, Any
from functools import wraps

from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class _InMemoryTTLCache:
    """Simple dict-based TTL cache used as a fallback when Redis is unavailable."""

    def __init__(self):
        self._store: dict = {}  # key -> (value, expiry_timestamp)

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expiry = entry
        if time.time() > expiry:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        self._store[key] = (value, time.time() + ttl)
        return True

    def delete(self, key: str) -> bool:
        self._store.pop(key, None)
        return True


class CacheManager:
    """Manages Redis caching for API responses, with in-memory TTL fallback."""

    def __init__(self):
        """Initialize Redis connection; fall back to in-memory cache if Redis is down."""
        self._memory_cache = _InMemoryTTLCache()
        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=0,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info(f"Connected to Redis at {settings.redis_host}:{settings.redis_port}")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Falling back to in-memory cache.")
            self.redis_client = None

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache (Redis first, then in-memory fallback).

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        # Try Redis first
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                logger.error(f"Error getting cache key {key} from Redis: {e}")

        # Fall back to in-memory cache
        return self._memory_cache.get(key)

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Set value in cache with TTL (Redis first, then in-memory fallback).

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 5 minutes)

        Returns:
            True if successful, False otherwise
        """
        # Try Redis first
        if self.redis_client:
            try:
                self.redis_client.setex(key, ttl, json.dumps(value))
                return True
            except Exception as e:
                logger.error(f"Error setting cache key {key} in Redis: {e}")

        # Fall back to in-memory cache
        return self._memory_cache.set(key, value, ttl)

    def delete(self, key: str) -> bool:
        """
        Delete key from cache (both Redis and in-memory).

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        deleted = False
        if self.redis_client:
            try:
                self.redis_client.delete(key)
                deleted = True
            except Exception as e:
                logger.error(f"Error deleting cache key {key} from Redis: {e}")

        self._memory_cache.delete(key)
        return deleted
    
    def get_or_set(self, key: str, fetch_func: Callable, ttl: int = 300) -> Any:
        """
        Get from cache or fetch and cache
        
        Args:
            key: Cache key
            fetch_func: Function to fetch data if not cached
            ttl: Time to live in seconds
            
        Returns:
            Cached or freshly fetched value
        """
        # Try cache first
        cached = self.get(key)
        if cached is not None:
            logger.debug(f"Cache hit for key: {key}")
            return cached
        
        # Fetch if not cached
        logger.debug(f"Cache miss for key: {key}")
        data = fetch_func()
        
        # Cache the result
        if data is not None:
            self.set(key, data, ttl)
        
        return data


# Global cache manager instance
cache_manager = CacheManager()


def cached(ttl: int = 300):
    """
    Decorator to cache function results
    
    Args:
        ttl: Time to live in seconds
        
    Usage:
        @cached(ttl=300)
        def fetch_data(symbol: str):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)
            
            return cache_manager.get_or_set(cache_key, lambda: func(*args, **kwargs), ttl)
        
        return wrapper
    return decorator
