import os
import redis.asyncio as aioredis
from typing import Optional
from fastapi import Request

REDIS_URL = os.getenv("REDIS_URL") or os.getenv("UPSTASH_REDIS_REST_URL") or os.getenv("UPSTASH_REDIS_TCP_URL")

async def init_redis(app):
    """Initialize async Redis client and attach to app.state."""
    if not REDIS_URL:
        return
    client = aioredis.from_url(REDIS_URL, decode_responses=True)
    # attach
    app.state.redis = client
    try:
        await client.ping()
    except Exception:
        pass

async def close_redis(app):
    client: Optional[aioredis.Redis] = getattr(app.state, "redis", None)
    if client is not None:
        try:
            await client.close()
        except Exception:
            pass


def get_redis(request: Request):
    return request.app.state.redis
