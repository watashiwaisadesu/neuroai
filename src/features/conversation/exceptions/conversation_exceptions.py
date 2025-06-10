from src.core.base.exception import AppException

class ConversationNotFoundError(AppException):
    message = "Conversation not found."
    status_code = 404
    error_code = "conversation_not_found"

class BotAccessDeniedError(AppException): # You might already have this in bot_exceptions.py
    message = "Not authorized to access the bot associated with this conversation."
    status_code = 403
    error_code = "bot_access_denied"