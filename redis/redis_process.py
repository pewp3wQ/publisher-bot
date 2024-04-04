from typing import Any
from aioredis import Redis

from config import load_config

cfg = load_config('.env')
redis_url = cfg.redis_data.url
redis_port = cfg.redis_data.port


async def connect_to_redis():
    redis = await Redis.from_url(f"redis://{redis_url}:{redis_port}", db=1, encoding="utf-8", decode_responses=True)
    return redis


async def set_data(user_id: int, user_dict: dict[str, Any]) -> Any:
    redis = await connect_to_redis()
    if await redis.hset(user_id, user_dict):
        return True
    else:
        return False


async def get_data(user_id: int) -> hash:
    redis = await connect_to_redis()
    result = await redis.hgetall(user_id)

    return result
