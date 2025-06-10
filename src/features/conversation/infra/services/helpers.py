from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from typing import Optional
from uuid import UUID

from src.features.bot.domain.entities.bot_entity import BotEntity
from src.features.bot.domain.repositories.bot_unit_of_work import BotUnitOfWork
from src.features.bot.exceptions.bot_exceptions import BotNotFoundError
# Import DTOs, Query Interface, Entities, Dependencies
from src.features.conversation.domain.entities.conversation_entity import ConversationEntity
from src.features.conversation.domain.entities.message_entity import MessageEntity
from src.features.conversation.domain.enums import ChatPlatform
from src.features.conversation.domain.uow.chat_unit_of_work import ConversationUnitOfWork
from src.features.conversation.domain.value_objects.participant_info import ParticipantInfo

# Import dependency providers (assuming these exist)



#
# async def _get_bot(bot_uow: BotUnitOfWork, bot_uid: UUID) -> BotEntity:
#     """Helper function to get bot details."""
#     async with bot_uow:
#         bot = await bot_uow.bot_repository.find_by_uid(bot_uid)
#         if not bot:
#             raise BotNotFoundError(f"Bot configuration not found for UID: {bot_uid}")
#         return bot


async def _get_or_create_conversation(
    chat_uow: ConversationUnitOfWork,
    platform: ChatPlatform,
    sender_id: str,
    bot_uid: UUID,
    conversation_owner_uid: UUID,
    bot_name: Optional[str], # Changed from str to Optional[str]
    sender_number: Optional[str],
    sender_nickname: Optional[str],
) -> ConversationEntity:
    """
    Helper function to get an existing conversation or create a new one.
    Assumes messages are loaded by the repository method if the conversation exists.
    """
    # This method should use the repository to find based on a unique key.
    # Example: platform, sender_id, bot_uid, owner_uid (or a subset that defines uniqueness)
    # The repository method find_by_platform_sender_bot_owner should handle loading messages.
    conversation = await chat_uow.conversation_repository.find_by_platform_and_sender_id( # Example method name
        platform=platform,
        sender_id=sender_id,
        bot_uid=bot_uid
    )

    if not conversation:
        logger.info(f"No existing conversation found for bot {bot_uid}, sender {sender_id}, platform {platform.value}. Creating new.")
        participant_info = ParticipantInfo(
            sender_id=sender_id,
            sender_number=sender_number,
            sender_nickname=sender_nickname,
        )
        conversation = ConversationEntity(
            owner_uid=conversation_owner_uid,
            bot_uid=bot_uid,
            platform=platform,
            participant=participant_info,
            bot_name=bot_name, # Pass bot_name
            initial_messages=[] # New conversation starts with no messages
        )
        # Persist the new conversation
        conversation = await chat_uow.conversation_repository.create(conversation)
        logger.info(f"Created new conversation with UID: {conversation.uid}")
    else:
        logger.info(f"Found existing conversation: {conversation.uid} with {len(conversation.messages)} messages.")
        # Messages should already be loaded by the repository call above
        # No need to re-add them here.

    return conversation


async def _add_message_to_conversation(
    chat_uow: ConversationUnitOfWork, conversation_uid: UUID, message: MessageEntity
) -> None:
    """Helper function to add a message to a conversation."""
    async with chat_uow:
        message = await chat_uow.message_repository.create(message, conversation_uid)
        #conversation.add_message(message) # Removed, handled by repo
        # await chat_uow.conversation_repository.update(conversation) #Removed conversation parameter
        # await chat_uow.commit()
        logger.debug(f"Added message {message.uid} to conversation {conversation_uid}")


