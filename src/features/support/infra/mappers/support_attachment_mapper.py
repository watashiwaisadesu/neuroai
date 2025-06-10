# src/features/support/infra/mappers/support_mapper.py

# Aliasing enums for consistency with domain entities

from src.features.support.domain.entities.support_attachment_entity import SupportAttachmentEntity
from src.features.support.infra.persistence.models.support_attachment_orm import SupportAttachmentORM



class SupportAttachmentMapper:
    def to_entity(self, orm_obj: SupportAttachmentORM) -> SupportAttachmentEntity:
        # When mapping from ORM to entity, use direct instantiation
        # as the entity already has a UID and timestamps from the database.
        return SupportAttachmentEntity(
            uid=orm_obj.uid, # Pass the existing UID
            support_uid=orm_obj.support_uid,
            file_url=orm_obj.file_url,
            file_name=orm_obj.file_name,
            content_type=orm_obj.content_type,
            size_bytes=orm_obj.size_bytes,
            created_at=orm_obj.created_at, # Pass existing created_at
            updated_at=orm_obj.updated_at, # Pass existing updated_at
        )

    def from_entity(self, entity: SupportAttachmentEntity) -> SupportAttachmentORM:
        return SupportAttachmentORM(
            uid=entity.uid,
            support_uid=entity.support_uid,
            file_url=entity.file_url,
            file_name=entity.file_name,
            content_type=entity.content_type,
            size_bytes=entity.size_bytes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )