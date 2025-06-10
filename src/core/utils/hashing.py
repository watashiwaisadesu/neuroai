from src.infra.logging.setup_async_logging import async_logger as logger
import uuid

from passlib.context import CryptContext

# Third-party imports
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from passlib.context import CryptContext

# Local imports (assuming config.py exists)
from src.config import Settings

# --- Configuration ---

# Load settings once
__SETTINGS: Settings = Settings()

# Configure password hashing context
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configure serializer specifically for Password Resets
# Use values from your Settings object
serializer = URLSafeTimedSerializer(
    secret_key=__SETTINGS.SECRET_KEY,  # Use a strong, unique secret key from settings
    salt=__SETTINGS.TOKEN_RESET_SALT  # Use a specific salt from settings
)
TOKEN_RESET_TIMEOUT_SECONDS: int = __SETTINGS.TOKEN_RESET_TIMEOUT


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hash: str) -> bool:
    return password_context.verify(password, hash)


def create_url_safe_token(payload: dict) -> str:
    payload_with_nonce = {**payload, "nonce": str(uuid.uuid4())}
    token = serializer.dumps(payload_with_nonce)
    logger.debug(f"Created password reset token for payload: {payload}")
    return token


def decode_url_safe_token(token: str):
    try:
        # loads() checks signature and automatically checks expiry based on max_age
        token_data = serializer.loads(
            token,
            max_age=TOKEN_RESET_TIMEOUT_SECONDS
        )
        logger.debug(
            f"Successfully decoded password reset token. Payload: {token_data}"
        )
        return token_data
    except SignatureExpired:
        logger.warning(
            f"Attempted to use expired password reset token: {token[:10]}..."
        )
        raise ValueError("Password reset token has expired.")
    except BadSignature as e:
        logger.warning(
            f"Invalid signature for password reset token: {token[:10]}... Error: {e}"
        )
        raise ValueError("Invalid password reset token signature.")
    except Exception as e:  # Catch other potential itsdangerous errors or unexpected issues
        logger.error(f"Error decoding password reset token: {e}", exc_info=True)
        raise ValueError("Invalid password reset token.")

