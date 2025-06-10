# src/features/bot/application/services/i_bot_platform_linker_service.py (or bot_platform_linker_service_interface.py)
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from uuid import UUID

from src.features.bot.domain.entities.bot_entity import BotEntity
from src.features.bot.domain.entities.bot_service_entity import BotServiceEntity
from src.features.conversation.domain.enums import ChatPlatform

class BotPlatformLinkerService(ABC):
    """
    Interface for services that handle the logic of activating or creating
    bot service links for specific platforms.
    """

    @abstractmethod
    async def ensure_platform_service_active(
        self,
        target_bot_entity: BotEntity,
        platform: ChatPlatform,
        linked_account_uid: UUID,
        service_details: Optional[Dict[str, Any]] = None
    ) -> BotServiceEntity:
        """
        Ensures a service for the given platform is active for the bot,
        with the provided configuration.

        It should handle finding and activating a 'reserved' service,
        or creating a new one if necessary. All operations should be
        atomic within the bot domain's unit of work.

        Args:
            target_bot_entity: The BotEntity for which the service is being processed.
            platform: The ChatPlatform enum member (e.g., ChatPlatform.TELEGRAM).
            linked_account_uid: Any platform uid (telegram_uid, whatsapp_uid etc.)
            service_details: account id, name  and other info

        Returns:
            The activated or newly created BotServiceEntity.

        Raises:
            Exception or specific domain exceptions if the operation fails critically.
        """
        pass