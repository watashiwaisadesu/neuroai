# src/features/conversation/application/mappers/conversation_dto_mapper.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from typing import List, Optional, Type
from datetime import datetime

from src.features.conversation.api.v1.dtos.get_single_conversation_dto import (
    ConversationDTO,
    BotInfoDTO,
    SenderInfoDTO,
    OwnerInfoDTO,
    MessageDTO,
)
from src.features.conversation.domain.entities.conversation_entity import ConversationEntity
from src.features.conversation.domain.entities.message_entity import MessageEntity



class ConversationDTOMapper:
    """
    Mapper for converting ConversationEntity to ConversationDTO,
    including nested message entities.
    """
    def __init__(self, entity_cls: Type[ConversationEntity], dto_cls: Type[ConversationDTO]):
        self.entity_cls = entity_cls
        self.dto_cls = dto_cls
        logger.debug(f"ConversationDTOMapper initialized for {entity_cls.__name__} and {dto_cls.__name__}")

    def _map_messages(self, messages: List[MessageEntity]) -> List[MessageDTO]:
        """Helper to map a list of MessageEntity to MessageDTO."""
        if not messages:
            return []
        # Sort messages by timestamp to ensure chronological order in DTO
        sorted_messages = sorted(messages, key=lambda m: m.timestamp if m.timestamp else datetime.min)
        return [
            MessageDTO(
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp
            )
            for msg in sorted_messages
        ]

    def to_dto(self, entity: ConversationEntity) -> Optional[ConversationDTO]:
        """Maps a ConversationEntity domain object to a ConversationDTO."""
        if not entity:
            logger.warning("Attempted to map a None ConversationEntity to DTO.")
            return None

        logger.debug(f"Mapping ConversationEntity (UID: {entity.uid}) to ConversationDTO.")
        try:
            sender_number_val = entity.participant.sender_number
            if sender_number_val == "":  # If your DB stores empty strings instead of None
                sender_number_val = None

            conversation_dto = self.dto_cls(
                conversation_uid=entity.uid,
                platform=entity.platform.value if hasattr(entity.platform, 'value') else entity.platform, # Handle Enum conversion
                bot=BotInfoDTO(
                    bot_uid=entity.bot_uid,
                    bot_name=entity.bot_name # Assuming bot_name is on ConversationEntity
                ),
                sender=SenderInfoDTO(
                    sender_id=entity.participant.sender_id,
                    sender_number=sender_number_val,
                    sender_username=entity.participant.sender_nickname
                ),
                owner=OwnerInfoDTO(owner_id=entity.owner_uid), # Corrected to owner_uid
                messages=self._map_messages(entity.messages), # Use helper for messages
                crm_catalog_id=entity.crm_catalog_id,
                updated_at=getattr(entity, 'updated_at', None) # Use getattr for robustness
            )
            logger.debug(f"Successfully mapped ConversationEntity {entity.uid} to ConversationDTO.")
            return conversation_dto
        except Exception as e:
            logger.error(f"Error mapping ConversationEntity {entity.uid} to DTO: {e}", exc_info=True)
            raise RuntimeError(f"Failed to map conversation entity {entity.uid} to DTO.") from e