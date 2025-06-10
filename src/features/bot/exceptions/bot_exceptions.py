from src.core.base.exception import AppException
from fastapi import status


class BotNotFoundError(AppException):
    message = "The requested bot was not found."
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "bot_not_found"


class BotAlreadyExistsError(AppException):
    message = "A bot with the given parameters already exists."
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "bot_already_exists"

class BotAccessDeniedError(AppException):
    """Used when a user tries to access a bot they don't have permission for."""
    message = "Access denied to the specified bot."
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "bot_access_denied"

class InvalidBotAISettingsError(AppException):
    """Raised when provided AI settings fail validation."""
    message = "Invalid AI configuration settings provided."
    # 422 Unprocessable Entity is often suitable for validation errors on input data
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "invalid_ai_settings"



class InvalidBotQuotaError(AppException):
    """Raised when provided quota settings fail validation."""
    message = "Invalid bot quota settings provided."
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "invalid_bot_quota"




class InvalidBotDetailsError(AppException):
    """Raised when other provided bot details fail validation."""
    message = "Invalid bot details provided."
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "invalid_bot_details"



class ParticipantNotFoundError(AppException):
    """Raised when a specific bot participant is not found."""
    message = "The specified participant was not found for this bot."
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "participant_not_found"


class ParticipantAlreadyExistsError(AppException):
    """Raised when attempting to add a user who is already a participant."""
    message = "This user is already a participant in this bot."
    # HTTP 409 Conflict is often suitable for duplicate resource attempts
    status_code = status.HTTP_409_CONFLICT
    error_code = "participant_already_exists"


class CannotAddOwnerAsParticipantError(AppException):
    """Raised when attempting to add the bot owner as a participant."""
    message = "Bot owner cannot be added as a participant."
    # Use 400 Bad Request as it's a client error based on input/logic
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "owner_cannot_be_participant"


class CannotUpdateOwnerRoleError(AppException): # Assuming AppException base
    """Raised when attempting to change the role of the bot owner via participant routes."""
    message = "Cannot change the role of the bot owner via participant management."
    status_code = status.HTTP_403_FORBIDDEN # Or 400 Bad Request
    error_code = "cannot_update_owner_role"

class CannotUnlinkOwnerError(AppException): # Assuming AppException base
    """Raised when attempting to remove the bot owner."""
    message = "Cannot remove the bot owner as a participant."
    status_code = status.HTTP_403_FORBIDDEN # Or 400 Bad Request
    error_code = "cannot_remove_owner"

class ServiceAlreadyLinkedError(AppException):
    """Raised when attempting to link a service that is already linked to the bot."""
    message = "This service platform is already linked to this bot."
    status_code = status.HTTP_409_CONFLICT
    error_code = "service_already_linked"

class ServiceNotFoundError(AppException):
    """Raised when a specific service link is not found for the bot."""
    message = "The specified service link was not found for this bot."
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "service_not_found"


class CannotTransferToSelfError(AppException):
    """Raised when attempting to transfer a bot to its current owner."""
    message = "Cannot transfer the bot to its current owner."
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "cannot_transfer_to_self"

class NewOwnerNotFoundError(AppException): # More specific than general UserNotFoundError
    """Raised when the specified new owner email is not found."""
    message = "The specified new owner was not found."
    status_code = status.HTTP_404_NOT_FOUND # 404 for new owner, or 400 on request
    error_code = "new_owner_not_found"

class DocumentUploadFailedError(AppException):
    message = "Failed to upload one or more documents."
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR  # Or 400 if client-side issue
    error_code = "document_upload_failed"

class DocumentNotFoundError(AppException):
    message = "The requested document was not found."
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "document_not_found"

class InvalidFileTypeError(AppException):
    message = "The uploaded file type is not allowed."
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "invalid_file_type"

class FileTooLargeError(AppException):
    message = "The uploaded file is too large."
    status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    error_code = "file_too_large"


class BotAuthorizationError(AppException):
    message = "Bot authorization failed."
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "bot_authorization_failed"


