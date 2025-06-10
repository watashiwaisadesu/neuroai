from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from typing import Optional, Type

# Import domain entity and ORM model
from src.features.bot.domain.entities.bot_participant_entity import BotParticipantEntity
from src.features.bot.infra.persistence.models.bot_participant import BotParticipantORM




class BotParticipantMapper:
    """
    Handles mapping between BotParticipantEntity domain objects and BotParticipantORM persistence objects.
    This class is not a dataclass as its primary role is behavioral (mapping logic),
    not data storage.
    """

    entity_cls: Type[BotParticipantEntity]
    orm_cls: Type[BotParticipantORM]

    def __init__(self, entity_cls: Type[BotParticipantEntity], orm_cls: Type[BotParticipantORM]):
        self.entity_cls = entity_cls
        self.orm_cls = orm_cls
        logger.debug(f"BotParticipantMapper initialized for {entity_cls.__name__} and {orm_cls.__name__}")

    def to_entity(self, orm_obj: BotParticipantORM) -> Optional[BotParticipantEntity]:
        """
        Maps a BotParticipantORM object from the persistence layer to a BotParticipantEntity domain object.
        Ensures proper handling of BaseEntity fields like created_at and updated_at.
        """
        if not orm_obj:
            logger.debug("Received None BotParticipantORM object, returning None entity.")
            return None
        try:
            # Map all fields required by the BotParticipantEntity dataclass constructor,
            # including inherited BaseEntity fields.
            entity = self.entity_cls(
                uid=orm_obj.uid,
                bot_uid=orm_obj.bot_uid,
                user_uid=orm_obj.user_uid,
                role=orm_obj.role,
                created_at=orm_obj.created_at,  # Explicitly pass created_at from ORM
                updated_at=orm_obj.updated_at,  # Explicitly pass updated_at from ORM
            )
            return entity
        except Exception as e:
            logger.error(f"Error mapping BotParticipantORM to Entity (UID: {getattr(orm_obj, 'uid', 'N/A')}): {e}", exc_info=True)
            raise

    def from_entity(self, entity: BotParticipantEntity) -> Optional[BotParticipantORM]:
        """
        Maps a BotParticipantEntity domain object to a BotParticipantORM object for persistence.
        Includes all relevant fields for ORM creation.
        """
        if not entity:
            logger.debug("Received None BotParticipantEntity, returning None ORM object.")
            return None
        try:
            # Map all fields to the ORM constructor.
            # This includes the timestamps from the BaseEntity.
            orm_data = {
                "uid": entity.uid,
                "bot_uid": entity.bot_uid,
                "user_uid": entity.user_uid,
                "role": entity.role,
                "created_at": entity.created_at,  # Explicitly pass created_at from entity
                "updated_at": entity.updated_at,  # Explicitly pass updated_at from entity
            }

            orm_instance = self.orm_cls(**orm_data)
            return orm_instance
        except Exception as e:
            logger.error(f"Error mapping BotParticipantEntity to ORM (UID: {getattr(entity, 'uid', 'N/A')}): {e}", exc_info=True)
            raise