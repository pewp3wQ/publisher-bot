from typing import Any
from aioredis import Redis
import pickle

from config import load_config

cfg = load_config('.env')
redis_url = cfg.redis_data.url
redis_port = cfg.redis_data.port


async def connect_to_redis():
    redis = await Redis(host=f"redis://{redis_url}", db=1, decode_responses=True)
    return redis


async def set_data(user_id: int, user_dict: dict[str, Any]) -> Any:
    redis = await connect_to_redis()
    if await redis.set(user_id, pickle.dumps(user_dict)):
        return True
    else:
        return False


async def get_data(user_id: int) -> hash:
    redis = await connect_to_redis()
    result = await redis.get(pickle.loads(user_id))

    return result
