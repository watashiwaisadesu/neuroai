# src/features/identity/application/commands/auth/change_email/change_email_command_handler.py
import json
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass

from src.core.base.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
from src.core.utils.hashing import create_url_safe_token
from src.features.identity.api.v1.dtos.auth.change_email_dto import RequestChangeEmailResponseDTO
from src.features.identity.application.commands.auth.request_change_email.change_email_command import RequestChangeEmailCommand
from src.features.identity.domain.repositories.user_unit_of_work import UserUnitOfWork
from src.features.identity.domain.events.email_change_events import EmailChangeRequestedEvent
from src.features.identity.exceptions.auth_exceptions import EmailAlreadyInUseError
from src.infra.services.redis.redis_service import RedisService




@dataclass
class RequestChangeEmailCommandHandler(BaseCommandHandler[RequestChangeEmailCommand, RequestChangeEmailResponseDTO]):
    _unit_of_work: UserUnitOfWork
    _redis_service: RedisService
    _mediator: Mediator

    async def __call__(self, command: RequestChangeEmailCommand) -> RequestChangeEmailResponseDTO:
        """
        Handle email change request - EXACT same logic as your original implementation
        """
        logger.info(f"Processing email change request for user {command.user_uid} to {command.new_email}")

        # 🔍 Check if new email already exists - same logic as original
        existing_user = await self._unit_of_work.user_repository.find_by_email(command.new_email)
        if existing_user:
            logger.warning(f"Email change request failed: {command.new_email} already in use")
            raise EmailAlreadyInUseError()

        # Create payload - same logic as original
        payload = {
            "user_uid": str(command.user_uid),
            "new_email": command.new_email
        }

        # Generate token - same logic as original
        token = create_url_safe_token(payload)

        # Store in Redis - same logic as original
        await self._redis_service.set_key(
            f"pending_email_update:{token}",
            json.dumps(payload),
            expire=3600
        )

        logger.info(f"Stored pending email change in Redis for user {command.user_uid}")

        # Create and publish domain event for email notification
        email_change_event = EmailChangeRequestedEvent(
            user_uid=command.user_uid,
            new_email=command.new_email,
            confirmation_token=token
        )

        # Publish event - notification service will handle the email sending
        await self._mediator.publish([email_change_event])

        logger.info(f"EmailChangeRequestedEvent published for user {command.user_uid}")

        # Return same response as original
        return RequestChangeEmailResponseDTO(
            message="Confirmation email sent.",
        )