from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

redis = None

async def init_redis():
    global redis
    redis = aioredis.from_url("redis://redis_app:5370")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    
async def get_redis():
    if redis is None:
        raise RuntimeError("Redis is not initialized")
    return redis