# src/features/notification/application/event_handlers/oauth_login_successful_handler.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass

from src.core.base.event import BaseEventHandler
from src.features.identity.domain.events.oauth_events import OAuthLoginSuccessfulEvent
from src.features.notification.domain.services.email_sender import EmailSender




@dataclass(kw_only=True)
class OAuthLoginSuccessfulEventHandler(BaseEventHandler[OAuthLoginSuccessfulEvent, None]):
    """Handler for OAuth login successful events - logs and optionally notifies"""
    email_sender: EmailSender

    async def handle(self, event: OAuthLoginSuccessfulEvent) -> None:
        """
        Handle OAuth login successful event
        """
        try:
            logger.info(f"Processing OAuthLoginSuccessfulEvent for user {event.user_uid} via {event.provider} (new_user: {event.is_new_user})")
            # Optional: Send login notification email for security
            # if not event.is_new_user:
            #     await self.email_sender.send_login_notification(
            #         to=event.email,
            #         provider=event.provider
            #     )

            logger.info(f"OAuth login event processed for user: {event.email}")

        except Exception as e:
            logger.error(f"Failed to handle OAuth login successful event: {e}", exc_info=True)
            # Don't re-raise - this is just a notification