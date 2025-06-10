from typing import Protocol


class UserEmailProvider(Protocol):
    email: str

class AuthNotificationService(Protocol):
    async def send_verification_email(self, user: UserEmailProvider) -> None: ...

    async def send_password_reset_email(self, email: str, token: str) -> None: ...

    async def send_change_email_email(self, email: str, token: str) -> None: ...
