from redis.exceptions import ConnectionError
from src.infra.services.redis.redis_client import redis_client
from src.infra.services.redis.redis_service import RedisService
from src.infra.services.redis.exceptions import RedisConnectionError

class RedisServiceHandler(RedisService):
    async def set_key(self, key: str, value: str, expire: int = 3600) -> None:
        try:
            result = await redis_client.set(key, value, ex=expire)
            print(f"✅ SET Redis: {key=} -> {result=}")

        except ConnectionError:
            raise RedisConnectionError()

    async def get_key(self, key: str):
        try:
            return await redis_client.get(key)
        except ConnectionError:
            raise RedisConnectionError()

    async def delete_key(self, key: str) -> None:
        try:
            await redis_client.delete(key)
        except ConnectionError:
            raise RedisConnectionError()