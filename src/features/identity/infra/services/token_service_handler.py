from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
import uuid
import jwt

from datetime import datetime, timedelta
from src.features.identity.application.services.token_service import TokenService


class TokenServiceHandler(TokenService):
    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        access_token_expiry: int,     # minutes
        refresh_token_expiry: int,    # days
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expiry = access_token_expiry
        self.refresh_token_expiry = refresh_token_expiry

    def create_access_token(self, payload: dict) -> str:
        return self._create_token(payload, minutes=self.access_token_expiry)

    def create_refresh_token(self, payload: dict) -> str:
        return self._create_token(payload, days=self.refresh_token_expiry, refresh=True)

    def _create_token(self, user_data: dict, minutes: int = 0, days: int = 0, refresh: bool = False) -> str:
        expiry = datetime.utcnow() + timedelta(minutes=minutes, days=days)
        payload = {
            "user": user_data,
            "exp": expiry,
            "jti": str(uuid.uuid4()),
            "refresh": refresh,
        }

        return jwt.encode(payload, key=self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> dict | None:
        try:
            return jwt.decode(token, key=self.secret_key, algorithms=[self.algorithm])
        except jwt.PyJWTError as e:
            logger.error(f"Token decode error: {str(e)}")
            return None
