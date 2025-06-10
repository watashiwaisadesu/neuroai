from src.core.utils.hashing import create_url_safe_token, decode_url_safe_token
from src.features.identity.domain.entities.user_entity import UserEntity, logger

from src.features.identity.application.services.auth_notification_service import AuthNotificationService, UserEmailProvider
from src.infra.services.email.send_verification_email_task import send_email


class AuthNotificationServiceHandler(AuthNotificationService):
    def __init__(self, frontend_url: str):
        self.frontend_url = frontend_url
        logger.info(f"AuthNotificationServiceImpl initialized with frontend_url: {self.frontend_url}")

    async def send_verification_email(self, user_data: UserEmailProvider) -> None:
        # user_data now only needs to provide an 'email' attribute.
        # If UserEntity had other essential fields for token generation or logging,
        # they would need to be in UserEmailProvider and passed via Kafka.
        token = create_url_safe_token({"email": user_data.email})
        link = f"{self.frontend_url}/verify-account/{token}"
        html = f"""
        <h1>Verify your Email</h1>
        <p>Please click this <a href="{link}">link</a> to verify your email</p>
        """
        logger.info(f"Preparing to send verification email to: {user_data.email}")
        send_email.delay([user_data.email], "Verify Your Email", html) # Celery task
        logger.debug(f"Verification email task initiated for: {user_data.email}")

    # ... other methods remain the same
    async def send_password_reset_email(self, email: str, token: str) -> None:
        link = f"{self.frontend_url}/reset-password/{token}"
        html = f"<h1>Reset Password</h1><p><a href='{link}'>link</a></p>"
        send_email.delay([email], "Reset Your Password", html)

    async def send_change_email_email(self, email: str, token: str) -> None:
        link = f"{self.frontend_url}/verify-email/{token}"
        html = f"""
        <h1>Confirm Email Change</h1>
        <p>Click the link to confirm your new email address:</p>
        <a href="{link}">Confirm Email Change</a>
        <p>If you didn't request this, you can ignore the message.</p>
        """
        send_email.delay([email], "Confirm Your Email Change", html)