# src/features/identity/application/commands/profile/update_avatar/update_avatar_command_handler.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
import uuid
from dataclasses import dataclass

from src.core.base.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
from src.features.identity.api.v1.dtos.profile.update_avatar_dto import AvatarUploadResponseDTO
from src.features.identity.application.commands.profile.update_avatar.update_avatar_command import UpdateAvatarCommand
from src.features.identity.domain.events.user_avatar_events import UserAvatarUploadRequestedEvent
from src.features.identity.domain.repositories.user_unit_of_work import UserUnitOfWork
from src.features.identity.exceptions.user_exceptions import UserNotFoundError




@dataclass
class UpdateAvatarCommandHandler(BaseCommandHandler[UpdateAvatarCommand, AvatarUploadResponseDTO]):
    _unit_of_work: UserUnitOfWork
    _mediator: Mediator

    async def __call__(self, command: UpdateAvatarCommand) -> AvatarUploadResponseDTO:
        async with self._unit_of_work as uow:
            # Fetch the user
            user = await uow.user_repository.find_by_uid(command.user_uid)
            if not user:
                raise UserNotFoundError(f"User with UID {command.user_uid} not found")

            # Generate unique request ID for tracking
            request_id = str(uuid.uuid4())

            # Publish event that avatar upload is requested
            upload_requested_event = UserAvatarUploadRequestedEvent(
                user_uid=user.uid,
                email=user.email,
                file_name=command.filename,
                content_type=command.content_type,
                avatar_file_data=command.avatar_file_data,
                request_id=request_id
            )

            await self._mediator.publish([upload_requested_event])

            logger.info(f"Avatar upload requested for user {user.uid}, request_id: {request_id}")

        # Return simple response with just the request info
        return AvatarUploadResponseDTO(
            message="Avatar upload initiated successfully",
            request_id=request_id,
            status="processing"
        )