# src/features/conversation/application/queries/get_single_bot_conversation/get_single_bot_conversation_query_handler.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass, field # Import 'field' for mapper injection

# No longer directly importing HTTPException here
# from fastapi import HTTPException, status

from src.core.base.query import BaseQueryHandler
from src.core.mediator.mediator import Mediator
from src.features.bot.application.services.bot_access_service import BotAccessService
# Import the new response DTO and the core ConversationDTO
from src.features.conversation.api.v1.dtos.get_single_conversation_dto import (
    GetConversationResponseDTO,
    ConversationDTO, # Used for mapper init
    # No longer needed directly here: BotInfoDTO, SenderInfoDTO, OwnerInfoDTO, MessageDTO,
)
from src.features.conversation.application.mappers.conversation_dto_mapper import ConversationDTOMapper # Import your mapper
from src.features.conversation.application.queries.get_single_conversation.get_single_conversation_query import \
    GetSingleBotConversationQuery # Note: original file name was get_single_bot_conversation_query.py
from src.features.conversation.domain.entities.conversation_entity import ConversationEntity # For mapper init
from src.features.conversation.domain.uow.chat_unit_of_work import ConversationUnitOfWork
# Import specific exceptions that should be raised by the handler
from src.features.conversation.exceptions.conversation_exceptions import ConversationNotFoundError, BotAccessDeniedError # Assuming these exist
from src.features.bot.exceptions.bot_exceptions import BotNotFoundError # If check_single_bot_access can raise this





@dataclass
class GetSingleBotConversationQueryHandler(BaseQueryHandler[GetSingleBotConversationQuery, GetConversationResponseDTO]):
    _unit_of_work: ConversationUnitOfWork
    _bot_access_service: BotAccessService
    _mediator: Mediator # Keep if publishing events (not directly used in this snippet's current logic, but good practice)
    _conversation_dto_mapper: ConversationDTOMapper = field(init=False, repr=False) # Inject mapper

    def __post_init__(self):
        # Initialize the mapper
        self._conversation_dto_mapper = ConversationDTOMapper(ConversationEntity, ConversationDTO)

    async def __call__(self, query: GetSingleBotConversationQuery) -> GetConversationResponseDTO:
        logger.info(f"Fetching single conversation {query.conversation_uid} for user UID: {query.user_uid}")

        # 1. Fetch conversation
        async with self._unit_of_work as uow:
            conversation = await uow.conversation_repository.find_by_uid(
                query.conversation_uid, # Corrected from conversation_id to conversation_uid
                load_messages=True
            )

        if not conversation:
            logger.warning(f"Conversation {query.conversation_uid} not found.")
            raise ConversationNotFoundError(f"Conversation with UID {query.conversation_uid} not found.")

        # 2. Validate user access to the bot associated with the conversation
        try:
            # check_single_bot_access handles if bot is not found or access is denied
            await self._bot_access_service.check_single_bot_access(
                user_uid=query.user_uid,
                bot_uid=conversation.bot_uid,
                allowed_roles=["user", "admin"] # Assuming user can view any bot they have access to
            )
        except (BotNotFoundError, BotAccessDeniedError) as e: # Catch access service exceptions
            logger.warning(f"Access denied for user {query.user_uid} to conversation {query.conversation_uid} via bot {conversation.bot_uid}: {e}")
            raise BotAccessDeniedError(f"Not authorized to access conversation {query.conversation_uid}.") # Re-raise as a conversation-specific access error

        # 3. Map ConversationEntity to ConversationDTO
        try:
            conversation_dto = self._conversation_dto_mapper.to_dto(conversation)
            if not conversation_dto:
                logger.error(f"Mapper returned None for conversation {conversation.uid}. This should not happen if entity is not None.")
                raise RuntimeError(f"Failed to map conversation {conversation.uid} to DTO.")
        except Exception as e:
            logger.error(f"Error during mapping conversation {conversation.uid} to DTO: {e}", exc_info=True)
            raise RuntimeError(f"Failed to process conversation data for {conversation.uid}.") from e


        logger.info(f"Successfully retrieved conversation {conversation.uid} for user {query.user_uid}.")
        # 4. Return the response wrapper DTO
        return GetConversationResponseDTO(
            message="Conversation retrieved successfully.",
            conversation=conversation_dto
        )