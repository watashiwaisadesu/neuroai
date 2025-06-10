from abc import ABC, abstractmethod

class OAuthClientService(ABC):

    @abstractmethod
    async def exchange_code_for_token(self, code: str) -> str:
        """Exchange the authorization code for an access token."""
        raise NotImplementedError

    @abstractmethod
    async def fetch_user_info(self, token: str) -> tuple[str, str]:
        """Use access token to fetch user's name and email."""
        raise NotImplementedError