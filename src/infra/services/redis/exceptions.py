from src.core.base.exception import AppException


class RedisConnectionError(AppException):
    message = "Redis connection failed. Ensure Redis is running."
    status_code = 503
    error_code = "redis_connection_error"