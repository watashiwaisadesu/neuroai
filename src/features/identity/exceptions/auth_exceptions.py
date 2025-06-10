from src.core.base.exception import AppException

class InvalidTokenError(AppException):
    message = "Invalid or expired token provided."
    status_code = 400
    error_code = "invalid_token"


class AuthVerificationError(AppException):
    message = "User verification failed. Please try again later."
    status_code = 500
    error_code = "auth_verification_failed"


class AccountNotVerifiedError(AppException):
    message = "Account is not verified. Please check your email for verification link."
    status_code = 403
    error_code = "account_not_verified"

class InsufficientPermissionError(AppException):
    message = "You do not have enough permissions to perform this action."
    status_code = 403
    error_code = "insufficient_permissions"


class InvalidCredentialsError(AppException):
    message = "Invalid email or password."
    status_code = 401
    error_code = "invalid_credentials"


class AccessTokenRequired(AppException):
    message = "Access token required. Provided token is not valid for this operation."
    status_code = 401
    error_code = "access_token_required"


class RefreshTokenRequired(AppException):
    message = "Refresh token required. Provided token is not a refresh token."
    status_code = 401
    error_code = "refresh_token_required"


class PasswordsDoNotMatchError(AppException):
    message = "Passwords do not match."
    status_code = 400
    error_code = "passwords_do_not_match"

class EmailAlreadyInUseError(AppException):
    message = "Email is already in use."
    status_code = 400
    error_code = "email_already_in_use"


class InvalidEmailVerificationToken(AppException):
    message = "Неверный или устаревший токен."
    status_code = 400
    error_code = "invalid_email_verification_token"

class TokenMissingData(AppException):
    message = "Токен не содержит необходимых данных."
    status_code = 400
    error_code = "token_missing_data"

class UserNotFoundForToken(AppException):
    message = "Пользователь не найден по UID из токена."
    status_code = 404
    error_code = "user_not_found"

class GoogleTokenExchangeError(AppException):
    message = "Failed to exchange code for access token with Google."
    status_code = 400
    error_code = "google_token_exchange_failed"

class GoogleUserInfoFetchError(AppException):
    message = "Failed to fetch user info from Google."
    status_code = 400
    error_code = "google_user_info_fetch_failed"

class OAuthUserCreationError(AppException):
    message = "Failed to create user during OAuth flow."
    status_code = 500
    error_code = "oauth_user_creation_failed"