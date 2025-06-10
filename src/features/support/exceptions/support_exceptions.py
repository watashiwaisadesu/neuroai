# src/features/support/exceptions/support_exceptions.py

class SupportError(Exception):
    """Base exception for support request related errors."""
    def __init__(self, message: str = "An unknown support request error occurred.", details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

class SupportNotFoundError(SupportError):
    """Exception raised when a support request is not found."""
    def __init__(self, message: str = "Support request not found."):
        super().__init__(message)

class SupportAlreadyExistsError(SupportError):
    """Exception raised when attempting to create a support request that already exists."""
    def __init__(self, message: str = "Support request already exists."):
        super().__init__(message)

class InvalidSupportDataError(SupportError):
    """Exception raised for invalid data provided for a support request."""
    def __init__(self, message: str = "Invalid support request data provided."):
        super().__init__(message)