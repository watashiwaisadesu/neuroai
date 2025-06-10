from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    ASYNC_DATABASE_URL: str
    SYNC_DATABASE_URL: str
    REDIS_URL: str
    EXTERNAL_LIBRARY_LEVEL_LOG: Optional[str] = "WARNING"
    LOG_LEVEL: str = "INFO"
    # OPENAI_API_KEY: str
    #
    REFRESH_TOKEN_EXPIRY_DAYS: int = 30
    ACCESS_TOKEN_EXPIRY_MINUTES: int = 60
    #
    # DOMAIN: str
    FRONTEND_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    #
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: Optional[str] = "No Reply"
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool
    #
    # AMOCRM_CLIENT_ID: str
    # AMOCRM_CLIENT_SECRET: str
    # AMOCRM_REDIRECT_URL: str
    # AMOCRM_SUBDOMAIN: str
    #
    GOOGLE_CLIENT_ID: str
    GOOGLE_REDIRECT_URI: str
    GOOGLE_CLIENT_SECRET: str

    # ADMIN_EMAIL: str
    # ADMIN_PASSWORD: str
    # ADMIN_COMPANY_NAME: str = "Default Company"
    # ADMIN_FIELD_OF_ACTIVITY: str = "Default Field"
    # ADMIN_BIN: str = "000000000"
    # ADMIN_LEGAL_ADDRESS: str = "Default Address"
    # ADMIN_CONTACT: str = "Default Contact"
    # ADMIN_PHONE_NUMBER: str = "0000000000"
    # ADMIN_REGISTRATION_DATE_STR: Optional[str] = None
    #
    # DEBUG: Optional[bool] = False

    AWS_ACCESS_KEY: str
    AWS_SECRET_KEY: str
    AWS_BUCKET_NAME: str
    AWS_REGION: str

    SECRET_KEY: str
    TOKEN_RESET_SALT: str
    TOKEN_RESET_TIMEOUT: int

    LLM_API_URL: str
    LLM_API_KEY: str
    LLM_MODEL: str

    TELEGRAM_API_ID: str
    TELEGRAM_API_HASH: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = 'ignore'

