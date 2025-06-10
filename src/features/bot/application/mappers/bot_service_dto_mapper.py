from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from typing import Type

from src.features.bot.api.v1.dtos.bot_service_dto import BotServiceDTO
from src.features.bot.domain.entities.bot_service_entity import BotServiceEntity



class BotServiceDTOMapper:
    """
    Mapper for converting BotServiceEntity domain objects to BotServiceDTO data transfer objects.
    This class is designed as a regular Python class to encapsulate mapping logic.
    """
    def __init__(self, entity_cls: Type[BotServiceEntity], dto_cls: Type[BotServiceDTO]):
        """
        Initializes the mapper with the specific entity and DTO classes.
        """
        self.entity_cls = entity_cls
        self.dto_cls = dto_cls
        logger.debug(f"BotServiceDTOMapper initialized for {entity_cls.__name__} and {dto_cls.__name__}")

    def to_dto(self, entity: BotServiceEntity) -> BotServiceDTO:
        """
        Maps a BotServiceEntity domain object to a BotServiceDTO.
        Ensures all relevant entity fields, including inherited timestamps, are mapped.
        """
        if not entity:
            logger.warning("Attempted to map a None BotServiceEntity to DTO.")
            raise ValueError("Entity cannot be None for mapping to DTO.")

        try:
            # Map all fields from the BotServiceEntity to the BotServiceDTO.
            # This includes uid, created_at, and updated_at inherited from BaseEntity.
            service_dto = self.dto_cls(
                service_uid=entity.uid,  # The unique ID of the BotServiceEntity record
                bot_uid=entity.bot_uid,
                platform=entity.platform,
                status=entity.status,
                linked_account_uid=entity.linked_account_uid,
                created_at=entity.created_at,  # Include created_at from the entity
                updated_at=entity.updated_at   # Include updated_at from the entity
            )
            logger.debug(f"Mapped BotServiceEntity {entity.uid} to BotServiceDTO.")
            return service_dto
        except Exception as e:
            logger.error(f"Error mapping BotServiceEntity {getattr(entity, 'uid', 'N/A')} to DTO: {e}", exc_info=True)
            raise RuntimeError(f"Failed to map service entity {getattr(entity, 'uid', 'N/A')} to DTO.") from e