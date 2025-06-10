import redis.asyncio as aioredis
from src.config import Settings

__settings = Settings()
redis_client = aioredis.from_url(__settings.REDIS_URL)