# 4. Infrastructure Event Handler for Redis (src/infra/services/redis/event_handlers/bot_expiry_handler.py)
from dataclasses import dataclass
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger

from src.core.base.event import BaseEventHandler
from src.features.bot.domain.events.bot_events import BotExpirySetEvent
from src.infra.services.redis.redis_service import RedisService




@dataclass(kw_only=True)
class BotExpiryHandler(BaseEventHandler[BotExpirySetEvent, None]):
    """Infrastructure handler that sets bot expiry in Redis"""
    _redis_service: RedisService

    async def handle(self, event: BotExpirySetEvent) -> None:
        try:
            redis_key = f"bot_expiry:{event.bot_uid}"
            await self._redis_service.set_key(
                redis_key,
                "pending",
                expire=event.expiry_seconds
            )
            logger.debug(
                f"Set Redis expiry for bot {event.bot_uid}: "
                f"{event.expiry_seconds} seconds"
            )
        except Exception as e:
            logger.error(f"Failed to set Redis expiry for bot {event.bot_uid}: {e}")