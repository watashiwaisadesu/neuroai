from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from src.config import Settings
from pathlib import Path


__SETTINGS: Settings = Settings()


mail_config = ConnectionConfig(
    MAIL_USERNAME=__SETTINGS.MAIL_USERNAME,
    MAIL_PASSWORD=__SETTINGS.MAIL_PASSWORD,
    MAIL_FROM=__SETTINGS.MAIL_FROM,
    MAIL_PORT=587,
    MAIL_SERVER=__SETTINGS.MAIL_SERVER,
    MAIL_FROM_NAME=__SETTINGS.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


mail = FastMail(config=mail_config)


def create_message(recipients: list[str], subject: str, body: str):

    message = MessageSchema(
        recipients=recipients, subject=subject, body=body, subtype=MessageType.html
    )

    return message