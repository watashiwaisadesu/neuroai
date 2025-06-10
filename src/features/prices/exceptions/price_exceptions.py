# src/features/prices/exceptions/price_exceptions.py

class PriceFeatureException(Exception):
    """Base exception for the Prices feature."""
    pass

class PlatformPriceAlreadyExistsError(PriceFeatureException):
    """Raised when trying to add a platform price that already exists."""
    pass

class PlatformPriceNotFoundError(PriceFeatureException):
    """Raised when a platform price is not found."""
    pass

class PriceNegativeError(PriceFeatureException):
    """Raised when a price value is negative where it shouldn't be."""
    pass
