# src/features/notification/infra/providers/smtp_email_sender.py
from src.features.notification.domain.services.email_sender import EmailSender
from pydantic import EmailStr
from src.infra.services.email.send_verification_email_task import send_email  # Celery task
from src.core.utils.hashing import create_url_safe_token
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger




class SmtpEmailSender(EmailSender):
    def __init__(self, frontend_url: str):
        self.frontend_url = frontend_url
        logger.info(f"SmtpEmailSender initialized with frontend_url: {self.frontend_url}")

    async def send_verification_email(self, to: EmailStr, token: str = None) -> None:
        # Generate token if not provided
        if not token:
            token = create_url_safe_token({"email": to})

        link = f"{self.frontend_url}/verify-account/{token}"
        html = f"""
        <h1>Verify your Email</h1>
        <p>Please click this <a href="{link}">link</a> to verify your email</p>
        """
        logger.info(f"Preparing to send verification email to: {to}")
        send_email.delay([to], "Verify Your Email", html)
        logger.debug(f"Verification email task initiated for: {to}")

    async def send_reset_password_email(self, to: EmailStr, token: str) -> None:
        link = f"{self.frontend_url}/reset-password/{token}"
        html = f"<h1>Reset Password</h1><p><a href='{link}'>Reset here</a></p>"
        logger.info(f"Preparing to send password reset email to: {to}")
        send_email.delay([to], "Reset Your Password", html)

    async def send_change_email_email(self, to: EmailStr, token: str) -> None:
        link = f"{self.frontend_url}/verify-email/{token}"
        html = f"""
        <h1>Confirm Email Change</h1>
        <p>Click the link to confirm your new email address:</p>
        <a href="{link}">Confirm Email Change</a>
        <p>If you didn't request this, you can ignore the message.</p>
        """
        logger.info(f"Preparing to send email change confirmation to: {to}")
        send_email.delay([to], "Confirm Your Email Change", html)
