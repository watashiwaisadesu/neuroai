# src/features/conversation/application/queries/get_playground_conversation/get_playground_conversation_query_handler.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass, field

from src.core.base.query import BaseQueryHandler
from src.core.mediator.mediator import Mediator
from src.features.bot.application.services.bot_access_service import BotAccessService  # Import BotAccessService
from src.features.bot.exceptions.bot_exceptions import BotAccessDeniedError, BotNotFoundError  # Specific bot exceptions
from src.features.conversation.api.v1.dtos.get_single_conversation_dto import (  # Import from get_single_conversation_dto
    GetConversationResponseDTO,
    ConversationDTO,  # Used for mapper init
    # No longer needed directly here for handler logic: BotInfoDTO, SenderInfoDTO, OwnerInfoDTO, MessageDTO,
)
from src.features.conversation.application.mappers.conversation_dto_mapper import \
    ConversationDTOMapper  # Import your mapper
from src.features.conversation.domain.entities.conversation_entity import ConversationEntity  # For mapper init
from src.features.conversation.domain.enums import ChatPlatform
from src.features.conversation.domain.uow.chat_unit_of_work import ConversationUnitOfWork
from src.features.conversation.exceptions.conversation_exceptions import ConversationNotFoundError  # Re-use exceptions
from .get_playground_conversation_query import GetPlaygroundConversationQuery  # Assuming this query is correct

# No longer directly importing HTTPException here
# from fastapi import HTTPException, status



@dataclass
class GetPlaygroundConversationQueryHandler(BaseQueryHandler[GetPlaygroundConversationQuery, GetConversationResponseDTO]):
    _unit_of_work: ConversationUnitOfWork
    _mediator: Mediator
    _bot_access_service: BotAccessService # Inject BotAccessService
    _conversation_dto_mapper: ConversationDTOMapper = field(init=False, repr=False) # Inject mapper

    def __post_init__(self):
        # Initialize the mapper
        self._conversation_dto_mapper = ConversationDTOMapper(ConversationEntity, ConversationDTO)

    async def __call__(self, query: GetPlaygroundConversationQuery) -> GetConversationResponseDTO:
        bot_uid_to_find = query.bot_uid
        user_uid = query.user_uid

        logger.info(f"Fetching playground conversation for bot UID: {bot_uid_to_find} by user UID: {user_uid}")

        # 1. Check if the user has access to this specific bot
        try:
            # This method should check if the bot exists and if the user has access to it.
            # It should raise BotNotFoundError or BotAccessDeniedError if not.
            await self._bot_access_service.check_single_bot_access(
                user_uid=user_uid,
                bot_uid=bot_uid_to_find,
                allowed_roles=["user", "admin"] # Or specific roles for playground access
            )
            logger.debug(f"User {user_uid} has access to bot {bot_uid_to_find}.")
        except (BotNotFoundError, BotAccessDeniedError) as e:
            logger.warning(f"User {user_uid} access denied to bot {bot_uid_to_find}: {e}")
            # Re-raise as a more generic access denied for conversation endpoint
            raise BotAccessDeniedError(f"Not authorized to access the bot's playground conversation.")

        # 2. Find the playground conversation for the bot
        async with self._unit_of_work as uow:
            conversation = await uow.conversation_repository.find_single_by_bot_uid_and_platform(
                bot_uid=bot_uid_to_find,
                platform=ChatPlatform.PLAYGROUND,
                load_messages=True
            )

        if not conversation:
            logger.info(f"No playground conversation found for bot {bot_uid_to_find}.")
            raise ConversationNotFoundError(f"Playground conversation not found for bot {bot_uid_to_find}.")

        # Additional validation (should ideally be handled by the repository if platform is strict)
        if conversation.platform != ChatPlatform.PLAYGROUND:
            logger.error(f"Conversation {conversation.uid} found for bot {bot_uid_to_find} has incorrect platform: {conversation.platform}. Expected PLAYGROUND.")
            raise RuntimeError("Found conversation with incorrect platform type for playground.") # This indicates a data integrity issue

        # 3. Map ConversationEntity to ConversationDTO
        try:
            conversation_dto = self._conversation_dto_mapper.to_dto(conversation)
            if not conversation_dto:
                logger.error(f"Mapper returned None for conversation {conversation.uid}.")
                raise RuntimeError(f"Failed to map conversation {conversation.uid} to DTO.")
        except Exception as e:
            logger.error(f"Error during mapping conversation {conversation.uid} to DTO: {e}", exc_info=True)
            raise RuntimeError(f"Failed to process conversation data for {conversation.uid}.") from e

        logger.info(f"Successfully retrieved playground conversation {conversation.uid} for bot {bot_uid_to_find}.")
        # 4. Return the response wrapper DTO
        return GetConversationResponseDTO(
            message="Playground conversation retrieved successfully.",
            conversation=conversation_dto
        )