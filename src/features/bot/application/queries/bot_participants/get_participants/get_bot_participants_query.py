from dataclasses import dataclass
from uuid import UUID
from src.core.mediator.query import BaseQuery

@dataclass
class GetBotParticipantsQuery(BaseQuery):
    """
    Query to retrieve participants for a specific bot.
    """
    bot_uid: UUID
    current_user_uid: UUID