from src.infra.services.redis.redis_service_handler import RedisServiceHandler
from src.infra.services.redis.redis_service import RedisService


def get_redis_service() -> RedisService:
    return RedisServiceHandler()