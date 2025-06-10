from enum import Enum

OWNER_ROLE_VALUE = "owner"

class BotParticipantRole(str, Enum):
    """Enumeration for assignable participant roles in a bot."""
    VIEWER = "viewer"
    EDITOR = "editor"
    ADMIN = "admin"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

class BotType(str, Enum):
    """Enumeration for allowed bot types."""
    MANAGER = "manager"
    SELLER = "seller"
    CONSULTANT = "consultant"

    @classmethod
    def list(cls):
        """Returns a list of all defined bot types."""
        return list(map(lambda c: c.value, cls))