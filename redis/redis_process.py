from typing import Any
from aioredis import Redis
import pickle

from config import load_config

cfg = load_config('.env')
redis_url = cfg.redis_data.url
redis_port = cfg.redis_data.port


async def connect_to_redis():
    redis = await Redis.from_url(f"redis://{redis_url}:{redis_port}", db=1)
    return redis


async def set_data(user_id: int, user_dict: dict[str, Any]) -> Any:
    redis = await connect_to_redis()
    data_dump = pickle.dumps(user_dict)
    if await redis.set(user_id, data_dump):
        return True
    else:
        return False


async def get_data(user_id: int) -> Any:
    redis = await connect_to_redis()
    result = await redis.get(user_id)
    result_load = pickle.loads(result)
    return result_load
