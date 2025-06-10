

class AppException(Exception):
    """Базовая ошибка приложения с сообщением и статус-кодом"""
    message: str = "Internal Server Error"
    status_code: int = 500
    error_code: str = "app_error"

    def __init__(self, message=None, error_code=None):
        if message:
            self.message = message
        if error_code:
            self.error_code = error_code

    def __str__(self):
        return self.message