# src/features/notification/application/event_handlers/send_email_change_confirmation_handler.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass

from src.core.base.event import BaseEventHandler
from src.features.identity.domain.events.email_change_events import EmailChangeRequestedEvent
from src.features.notification.domain.services.email_sender import EmailSender




@dataclass(kw_only=True)
class SendEmailChangeConfirmationEventHandler(BaseEventHandler[EmailChangeRequestedEvent, None]):
    """Handler for email change requested events - sends the confirmation email"""
    email_sender: EmailSender

    async def handle(self, event: EmailChangeRequestedEvent) -> None:
        """
        Handle email change requested event by sending confirmation email
        """
        try:
            logger.info(f"Processing EmailChangeRequestedEvent for user {event.user_uid} to email: {event.new_email}")

            # Send email change confirmation email using your email sender
            await self.email_sender.send_change_email_email(
                to=event.new_email,
                token=event.confirmation_token
            )

            logger.info(f"Email change confirmation sent successfully to: {event.new_email}")

        except Exception as e:
            logger.error(f"Failed to send email change confirmation to {event.new_email}: {e}", exc_info=True)
            # Don't re-raise - we don't want the command to fail if email fails
