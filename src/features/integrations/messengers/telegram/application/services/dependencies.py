from src.infra.logging.setup_async_logging import async_logger
logger = async_logger

from src.config import Settings
from fastapi import Depends

from src.features.conversation.dependencies import get_process_incoming_message_use_case
from src.features.conversation.domain.services.process_incoming_message_command import ProcessIncomingMessageCommand
# Import Command Interfaces and Implementations
from src.features.integrations.messengers.telegram.application.services.telegram_event_handler_service import \
    TelegramEventHandlerService
from src.features.integrations.messengers.telegram.application.services.telegram_event_handler_service_impl import \
    TelegramEventHandlerServiceHandler
# get_telegram_unit_of_work assumed to be defined in this file
# from .uow.telegram_unit_of_work_impl import TelegramUnitOfWorkImpl # For get_telegram_unit_of_work
from src.features.integrations.messengers.telegram.application.services.telethon_client_service import TelethonClientService
from src.features.integrations.messengers.telegram.application.services.telethon_client_service_impl import \
    TelethonClientServiceImpl
from src.features.integrations.messengers.telegram.dependencies import get_telegram_unit_of_work
# Import UoW provider, service providers
from src.features.integrations.messengers.telegram.domain.uow.telegram_unit_of_work import TelegramUnitOfWork




def get_telethon_client_service(
) -> TelethonClientService:
    __settings = Settings()
    """Provides an instance of the ITelethonClientService."""
    logger.debug("Providing TelethonClientServiceImpl")
    # TelethonClientServiceImpl takes settings for API ID/Hash
    return TelethonClientServiceImpl(settings=__settings)


def get_telegram_event_handler_service(
    process_message_command: ProcessIncomingMessageCommand = Depends(get_process_incoming_message_use_case),
    telegram_uow: TelegramUnitOfWork = Depends(get_telegram_unit_of_work),
    telethon_service: TelethonClientService = Depends(get_telethon_client_service)
) -> TelegramEventHandlerService: # Return the interface
    """Provides an instance of the TelegramEventHandlerService."""
    logger.debug("Providing TelegramEventHandlerServiceImpl")
    return TelegramEventHandlerServiceHandler(
        process_message_command=process_message_command,
        telegram_uow=telegram_uow,
        telethon_service=telethon_service
    )
