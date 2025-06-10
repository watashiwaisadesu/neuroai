from dataclasses import dataclass

from src.core.base.command import BaseCommandHandler, BaseCommand
# from src.features.identity.domain.value_objects.email_vo import Email


@dataclass
class LoginUserCommand(BaseCommand):
    email: str
    password: str
