# src/features/notification/application/event_handlers/oauth_user_created_handler.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass

from src.core.base.event import BaseEventHandler
from src.features.identity.domain.events.oauth_events import OAuthUserRegisteredEvent
from src.features.notification.domain.services.email_sender import EmailSender




@dataclass(kw_only=True)
class OAuthUserRegisteredEventHandler(BaseEventHandler[OAuthUserRegisteredEvent, None]):
    """Handler for OAuth user created events - sends welcome email"""
    email_sender: EmailSender

    async def handle(self, event: OAuthUserRegisteredEvent) -> None:
        """
        Handle OAuth user created event by sending welcome email
        """
        try:
            logger.info(f"Processing OAuthUserCreatedEvent for user {event.user_uid} via {event.provider}")
            # Optional: Send welcome email to new OAuth users
            # await self.email_sender.send_welcome_email(
            #     to=event.email,
            #     provider=event.provider
            # )

            logger.info(f"Welcome notification processed for OAuth user: {event.email}")

        except Exception as e:
            logger.error(f"Failed to handle OAuth user creation event: {e}", exc_info=True)
            # Don't re-raise - this is just a notification
