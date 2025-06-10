# src/features/announcements/application/commands/create_announcement/create_announcement_command_handler.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass

# Adjust imports based on your project structure
from src.core.mediator.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
from src.features.announcement.api.v1.dtos.announcements_response_dto import AnnouncementResponseDTO
from src.features.announcement.application.commands.create_announcement.create_announcement_command import CreateAnnouncementCommand
from src.features.announcement.application.mappers.announcement_dto_mapper import AnnouncementDTOMapper
from src.features.announcement.domain.entities.announcement_entity import AnnouncementEntity
from src.features.announcement.domain.uow.announcement_unit_of_work import AnnouncementUnitOfWork




@dataclass
class CreateAnnouncementCommandHandler(BaseCommandHandler[CreateAnnouncementCommand, AnnouncementResponseDTO]):
    _unit_of_work: AnnouncementUnitOfWork
    _mediator: Mediator
    _mapper: AnnouncementDTOMapper = AnnouncementDTOMapper()  # Instantiate the mapper

    async def __call__(self, command: CreateAnnouncementCommand) -> AnnouncementResponseDTO:
        """
        Handles the creation of a new announcement.
        """
        logger.info(f"Attempting to create announcement: title='{command.title}', version='{command.version}'")

        # Create the domain entity with the provided data
        new_announcement_entity = AnnouncementEntity(
            title=command.title,
            version=command.version,
            text=command.text,
            type=command.type,
        )

        async with self._unit_of_work:
            # Persist the entity via the repository
            created_entity = await self._unit_of_work.announcement_repository.create(new_announcement_entity)
            logger.info(f"Announcement {created_entity.uid} created and persisted.")

            # If it's published immediately, or you want to track any creation:
            # Publish a domain event for EDA
            # event = AnnouncementCreatedEvent(
            #     uid=created_entity.uid,
            #     title=created_entity.title,
            #     version=created_entity.version,
            #     text=created_entity.text,
            #     type=created_entity.type,
            # )
            # await self._mediator.publish([event])
            logger.info(f"AnnouncementCreatedEvent published for announcement {created_entity.uid}.")

        dto = self._mapper.to_dto(created_entity)

        announcement_dto_instance = self._mapper.to_dto(created_entity)

        # Return the final AnnouncementResponseDTO, wrapping the mapped AnnouncementDTO
        return AnnouncementResponseDTO(
            message="Successfully created announcement",
            announcement=announcement_dto_instance  # <--- Pass the actual AnnouncementDTO instance
        )