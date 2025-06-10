from src.core.base.exception import AppException


class CeleryConnectionError(AppException):
    message: str = "Celery broker connection failed."
    status_code = 500
    error_code: str = "celery_connection_error"

