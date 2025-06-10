from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
import uuid
from dataclasses import dataclass

from src.core.base.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
from src.features.bot.application.services.user_lookup_service import UserLookupService
from src.features.identity.exceptions.user_exceptions import UserNotFoundError
from src.features.support.api.v1.dtos.support_dtos import SupportInitiatedResponseDTO
from src.features.support.application.commands.create_support.create_support_command import \
    CreateSupportCommand
from src.features.support.domain.events.support_requested_event import SupportRequestedEvent




@dataclass
class CreateSupportCommandHandler(BaseCommandHandler[CreateSupportCommand, SupportInitiatedResponseDTO]): # Renamed class (if it was CreateSupportRequestCommandHandler)
    _user_lookup_service: UserLookupService
    _mediator: Mediator

    async def __call__(self, command: CreateSupportCommand) -> SupportInitiatedResponseDTO:
        # 1. Verify user exists
        user = await self._user_lookup_service.get_user_by_uid(str(command.user_uid))
        if not user:
            raise UserNotFoundError(f"User with UID {command.user_uid} not found")
        item_email = command.email or user.email # Renamed variable

        # 2. Generate a unique ID for tracking
        uid = uuid.uuid4() # Renamed variable

        # 3. Publish an event to handle file uploads and subsequent creation
        support_request_event = SupportRequestedEvent(
            uid=uid,
            user_uid=command.user_uid,
            email=item_email,
            subject=command.subject,
            message=command.message,
            category=command.category,
            attachments=command.attachments or [],  # Ensure it's a list, even if None
        )
        await self._mediator.publish([support_request_event])

        logger.info(f"Support item submission initiated for user {command.user_uid}, item_id: {uid}") # Updated log message

        # 4. Return an immediate response DTO
        return SupportInitiatedResponseDTO(
            request_id=uid, # DTO field name remains request_id for API consistency if external
            message="Your support item has been received and is being processed.", # Updated message
            status="processing"
        )