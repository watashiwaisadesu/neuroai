from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from typing import Optional, Type

from src.features.bot.domain.entities.bot_service_entity import BotServiceEntity
from src.features.bot.infra.persistence.models.bot_service import BotServiceORM




class BotServiceMapper:
    """
    Handles mapping between BotServiceEntity domain objects and BotServiceORM persistence objects.
    This class is designed as a regular class, emphasizing its behavioral role in mapping data.
    """

    entity_cls: Type[BotServiceEntity]
    orm_cls: Type[BotServiceORM]

    def __init__(self, entity_cls: Type[BotServiceEntity], orm_cls: Type[BotServiceORM]):
        self.entity_cls = entity_cls
        self.orm_cls = orm_cls
        logger.debug(f"BotServiceMapper initialized for {entity_cls.__name__} and {orm_cls.__name__}")

    def to_entity(self, orm_obj: BotServiceORM) -> Optional[BotServiceEntity]:
        """
        Maps a BotServiceORM object from the persistence layer to a BotServiceEntity domain object.
        Ensures all fields, including inherited BaseEntity timestamps, are correctly passed.
        """
        if not orm_obj:
            logger.debug("Received None BotServiceORM object, returning None entity.")
            return None
        try:
            # Pass all fields directly from the ORM object to the entity's dataclass constructor,
            # including uid, created_at, and updated_at from BaseEntity.
            entity = self.entity_cls(
                uid=orm_obj.uid,
                bot_uid=orm_obj.bot_uid,
                platform=orm_obj.platform,
                status=orm_obj.status,
                linked_account_uid=orm_obj.linked_account_uid,
                service_details=orm_obj.service_details,
                created_at=orm_obj.created_at,  # Explicitly pass created_at from ORM
                updated_at=orm_obj.updated_at   # Explicitly pass updated_at from ORM
            )
            return entity
        except Exception as e:
            logger.error(f"Error mapping BotServiceORM to Entity (UID: {getattr(orm_obj, 'uid', 'N/A')}): {e}", exc_info=True)
            raise # Re-raise the exception to indicate a mapping failure.

    def from_entity(self, entity: BotServiceEntity) -> Optional[BotServiceORM]:
        """
        Maps a BotServiceEntity domain object to a BotServiceORM object for persistence.
        Includes all relevant fields for ORM creation/update.
        """
        if not entity:
            logger.debug("Received None BotServiceEntity, returning None ORM object.")
            return None
        try:
            # Prepare data for the ORM constructor, including all fields from the entity.
            # BaseEntity's dataclass will ensure uid, created_at, updated_at are always present on the entity.
            orm_data = {
                "uid": entity.uid,
                "bot_uid": entity.bot_uid,
                "platform": entity.platform,
                "status": entity.status,
                "linked_account_uid": entity.linked_account_uid,
                "service_details": entity.service_details,
                "created_at": entity.created_at,  # Explicitly pass created_at from entity
                "updated_at": entity.updated_at,  # Explicitly pass updated_at from entity
            }

            # The check `if entity.uid is None and "uid" in orm_data:` is generally
            # no longer needed if BaseEntity automatically assigns a UUID on creation.
            # Your ORM layer will handle whether to use the provided UID for inserts/updates.

            return self.orm_cls(**orm_data)
        except Exception as e:
            logger.error(f"Error mapping BotServiceEntity to ORM (UID: {getattr(entity, 'uid', 'N/A')}): {e}", exc_info=True)
            raise # Re-raise the exception to indicate a mapping failure.