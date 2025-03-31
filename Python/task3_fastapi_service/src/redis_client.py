
from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

redis = None
cache_initialized = False

async def init_redis():
    global redis, cache_initialized
    redis = aioredis.from_url("redis://redis_app:5370")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    cache_initialized = True
    
async def get_redis():
    if redis is None:
        raise RuntimeError("Redis is not initialized")
    return redis