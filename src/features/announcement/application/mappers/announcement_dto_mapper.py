# src/features/announcements/api/mappers/announcement_response_dto_mapper.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger

from src.features.announcement.api.v1.dtos.announcements_response_dto import \
    AnnouncementDTO  # Assuming this DTO can serve as the response
from src.features.announcement.domain.entities.announcement_entity import AnnouncementEntity


class AnnouncementDTOMapper:
    """
    Mapper for converting AnnouncementEntity domain objects to AnnouncementResponseDTOs.
    """
    @staticmethod
    def to_dto(entity: AnnouncementEntity) -> AnnouncementDTO:
        """
        Maps an AnnouncementEntity domain object to an AnnouncementResponseDTO.
        """
        if not entity:
            logger.warning("Attempted to map a None AnnouncementEntity to DTO.")
            raise ValueError("Entity cannot be None for mapping.")

        try:
            # Assuming AnnouncementResponseDTO has a constructor that accepts these fields,
            # or a @classmethod like from_entity as used in create_announcement_command_handler.
            return AnnouncementDTO.from_entity(entity)
        except Exception as e:
            logger.error(f"Error mapping AnnouncementEntity {getattr(entity, 'uid', 'N/A')} to DTO: {e}", exc_info=True)
            raise RuntimeError(f"Failed to map announcement entity {getattr(entity, 'uid', 'N/A')} to DTO.") from e