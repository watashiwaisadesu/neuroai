# src/features/identity/application/queries/auth/initiate_google_oauth/initiate_google_oauth_query_handler.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass

from src.core.base.query import BaseQueryHandler
from src.features.identity.api.v1.dtos.auth.initiate_google_oauth_dto import InitiateGoogleOauthResponseDTO
from src.features.identity.application.queries.auth.initiate_google_oauth.initiate_google_oauth_query import InitiateGoogleOauthQuery




@dataclass
class InitiateGoogleOauthQueryHandler(BaseQueryHandler[InitiateGoogleOauthQuery, InitiateGoogleOauthResponseDTO]):
    _google_client_id: str
    _google_redirect_uri: str

    async def __call__(self, query: InitiateGoogleOauthQuery) -> InitiateGoogleOauthResponseDTO:
        """
        Generate Google OAuth authorization URL - EXACT same logic as your original
        """
        logger.info("Initiating Google OAuth flow")

        # Generate OAuth URL - same logic as original
        url = (
            "https://accounts.google.com/o/oauth2/auth"
            f"?response_type=code"
            f"&client_id={self._google_client_id}"
            f"&redirect_uri={self._google_redirect_uri}"
            f"&scope=openid%20profile%20email"
            f"&access_type=offline"
        )

        logger.debug(f"Generated Google OAuth URL: {url}")
        print(url)
        return InitiateGoogleOauthResponseDTO(url=url)