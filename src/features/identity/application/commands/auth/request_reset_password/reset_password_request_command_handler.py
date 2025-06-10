# src/features/identity/application/commands/auth/reset_password_request/reset_password_request_command_handler.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass

from src.core.base.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
from src.core.utils.hashing import create_url_safe_token
from src.features.identity.api.v1.dtos.auth.reset_password_request_dto import RequestResetPasswordRequestDTO, \
    RequestResetPasswordResponseDTO
from src.features.identity.application.commands.auth.request_reset_password.reset_password_request_command import \
    RequestResetPasswordCommand
from src.features.identity.domain.events.password_reset_request_events import PasswordResetRequestedEvent




@dataclass
class RequestResetPasswordCommandHandler(
    BaseCommandHandler[RequestResetPasswordCommand, RequestResetPasswordResponseDTO]):
    _mediator: Mediator

    async def __call__(self, command: RequestResetPasswordCommand) -> RequestResetPasswordResponseDTO:
        """
        Handle password reset request by generating token and publishing event
        """
        logger.info(f"Password reset requested for email: {command.email}")

        # Generate reset token - same logic as your original
        token = create_url_safe_token({"email": command.email})

        # Create and publish domain event
        reset_event = PasswordResetRequestedEvent(
            email=command.email,
            reset_token=token
        )

        # Publish event - notification service will handle the email sending
        await self._mediator.publish([reset_event])

        logger.info(f"PasswordResetRequestedEvent published for email: {command.email}")

        # Return same response as original
        return RequestResetPasswordResponseDTO(
            message="Please check your email for instructions"
        )