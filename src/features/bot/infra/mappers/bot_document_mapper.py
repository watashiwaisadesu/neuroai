# src/features/bot/infra/mappers/bot_document_mapper.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from typing import Optional, Type

# Assuming BotDocumentEntity now also inherits from BaseEntity (a dataclass)
from src.features.bot.domain.entities.bot_document_entity import BotDocumentEntity
from src.features.bot.infra.persistence.models.bot_document import BotDocumentORM




class BotDocumentMapper:
    """
    Handles mapping between BotDocumentEntity and BotDocumentORM.
    This class is not a dataclass as it encapsulates mapping logic.
    """
    entity_cls: Type[BotDocumentEntity]
    orm_cls: Type[BotDocumentORM]

    def __init__(self, entity_cls: Type[BotDocumentEntity], orm_cls: Type[BotDocumentORM]):
        self.entity_cls = entity_cls
        self.orm_cls = orm_cls

    def to_entity(self, orm_obj: BotDocumentORM) -> Optional[BotDocumentEntity]:
        """Converts an ORM object to a domain entity."""
        if not orm_obj:
            logger.debug("Received None ORM object, returning None entity.")
            return None

        # When converting ORM to Entity, we pass all known attributes.
        # Since BaseEntity (inherited by BotDocumentEntity) handles default timestamps,
        # we can just pass them if they exist on the ORM.
        return self.entity_cls(
            uid=orm_obj.uid,
            # created_at and updated_at are now fields in BaseEntity,
            # which BotDocumentEntity inherits. We pass them from the ORM.
            created_at=orm_obj.created_at,
            updated_at=orm_obj.updated_at,
            bot_uid=orm_obj.bot_uid,
            filename=orm_obj.filename,
            content_type=orm_obj.content_type,
            file_data=orm_obj.file_data
            # storage_path=orm_obj.storage_path, # Uncomment if used
            # file_size=orm_obj.file_size        # Uncomment if used
        )

    def from_entity(self, entity: BotDocumentEntity) -> Optional[BotDocumentORM]:
        """Converts a domain entity to an ORM object."""
        if not entity:
            logger.debug("Received None entity, returning None ORM object.")
            return None

        data = {
            "uid": entity.uid,
            "bot_uid": entity.bot_uid,
            "filename": entity.filename,
            "content_type": entity.content_type,
            "file_data": entity.file_data,
            # "storage_path": entity.storage_path, # Uncomment if used
            # "file_size": entity.file_size,        # Uncomment if used
            # Explicitly pass created_at and updated_at as they are part of the entity
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

        # The uid might be None if the entity is brand new and the DB generates it.
        # However, BaseEntity's default_factory ensures UID is always present.
        # So, this pop logic is generally not needed if BaseEntity is used as intended.
        # If your ORM layer specifically requires `uid` to be omitted for new records
        # where the DB auto-generates it, you'd handle that in the repository or ORM session.
        # For a truly new entity (not yet persisted), entity.uid would already be a UUID.
        # The ORM typically handles `created_at` and `updated_at` defaults,
        # but passing them from the entity is fine for consistency,
        # especially during updates.

        return self.orm_cls(**data)