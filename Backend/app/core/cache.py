"""
Redis Caching Service.
Provides caching layer for frequently accessed data.
"""
import json
import pickle
from typing import Optional, Any, Callable
from functools import wraps
import hashlib
import redis
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class CacheService:
    """
    Redis-based caching service with automatic serialization.
    """

    def __init__(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=False,  # Handle binary data
                max_connections=settings.REDIS_MAX_CONNECTIONS
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            self.redis_client = None

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate cache key from prefix and arguments.

        Args:
            prefix: Key prefix (e.g., "lead", "stats")
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Cache key string
        """
        # Create string representation of arguments
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])

        # Hash for long keys
        if len(key_parts) > 5:
            key_hash = hashlib.md5(
                ":".join(key_parts).encode()
            ).hexdigest()
            return f"{prefix}:{key_hash}"

        return f"{prefix}:{':'.join(key_parts)}"

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if not self.redis_client or not settings.CACHE_ENABLED:
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                # Try JSON first (faster)
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # Fallback to pickle for complex objects
                    return pickle.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get failed for key {key}: {e}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default from settings)

        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client or not settings.CACHE_ENABLED:
            return False

        if ttl is None:
            ttl = settings.CACHE_TTL_SECONDS

        try:
            # Try JSON serialization first (faster, readable)
            try:
                serialized = json.dumps(value)
            except (TypeError, ValueError):
                # Fallback to pickle for complex objects
                serialized = pickle.dumps(value)

            self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set failed for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            return False

        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete failed for key {key}: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.

        Args:
            pattern: Key pattern (e.g., "lead:*")

        Returns:
            Number of keys deleted
        """
        if not self.redis_client:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern failed for {pattern}: {e}")
            return 0

    def clear_all(self) -> bool:
        """
        Clear entire cache (use with caution).

        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            return False

        try:
            self.redis_client.flushdb()
            logger.warning("Cache cleared completely")
            return True
        except Exception as e:
            logger.error(f"Cache clear failed: {e}")
            return False

    def get_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        if not self.redis_client:
            return {"enabled": False}

        try:
            info = self.redis_client.info()
            return {
                "enabled": True,
                "used_memory": info.get("used_memory_human"),
                "total_keys": self.redis_client.dbsize(),
                "hit_rate": info.get("keyspace_hits", 0) /
                           (info.get("keyspace_hits", 0) + info.get("keyspace_misses", 1)),
                "connected_clients": info.get("connected_clients"),
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"enabled": True, "error": str(e)}


# Global cache service instance
cache = CacheService()


def cached(
    prefix: str,
    ttl: Optional[int] = None,
    key_builder: Optional[Callable] = None
):
    """
    Decorator for caching function results.

    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds
        key_builder: Optional function to build cache key from args

    Example:
        @cached("lead_stats", ttl=300)
        def get_lead_stats():
            return expensive_database_query()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                cache_key = cache._generate_key(prefix, *args, **kwargs)

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_value

            # Execute function
            logger.debug(f"Cache miss for {cache_key}")
            result = func(*args, **kwargs)

            # Store in cache
            cache.set(cache_key, result, ttl)

            return result

        # Add cache control methods
        wrapper.invalidate = lambda *args, **kwargs: cache.delete(
            key_builder(*args, **kwargs) if key_builder
            else cache._generate_key(prefix, *args, **kwargs)
        )
        wrapper.invalidate_all = lambda: cache.delete_pattern(f"{prefix}:*")

        return wrapper
    return decorator


class CacheKeys:
    """
    Centralized cache key definitions.
    """
    # Lead caching
    LEAD_BY_ID = "lead:id"
    LEAD_BY_SESSION = "lead:session"
    LEAD_STATS = "lead:stats"
    LEAD_LIST = "lead:list"
    LEAD_HOT_UNCONTACTED = "lead:hot:uncontacted"

    # Conversation caching
    CONV_BY_SESSION = "conv:session"
    CONV_ACTIVE = "conv:active"

    # Analytics caching
    ANALYTICS_DAILY = "analytics:daily"
    ANALYTICS_WEEKLY = "analytics:weekly"


# Cache TTL presets (in seconds)
class CacheTTL:
    """Time-to-live presets for different data types."""
    SHORT = 60  # 1 minute
    MEDIUM = 300  # 5 minutes
    LONG = 1800  # 30 minutes
    HOUR = 3600  # 1 hour
    DAY = 86400  # 24 hours
