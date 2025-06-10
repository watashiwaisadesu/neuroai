# src/features/conversation/dependencies.py (New file)

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from typing import Dict

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.features.bot.dependencies import get_bot_unit_of_work
from src.features.bot.domain.repositories.bot_unit_of_work import BotUnitOfWork
from src.features.conversation.domain.services.process_incoming_message_command import \
    ProcessIncomingMessageCommand
from src.features.conversation.infra.services.process_incoming_message_impl import \
    ProcessIncomingMessageCommandHandler
# Import Interfaces, Implementations, Base Providers
from src.features.conversation.domain.uow.chat_unit_of_work import ConversationUnitOfWork
from src.features.conversation.infra.persistence.uow.chat_unit_of_work_impl import ConversationUnitOfWorkImpl # Import UoW Impl
from src.features.generation.application.services.generation_service import IGenerationService
from src.features.generation.dependencies import get_stub_generation_service, get_deepseek_generation_service
from src.infra.persistence.connection.sqlalchemy_engine import get_async_db # Import DB Session provider



# --- Chat UoW Provider ---
async def get_chat_unit_of_work(
    session: AsyncSession = Depends(get_async_db),
) -> ConversationUnitOfWork:
    """Provides an instance of the Chat Unit of Work."""
    logger.debug("Providing Chat Unit of Work")
    return ConversationUnitOfWorkImpl(session=session)



def get_process_incoming_message_use_case(
    chat_uow: ConversationUnitOfWork = Depends(get_chat_unit_of_work),
    bot_uow: BotUnitOfWork = Depends(get_bot_unit_of_work),
    # Inject individual generation services
    stub_generation_service: IGenerationService = Depends(get_stub_generation_service),
    deepseek_generation_service: IGenerationService = Depends(get_deepseek_generation_service),
    # openai_generation_service: IGenerationService = Depends(get_openai_generation_service), # Example
) -> ProcessIncomingMessageCommand:
    """
    Provides an instance of the IProcessIncomingMessageCommand use case,
    injecting available generation services.
    """
    logger.debug("Providing ProcessIncomingMessageCommand Use Case with generation services")

    # Create a map of available generation services
    available_generation_services: Dict[str, IGenerationService] = {
        "stub": stub_generation_service,
        "deepseek-v2:16b": deepseek_generation_service,
        # Add other services here as they are implemented
    }

    return ProcessIncomingMessageCommandHandler(
        chat_uow=chat_uow,
        bot_uow=bot_uow,
        available_generation_services=available_generation_services, # Pass the map
    )


