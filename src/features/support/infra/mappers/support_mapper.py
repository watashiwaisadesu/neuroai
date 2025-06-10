# src/features/support/infra/mappers/support_attachment_mapper.py

import uuid
from typing import List

from src.features.support.domain.entities.support_entity import SupportEntity
from src.features.support.domain.entities.support_attachment_entity import SupportAttachmentEntity
from src.features.support.domain.value_objects.support_enums import SupportStatus, SupportPriority, \
    SupportCategory
from src.features.support.infra.mappers.support_attachment_mapper import SupportAttachmentMapper
from src.features.support.infra.persistence.models.support_orm import SupportORM
from src.features.support.infra.persistence.models.support_attachment_orm import SupportAttachmentORM

# Aliasing enums for consistency with domain entities


class SupportMapper:
    def __init__(self):
        self._attachment_mapper = SupportAttachmentMapper()

    def to_entity(self, orm_obj: SupportORM) -> SupportEntity:
        attachments_entities = [self._attachment_mapper.to_entity(att_orm) for att_orm in orm_obj.attachments]
        # When mapping from ORM to entity, use direct instantiation for SupportEntity too
        return SupportEntity(
            uid=orm_obj.uid,
            user_uid=orm_obj.user_uid,
            email=orm_obj.email,
            message=orm_obj.message,
            subject=orm_obj.subject,
            attachments=attachments_entities,
            status=SupportStatus(orm_obj.status),
            priority=SupportPriority(orm_obj.priority),
            category=SupportCategory(orm_obj.category) if orm_obj.category else None,
            created_at=orm_obj.created_at,
            updated_at=orm_obj.updated_at,
        )

    def from_entity(self, entity: SupportEntity) -> SupportORM:
        attachments_orms = [self._attachment_mapper.from_entity(att_entity) for att_entity in entity.attachments]
        return SupportORM(
            uid=entity.uid,
            user_uid=entity.user_uid,
            email=entity.email,
            message=entity.message,
            subject=entity.subject,
            attachments=attachments_orms,
            status=entity.status.value,
            priority=entity.priority.value,
            category=entity.category.value if entity.category else None,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
