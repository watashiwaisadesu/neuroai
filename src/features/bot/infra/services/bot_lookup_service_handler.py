from uuid import UUID
from src.features.bot.domain.entities.bot_entity import BotEntity
from src.features.bot.domain.repositories.bot_unit_of_work import BotUnitOfWork
from src.features.bot.exceptions.bot_exceptions import BotNotFoundError
from src.features.conversation.domain.services.bot_lookup_service import BotLookupService


class BotLookupServiceHandler(BotLookupService):
    def __init__(self, bot_uow: BotUnitOfWork):
        self._bot_uow = bot_uow

    async def get_bot(self, bot_uid: UUID) -> BotEntity:
        async with self._bot_uow:
            bot = await self._bot_uow.bot_repository.find_by_uid(bot_uid)
            if not bot:
                raise BotNotFoundError(f"Bot configuration not found for UID: {bot_uid}")
            return bot