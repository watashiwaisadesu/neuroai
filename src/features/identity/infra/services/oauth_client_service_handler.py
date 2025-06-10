import json
import httpx
from urllib.parse import unquote

from src.features.identity.application.services.oauth_client_service import OAuthClientService



class OAuthClientServiceHandler(OAuthClientService):
    """Google OAuth client service implementation"""

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """
        Initialize with OAuth credentials from DI container
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    async def exchange_code_for_token(self, code: str) -> str:
        """Exchange authorization code for access token"""
        decoded_code = unquote(code)
        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": decoded_code,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=payload, headers=headers)
            response.raise_for_status()
            token_data = response.json()
            token = token_data.get("access_token")
            if not token:
                raise ValueError("Google did not return access token.")
            return token

    async def fetch_user_info(self, token: str) -> tuple[str, str]:
        """Fetch user info from Google using access token"""
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get("https://www.googleapis.com/oauth2/v2/userinfo", headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get("name"), data.get("email")
