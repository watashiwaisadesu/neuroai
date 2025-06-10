from fastapi import status
from src.core.base.exception import AppException

class TelegramGenericError(AppException):
    """A generic error related to Telegram integration."""
    message = "An unexpected error occurred with the Telegram integration."
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "telegram_generic_error"


class TelegramConnectionError(AppException):
    """Raised when the application cannot connect to Telegram's servers."""
    message = "Could not connect to Telegram. Please check network or try again later."
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE # Service Unavailable
    error_code = "telegram_connection_error"


class TelegramAuthError(AppException):
    """Raised for authentication failures with Telegram (e.g., invalid session, bad code)."""
    message = "Telegram authentication failed. Please try logging in again."
    # 401 for auth issues, or 400 if it's due to bad input from user (like wrong code)
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "telegram_auth_error"



class TelegramRateLimitError(AppException):
    """Raised when Telegram APIs indicate a rate limit or flood wait."""
    message = "Too many requests to Telegram. Please wait and try again."
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    error_code = "telegram_rate_limit_error"



class TelegramResourceNotFoundError(AppException):
    """Raised when a specific Telegram resource (e.g., user, chat) is not found via API."""
    message = "The requested Telegram resource was not found."
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "telegram_resource_not_found"


class TelegramAppCredentialsNotSetError(AppException):
    """Raised when Telegram API ID/Hash are not configured."""
    message = "Telegram application credentials (API ID/Hash) are not configured in the system."
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR # Server misconfiguration
    error_code = "telegram_app_credentials_missing"


class TelegramLinkNotFoundError(AppException):
    """Raised when a TelegramAccountLinkEntity is not found in the database."""
    message = "The specified Telegram account link was not found."
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "telegram_link_not_found"




class TelegramLinkAlreadyExistsError(AppException):
    """
    Raised when attempting to create a TelegramAccountLinkEntity that
    would violate a unique constraint (e.g., phone number or Telegram user ID
    is already linked in a conflicting way).
    """
    message = "This Telegram account or phone number is already linked in a conflicting manner."
    status_code = status.HTTP_409_CONFLICT # 409 Conflict is suitable for duplicates
    error_code = "telegram_link_already_exists"




