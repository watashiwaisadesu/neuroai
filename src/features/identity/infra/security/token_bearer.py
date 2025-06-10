# src/features/identity/infra/security/token_bearer.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from typing import Optional, Dict, Any
from fastapi import Request, WebSocket, HTTPException, status, WebSocketException
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials

# Import your services and exceptions
from src.features.identity.application.services.token_service import TokenService
from src.features.identity.application.services.token_blocklist_service import TokenBlocklistService
from src.features.identity.exceptions.auth_exceptions import (
    InvalidTokenError,
    AccessTokenRequired,
    RefreshTokenRequired
)




class AppTokenBearer(HTTPBearer):
    def __init__(
            self,
            token_service: TokenService,
            blocklist_service: TokenBlocklistService,
            auto_error: bool = True,
            scheme_name: str = "Bearer"  # Add scheme_name parameter with default
    ):
        # Pass the potentially custom scheme_name to the parent HTTPBearer
        super().__init__(auto_error=auto_error, scheme_name=scheme_name)
        self.token_service = token_service
        self.blocklist_service = blocklist_service
        logger.debug(f"{self.__class__.__name__} initialized with scheme_name: '{scheme_name}'.")

    # ... (the rest of your __call__, _verify_token_type, verify_token_from_query methods remain the same) ...
    async def __call__(self, request: Request = None, websocket: WebSocket = None) -> Dict[str, Any]:
        auth_creds: Optional[HTTPAuthorizationCredentials] = None
        is_websocket_context = bool(websocket)
        # ... (rest of the __call__ method as corrected in the previous step) ...
        # Ensure this method uses self.scheme_name if needed for error messages,
        # though HTTPBearer parent class handles that for WWW-Authenticate.

        # --- Token Extraction (Simplified for Brevity - Use your full version) ---
        if is_websocket_context:
            auth_header_value: Optional[str] = None
            for name, value in websocket.scope.get("headers", []):
                if name == b"authorization":
                    auth_header_value = value.decode("utf-8", errors="ignore")
                    break
            if auth_header_value:
                parts = auth_header_value.split()
                scheme_from_header = parts[0] if parts else ""
                token_str = parts[1] if len(parts) > 1 else ""
                if scheme_from_header.lower() == "bearer" and token_str:
                    auth_creds = HTTPAuthorizationCredentials(scheme="Bearer",
                                                              credentials=token_str)  # Use "Bearer" for the scheme in creds

            if not auth_creds and self.auto_error:
                raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION,
                                         reason=f"{self.scheme_name} token missing or malformed.")
        elif request:
            try:
                auth_creds = await super().__call__(request)
            except HTTPException as e:
                if self.auto_error:
                    raise InvalidTokenError(detail="Authentication token missing or malformed.") from e
                return None
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Authentication context error.")

        if not auth_creds: return None
        token = auth_creds.credentials

        # --- Token Decoding, Blocklist Check, and Type Verification (Simplified for Brevity - Use your full version) ---
        try:
            token_data = self.token_service.decode_token(token)
            if not token_data: raise InvalidTokenError("Token decoded to None.")
            jti = token_data.get("jti")
            if not jti: raise InvalidTokenError("Token payload missing 'jti'.")
            if await self.blocklist_service.is_blocked(jti): raise InvalidTokenError("Token has been revoked.")
            self._verify_token_type(token_data)
        except (InvalidTokenError, AccessTokenRequired, RefreshTokenRequired) as e:
            if self.auto_error:
                detail = e.message if hasattr(e, 'message') and e.message else str(e)
                if is_websocket_context:
                    raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason=detail) from e
                else:
                    # Let the custom AppException propagate for HTTP
                    if isinstance(e, InvalidTokenError):
                        e.status_code = status.HTTP_401_UNAUTHORIZED
                    elif isinstance(e, (AccessTokenRequired, RefreshTokenRequired)):
                        e.status_code = status.HTTP_401_UNAUTHORIZED  # Or 403
                    raise e
            return None
        # ... (other specific error handling) ...
        return token_data

    def _verify_token_type(self, token_data: dict):
        raise NotImplementedError("Subclasses must implement _verify_token_type.")

    async def verify_token_from_query(self, token: str) -> Dict[str, Any]:
        # ... (implementation as before)
        logger.debug(f"Verifying token from query parameter: {token[:20]}...")
        if not token:
            raise InvalidTokenError("No token provided in query.")
        try:
            token_data = self.token_service.decode_token(token)
        except InvalidTokenError as e:
            logger.warning(f"Query token decoding failed: {e.message if hasattr(e, 'message') else str(e)}")
            raise
        if not token_data: raise InvalidTokenError("Invalid token in query parameters.")
        jti = token_data.get("jti")
        if not jti: raise InvalidTokenError("Invalid token: Missing JTI (query).")
        if await self.blocklist_service.is_blocked(jti):
            raise InvalidTokenError("Token from query is blocked.")
        self._verify_token_type(token_data)
        logger.info(f"Token from query validated for user UID: {token_data.get('uid') or token_data.get('user_uid')}")
        return token_data


# src/features/identity/infra/security/token_bearer.py (Continued)

class AccessTokenBearer(AppTokenBearer):
    def __init__(
        self,
        token_service: TokenService,
        blocklist_service: TokenBlocklistService,
        auto_error: bool = True
    ):
        # Provide a distinct scheme_name for OpenAPI
        super().__init__(
            token_service=token_service,
            blocklist_service=blocklist_service,
            auto_error=auto_error,
            scheme_name="AccessTokenAuth" # Custom scheme name for Swagger
        )

    def _verify_token_type(self, token_data: dict):
        """Ensures the token is an access token (not a refresh token)."""
        logger.debug("AccessTokenBearer: Verifying token is an access token.")
        if token_data.get("refresh") is True:
            logger.warning("AccessTokenBearer: Refresh token provided where access token was expected.")
            raise AccessTokenRequired()


class RefreshTokenBearer(AppTokenBearer):
    def __init__(
        self,
        token_service: TokenService,
        blocklist_service: TokenBlocklistService,
        auto_error: bool = True
    ):
        # Provide a distinct scheme_name for OpenAPI
        super().__init__(
            token_service=token_service,
            blocklist_service=blocklist_service,
            auto_error=auto_error,
            scheme_name="RefreshTokenAuth" # Custom scheme name for Swagger
        )

    def _verify_token_type(self, token_data: dict):
        """Ensures the token is a refresh token."""
        logger.debug("RefreshTokenBearer: Verifying token is a refresh token.")
        if token_data.get("refresh") is not True:
            logger.warning("RefreshTokenBearer: Non-refresh token provided where refresh token was expected.")
            raise RefreshTokenRequired()



