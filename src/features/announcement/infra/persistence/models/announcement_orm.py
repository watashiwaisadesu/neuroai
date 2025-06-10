# src/features/announcements/infra/persistence/repositories/sqlalchemy_announcement_repository.py

from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped

from src.features.announcement.domain.entities.announcement_entity import (
    AnnouncementType  # Ensure AnnouncementType is accessible and correctly defined (e.g., an Enum)
)
# Assuming 'Base' is imported from your core SQLAlchemy setup
from src.infra.persistence.models.sqlalchemy_base import SQLAlchemyBase


class AnnouncementORM(SQLAlchemyBase):
    """
    SQLAlchemy ORM model for the Announcement entity using mapped_column.
    Maps the AnnouncementEntity to the 'announcements' table in the database.
    """
    __tablename__ = "announcements"

    # Fields matching AnnouncementEntity, using mapped_column
    # Mapped[str] implies nullable=False by default for non-Optional types
    title: Mapped[str] = mapped_column(String, nullable=False)
    # Store enum as string. Use default=AnnouncementType.INFORMATION.value to store the string value.
    type: Mapped[str] = mapped_column(String, nullable=False, default=AnnouncementType.INFORMATION)
    version: Mapped[str] = mapped_column(String, nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)


    def __repr__(self):
        return (
            f"<AnnouncementORM(uid={self.uid}, title='{self.title}', "
            f"type='{self.type}', version='{self.version}')>"
        )