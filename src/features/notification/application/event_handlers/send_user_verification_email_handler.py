from dataclasses import dataclass
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from src.core.base.event import BaseEventHandler
from src.features.identity.domain.events.user_registered_events import UserRegisteredEvent
from src.features.notification.domain.services.email_sender import EmailSender




@dataclass(kw_only=True)
class SendUserVerificationEmailEventHandler(BaseEventHandler[UserRegisteredEvent, None]):
    email_sender: EmailSender

    async def handle(self, event: UserRegisteredEvent) -> None:
        logger.info(f"Handling user registration event for email: {event.email}")
        try:
            await self.email_sender.send_verification_email(event.email)
            logger.info(f"Verification email sent successfully to {event.email}")
        except Exception as e:
            logger.error(f"Failed to send verification email to {event.email}: {e}", exc_info=True)