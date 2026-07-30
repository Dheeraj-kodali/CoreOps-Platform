import json
import logging
from typing import Optional, Any, Callable
from functools import wraps
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Enterprise Redis L2 Cache Manager implementing the Cache-Aside pattern.
    """

    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self._redis: Optional[aioredis.Redis] = None

    async def get_client(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = aioredis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)
        return self._redis

    async def get(self, key: str) -> Optional[Any]:
        try:
            client = await self.get_client()
            val = await client.get(key)
            if val:
                logger.debug(f"[Cache HIT] Key: {key}")
                return json.loads(val)
            logger.debug(f"[Cache MISS] Key: {key}")
            return None
        except Exception as e:
            logger.warning(f"[Cache Error] Failed reading key '{key}': {str(e)}")
            return None

    async def set(self, key: str, value: Any, expire_seconds: int = 300) -> bool:
        try:
            client = await self.get_client()
            serialized = json.dumps(value, default=str)
            await client.set(key, serialized, ex=expire_seconds)
            logger.debug(f"[Cache SET] Key: {key} (TTL: {expire_seconds}s)")
            return True
        except Exception as e:
            logger.warning(f"[Cache Error] Failed writing key '{key}': {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        try:
            client = await self.get_client()
            await client.delete(key)
            logger.debug(f"[Cache DELETE] Key: {key}")
            return True
        except Exception as e:
            logger.warning(f"[Cache Error] Failed deleting key '{key}': {str(e)}")
            return False

    async def invalidate_pattern(self, pattern: str) -> int:
        try:
            client = await self.get_client()
            keys = await client.keys(pattern)
            if keys:
                await client.delete(*keys)
                logger.info(f"[Cache INVALIDATE] Flushed {len(keys)} keys matching '{pattern}'")
                return len(keys)
            return 0
        except Exception as e:
            logger.warning(f"[Cache Error] Failed invalidating pattern '{pattern}': {str(e)}")
            return 0


# Global Cache Manager Singleton
cache_manager = CacheManager()


def cached(prefix: str, expire_seconds: int = 300):
    """
    Decorator for caching async function returns using Cache-Aside strategy.
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key_parts = [prefix] + [str(arg) for arg in args[1:]] + [f"{k}={v}" for k, v in sorted(kwargs.items())]
            cache_key = ":".join(key_parts)

            cached_val = await cache_manager.get(cache_key)
            if cached_val is not None:
                return cached_val

            result = await func(*args, **kwargs)
            if result is not None:
                await cache_manager.set(cache_key, result, expire_seconds=expire_seconds)
            return result

        return wrapper

    return decorator
