from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from typing import Optional, Type

from src.features.bot.api.v1.dtos.bot_participant import BotParticipantDTO
from src.features.bot.domain.entities.bot_participant_entity import BotParticipantEntity
from src.features.bot.application.services.user_lookup_service import UserInfo # Import UserInfo from UserLookupService



class BotParticipantDTOMapper:
    """
    Mapper for converting BotParticipantEntity to BotParticipantDTO.
    It can optionally enrich the DTO with user email and avatar from UserInfo.
    This class remains a regular Python class, suitable for its behavioral role.
    """
    def __init__(self, entity_cls: Type[BotParticipantEntity], dto_cls: Type[BotParticipantDTO]):
        """
        Initializes the mapper with the specific entity and DTO classes.
        """
        self.entity_cls = entity_cls
        self.dto_cls = dto_cls
        logger.debug(f"BotParticipantDTOMapper initialized for {entity_cls.__name__} and {dto_cls.__name__}")

    def to_dto(self, entity: BotParticipantEntity, user_info: Optional[UserInfo] = None) -> BotParticipantDTO:
        """
        Maps a BotParticipantEntity domain object to a BotParticipantDTO.
        Optionally takes UserInfo to populate user-specific details like email and avatar.
        Ensures all relevant entity fields, including inherited timestamps, are mapped.
        """
        if not entity:
            logger.warning("Attempted to map a None BotParticipantEntity to DTO.")
            raise ValueError("Entity cannot be None for mapping to DTO.")

        # Safely extract user email and avatar from UserInfo, providing None if not available
        email = user_info.email if user_info and user_info.email else None
        avatar = user_info.avatar_file_url if user_info and user_info.avatar_file_url else None

        try:
            # Map all fields from the BotParticipantEntity, including those inherited from BaseEntity.
            participant_dto = self.dto_cls(
                participant_uid=entity.uid, # The BaseEntity's UID serves as the participant_uid
                bot_uid=entity.bot_uid,
                user_uid=entity.user_uid,
                role=entity.role,
                created_at=entity.created_at, # Include created_at from the entity
                updated_at=entity.updated_at, # Include updated_at from the entity
                email=email,
                avatar=avatar
            )
            logger.debug(f"Mapped BotParticipantEntity {entity.uid} to BotParticipantDTO.")
            return participant_dto
        except Exception as e:
            logger.error(f"Error mapping BotParticipantEntity {getattr(entity, 'uid', 'N/A')} to DTO: {e}", exc_info=True)
            raise RuntimeError(f"Failed to map participant entity {getattr(entity, 'uid', 'N/A')} to DTO.") from e