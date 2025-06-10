from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from typing import Optional, Type

from src.features.bot.api.v1.dtos.minimal_bot_dto import MinimalBotDTO
from src.features.bot.domain.entities.bot_entity import BotEntity



class MinimalBotDTOMapper:
    """
    Mapper for converting a BotEntity domain object to a MinimalBotDTO.
    This mapper provides a simplified representation of the bot, suitable
    for listings or quick overviews.
    """
    def __init__(self, entity_cls: Type[BotEntity], dto_cls: Type[MinimalBotDTO]):
        """
        Initializes the mapper with the specific entity and DTO classes.
        """
        self.entity_cls = entity_cls
        self.dto_cls = dto_cls
        logger.debug(f"MinimalBotDTOMapper initialized for {entity_cls.__name__} and {dto_cls.__name__}")

    def to_dto(self, entity: BotEntity) -> Optional[MinimalBotDTO]:
        """
        Maps a BotEntity domain object to a MinimalBotDTO.
        Handles potential None values for string fields by providing an empty string.
        """
        if not entity:
            logger.debug("MinimalBotDTOMapper.to_dto received None entity, returning None.")
            return None

        try:
            # Ensure 'name' and 'status' are non-None strings for the DTO
            bot_name = entity.name if entity.name is not None else ""
            bot_status = entity.status if entity.status is not None else ""

            minimal_dto = self.dto_cls(
                uid=entity.uid,
                user_uid=entity.user_uid,
                name=bot_name,
                status=bot_status,
                # Explicitly add created_at and updated_at, as they are part of BaseEntity
                created_at=entity.created_at,
                updated_at=entity.updated_at,
            )
            logger.debug(f"Mapped BotEntity {entity.uid} to MinimalBotDTO.")
            return minimal_dto
        except Exception as e:
            logger.error(f"Error mapping BotEntity {getattr(entity, 'uid', 'N/A')} to MinimalBotDTO: {e}", exc_info=True)
            # Re-raise to signal a critical mapping failure
            raise RuntimeError(f"Failed to map minimal bot entity {getattr(entity, 'uid', 'N/A')} to DTO.") from e