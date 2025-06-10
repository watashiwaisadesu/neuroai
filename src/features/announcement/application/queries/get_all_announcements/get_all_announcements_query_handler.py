from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass
from typing import List

from src.core.mediator.mediator import Mediator
from src.core.mediator.query import BaseQueryHandler
# Corrected import path for DTOs
from src.features.announcement.api.v1.dtos.announcements_response_dto import AnnouncementDTO, GetAnnouncementsResponseDTO
from src.features.announcement.application.queries.get_all_announcements.get_all_announcements_query import \
    GetAllAnnouncementsQuery
# Corrected import path for mapper
from src.features.announcement.application.mappers.announcement_dto_mapper import AnnouncementDTOMapper
from src.features.announcement.domain.uow.announcement_unit_of_work import AnnouncementUnitOfWork




@dataclass
class GetAllAnnouncementsQueryHandler(BaseQueryHandler[GetAllAnnouncementsQuery, GetAnnouncementsResponseDTO]):
    _unit_of_work: AnnouncementUnitOfWork
    _mediator: Mediator
    _mapper: AnnouncementDTOMapper = AnnouncementDTOMapper()  # Instantiate the mapper

    async def __call__(self, query: GetAllAnnouncementsQuery) -> GetAnnouncementsResponseDTO:
        """
        Handles the GetAllAnnouncementsQuery by retrieving all announcements
        and mapping them to DTOs, then wrapping them in a GetAnnouncementsResponseDTO.
        """
        logger.info("Handling GetAllAnnouncementsQuery: retrieving all announcements.")

        announcement_dtos: List[AnnouncementDTO] = []
        async with self._unit_of_work:
            announcements = await self._unit_of_work.announcement_repository.get_all()
            logger.debug(f"Found {len(announcements)} announcement entities.")

            for announcement in announcements:
                try:
                    dto = self._mapper.to_dto(announcement)
                    announcement_dtos.append(dto)
                except Exception as e:
                    logger.error(f"Failed to map announcement {announcement.uid} to DTO: {e}", exc_info=True)
                    # It's generally better to let mapping errors propagate unless you have a specific strategy
                    # for partial success. For now, re-raising to ensure failure is clear.
                    raise

        logger.info(f"Successfully retrieved and mapped {len(announcement_dtos)} announcement DTOs.")

        # FIX: Wrap the list of DTOs in the GetAnnouncementsResponseDTO
        return GetAnnouncementsResponseDTO(
            message=f"Successfully retrieved {len(announcement_dtos)} announcements.",
            announcements=announcement_dtos
        )