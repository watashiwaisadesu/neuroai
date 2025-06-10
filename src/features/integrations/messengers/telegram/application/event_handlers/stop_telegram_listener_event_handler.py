# src/features/integrations/telegram/application/event_handlers/stop_telegram_listener_handler.py

from dataclasses import dataclass
from src.core.base.event import BaseEventHandler
from src.features.bot.domain.events.service_unlinked_event import ServiceUnlinkedEvent
from src.features.conversation.domain.enums import ChatPlatform
from src.features.integrations.messengers.telegram.application.services.telethon_client_service import TelethonClientService


@dataclass(kw_only=True)
class StopTelegramListenerHandler(BaseEventHandler[ServiceUnlinkedEvent, None]):
    _telethon_service: TelethonClientService

    async def handle(self, event: ServiceUnlinkedEvent) -> None:
        print(f"stopping listener:{event.service_uid}")
        # if event.platform != ChatPlatform.TELEGRAM.value:
        #     return  # Ignore unrelated platforms
        #
        # if not event.linked_account_uid:
        #     return  # Nothing to stop
        #
        # try:
        #     print("stopping listeners")
        #     await self._telethon_service.stop_message_listener(service_uid=event.service_uid)
        # except Exception as ex:
        #     # Log it, don’t blow up the system over failed shutdown
        #     from src.infra.logging.setup_async_logging import async_logger
# logger = async_logger
        #     logging.getLogger(__name__).error(
        #         f"Failed to stop Telegram listener for service {event.service_uid}: {ex}",
        #         exc_info=True
        #     )
