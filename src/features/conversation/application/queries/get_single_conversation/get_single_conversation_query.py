# src/features/conversation/application/queries/get_single_bot_conversation/get_single_bot_conversation_query.py

from dataclasses import dataclass
from uuid import UUID
from src.core.base.query import BaseQuery


@dataclass
class GetSingleBotConversationQuery(BaseQuery):
    conversation_uid: UUID
    user_uid: UUID
