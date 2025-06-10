from src.core.base.exception import AppException

class UserNotFoundError(AppException):
    message = "User not found."
    status_code = 404
    error_code = "user_not_found"

class UserAlreadyExistsError(AppException):
    message = "User already exists."
    status_code = 409
    error_code = "user_already_exists"

class UsersNotFoundError(AppException):
    message = "No users found."
    status_code = 404
    error_code = "users_not_found"

class AvatarNotFoundError(AppException):
    message = "Avatar not found."
    status_code = 404
    error_code = "avatar_not_found"
