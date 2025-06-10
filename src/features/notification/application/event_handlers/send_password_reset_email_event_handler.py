# src/features/identity/application/event_handlers/password_reset_event_handler.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass

from src.core.base.event import BaseEventHandler
from src.features.identity.domain.events.password_reset_request_events import PasswordResetRequestedEvent
from src.features.notification.domain.services.email_sender import EmailSender




@dataclass(kw_only=True)
class SendPasswordResetEmailEventHandler(BaseEventHandler[PasswordResetRequestedEvent, None]):
    """Handler for password reset requested events - sends the actual email"""
    email_sender: EmailSender

    async def handle(self, event: PasswordResetRequestedEvent) -> None:
        """
        Handle password reset requested event by sending reset email
        """
        try:
            logger.info(f"Processing PasswordResetRequestedEvent for email: {event.email}")

            # Send password reset email - same logic as your original
            await self.email_sender.send_reset_password_email(
                to=event.email,
                token=event.reset_token
            )

            logger.info(f"Password reset email sent successfully to: {event.email}")

        except Exception as e:
            logger.error(f"Failed to send password reset email to {event.email}: {e}", exc_info=True)
            # Don't re-raise - we don't want the command to fail if email fails
            # The user will get the success message regardless