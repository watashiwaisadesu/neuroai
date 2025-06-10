from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

from src.core.base.query import BaseQueryHandler
from src.core.mediator.mediator import Mediator
from src.features.bot.application.services.bot_access_service import BotAccessService
from src.features.conversation.api.v1.dtos.get_all_conversations_dto import (
    ConversationMinimalDTO,
    LastMessageItemDTO,
    BotInfoDTO,
    SenderInfoDTO,
    OwnerInfoDTO,
    GetConversationsResponseDTO  # <-- NEW: Import the response wrapper DTO
)
from src.features.conversation.domain.entities.message_entity import MessageEntity
from src.features.conversation.domain.enums import ChatPlatform
from src.features.conversation.domain.uow.chat_unit_of_work import ConversationUnitOfWork
from .get_all_conversations_query import GetAllConversationsQuery  # Assuming it's in the same directory



@dataclass
class GetAllConversationsQueryHandler(BaseQueryHandler[GetAllConversationsQuery, GetConversationsResponseDTO]): # <-- Changed return type
    _unit_of_work: ConversationUnitOfWork
    _mediator: Mediator
    _bot_access_service: BotAccessService

    async def __call__(self, query: GetAllConversationsQuery) -> GetConversationsResponseDTO: # <-- Changed return type
        user_uid = query.user # Use the more specific user_uid for clarity
        platform_filter = query.platform_filter

        logger.info(f"Fetching all conversations for user UID: {user_uid} with platform filter: {platform_filter}")

        # Get accessible bots for the user
        # Note: get_accessible_bots typically returns BotEntity objects.
        # Ensure it's correctly handling the user ID (UUID vs str).
        accessible_bots = await self._bot_access_service.get_accessible_bots(user_uid=user_uid)
        bot_uids = [bot.uid for bot in accessible_bots]

        if not bot_uids:
            message = "No accessible bots found, therefore no conversations to display."
            logger.info(message)
            return GetConversationsResponseDTO(message=message, conversations=[])

        conversations_found: List[ConversationMinimalDTO] = []

        async with self._unit_of_work as uow: # Use the UoW context
            if platform_filter:
                try:
                    platform_enum = ChatPlatform(platform_filter)
                    conversations = await uow.conversation_repository.find_by_bot_uids_and_platform(
                        bot_uids=bot_uids,
                        platform=platform_enum,
                        load_messages=True
                    )
                except ValueError:
                    logger.warning(f"Invalid platform filter provided: {platform_filter}. No conversations returned.")
                    return GetConversationsResponseDTO(message=f"Invalid platform filter: '{platform_filter}'.", conversations=[])
            else:
                conversations = await uow.conversation_repository.find_by_bot_uids(
                    bot_uids=bot_uids,
                    load_messages=True
                )
        logger.debug(f"Retrieved {len(conversations)} raw conversation entities.")

        for conv in conversations:
            try:
                last_msg = self._get_last_message(conv.messages)
                last_message_dto = LastMessageItemDTO(
                    content=last_msg.content,
                    timestamp=last_msg.timestamp
                ) if last_msg else None

                conversations_found.append(ConversationMinimalDTO(
                    conversation_uid=conv.uid,
                    platform=conv.platform.value,
                    bot=BotInfoDTO(
                        bot_uid=conv.bot_uid,
                        bot_name=conv.bot_name # Assuming bot_name is on ConversationEntity
                    ),
                    sender=SenderInfoDTO(
                        sender_id=conv.participant.sender_id,
                        sender_number=conv.participant.sender_number,
                        sender_username=conv.participant.sender_nickname
                    ),
                    owner=OwnerInfoDTO(owner_uid=conv.owner_uid),
                    last_message=last_message_dto,
                    crm_catalog_id=conv.crm_catalog_id,
                    updated_at=getattr(conv, 'updated_at', None)
                ))
            except Exception as e:
                logger.error(f"Failed to process conversation {conv.uid}: {e}", exc_info=True)

        # Sort the results by updated_at
        conversations_found.sort(key=lambda dto: dto.updated_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)

        message = f"Successfully retrieved {len(conversations_found)} conversation(s) for user {user_uid}."
        if platform_filter:
            message += f" Filtered by platform: '{platform_filter}'."
        elif not conversations_found:
             message = f"No conversations found for user {user_uid}."

        logger.info(message)
        return GetConversationsResponseDTO(
            message=message,
            conversations=conversations_found
        )

    def _get_last_message(self, messages: list[MessageEntity]) -> Optional[MessageEntity]:
        """
        Helper method to get the last message from a list of messages.
        Assumes messages are already sorted or the last element is the latest.
        """
        if not messages:
            return None
        # It's safer to sort by timestamp here if messages are not guaranteed to be ordered
        # return sorted(messages, key=lambda msg: msg.timestamp if msg.timestamp else datetime.min.replace(tzinfo=timezone.utc))[-1]
        return messages[-1] # Assuming messages are ordered by creation/update time