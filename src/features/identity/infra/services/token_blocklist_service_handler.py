from src.features.identity.application.services.token_blocklist_service import TokenBlocklistService
from src.infra.services.redis.redis_service import RedisService

class TokenBlocklistServiceHandler(TokenBlocklistService):
    def __init__(self, redis_service: RedisService):
        self.redis = redis_service

    async def block_token(self, jti: str, expiry: int) -> None:
        await self.redis.set_key(jti, "", expire=expiry)

    async def is_blocked(self, jti: str) -> bool:
        val = await self.redis.get_key(jti)
        return val is not None

    async def unblock_token(self, jti: str) -> None:
        await self.redis.delete_key(jti)