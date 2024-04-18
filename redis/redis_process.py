from typing import Any
import logging
from aioredis import Redis
import pickle

from config import load_config
logger = logging.getLogger(__name__)

TEMP_REDIS = {}

cfg = load_config('.env')
redis_url = cfg.redis_data.url
redis_port = cfg.redis_data.port


async def connect_to_redis():
    redis = await Redis.from_url(f"redis://{redis_url}:{redis_port}", db=1)
    return redis


async def set_data(user_id: int, user_dict: dict[str, Any]) -> Any:
    # TEMP_REDIS[user_id] = user_dict
    #
    # logger.info(f'{user_id} -- {user_dict} -- {TEMP_REDIS}')
    #
    # if len(TEMP_REDIS) != 0:
    #     return True
    # else:
    #     return False
    redis = await connect_to_redis()
    data_dump = pickle.dumps(user_dict)
    if await redis.set(user_id, data_dump):
        return True
    else:
        return False


async def get_data(user_id: int) -> Any:
    # result = TEMP_REDIS.get(user_id)
    #
    # logger.info(f'{user_id} -- {result}')
    #
    # return result

    redis = await connect_to_redis()
    result = await redis.get(user_id)
    result_load = pickle.loads(result)
    return result_load
