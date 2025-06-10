from src.features.announcement.domain.entities.announcement_entity import AnnouncementEntity
from src.features.announcement.infra.persistence.models.announcement_orm import AnnouncementORM


class AnnouncementMapper:
    """
    Handles mapping between AnnouncementEntity and AnnouncementORM.
    """
    @staticmethod
    def to_entity(orm_announcement: AnnouncementORM) -> AnnouncementEntity:
        """Converts an ORM object to a domain entity."""
        return AnnouncementEntity(
            uid=orm_announcement.uid,
            title=orm_announcement.title,
            version=orm_announcement.version,
            text=orm_announcement.text,
            type=orm_announcement.type,
            created_at=orm_announcement.created_at,
            updated_at=orm_announcement.updated_at
        )

    @staticmethod
    def from_entity(entity: AnnouncementEntity) -> AnnouncementORM:
        """Converts a domain entity to an ORM object."""
        return AnnouncementORM(
            uid=entity.uid,
            title=entity.title,
            version=entity.version,
            text=entity.text,
            type=entity.type,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )