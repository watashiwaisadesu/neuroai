# 2. Command Handler (src/features/identity/application/commands/profile/update_me/update_me_command_handler.py)
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass, field
from typing import Dict, Any

from src.core.base.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
from src.features.identity.api.v1.dtos.profile.get_me_dto import UserResponseDTO, UserDTO
from src.features.identity.application.commands.profile.update_me.update_me_command import UpdateMeCommand
from src.features.identity.application.mappers.user_dto_mapper import UserDTOMapper
from src.features.identity.domain.entities.user_entity import UserEntity
from src.features.identity.domain.repositories.user_unit_of_work import UserUnitOfWork
from src.features.identity.exceptions.user_exceptions import UserNotFoundError




@dataclass
class UpdateMeCommandHandler(BaseCommandHandler[UpdateMeCommand, UserResponseDTO]):
    _unit_of_work: UserUnitOfWork
    _mediator: Mediator

    _user_dto_mapper: UserDTOMapper = field(init=False, repr=False)

    def __post_init__(self):
        self._user_dto_mapper = UserDTOMapper(UserEntity, UserDTO)

    async def __call__(self, command: UpdateMeCommand) -> UserResponseDTO:
        async with self._unit_of_work as uow:
            # Fetch the current user
            user = await uow.user_repository.find_by_uid(command.user_uid)
            if not user:
                raise UserNotFoundError(f"User with UID {command.user_uid} not found")

            # Store old values for event
            old_values = self._extract_old_values(user, command.update_data)

            # Update the user entity
            user.update_info(**command.update_data)

            # Persist the changes
            updated_user = await uow.user_repository.update(user)

            # Create and publish event
            # profile_updated_event = UserProfileUpdatedEvent(
            #     user_uid=user.uid,
            #     email=user.email,
            #     updated_fields=list(command.update_data.keys()),
            #     old_values=old_values,
            #     new_values=command.update_data
            # )
            #
            # await self._mediator.publish([profile_updated_event])

            logger.info(f"User {user.uid} profile updated. Fields: {list(command.update_data.keys())}")

        # Map to DTO and return
        user_dto = self._user_dto_mapper.to_dto(updated_user)
        return UserResponseDTO(
            message="User updated successfully",
            user=UserDTO(**user_dto.model_dump())
        )

    def _extract_old_values(self, user: UserEntity, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract current values of fields that will be updated"""
        old_values = {}
        for field in update_data.keys():
            if hasattr(user, field):
                old_values[field] = getattr(user, field)
        return old_values