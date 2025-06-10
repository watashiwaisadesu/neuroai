from fastapi import APIRouter

from src.features.conversation.api.v1.routes.get_all_conversations import get_all_conversations_router
from src.features.conversation.api.v1.routes.get_playground_conversation import get_playground_conversation_router
from src.features.conversation.api.v1.routes.get_conversation import get_conversation_router


conversation_router = APIRouter(prefix="/v1/conversations", tags=["Conversations"])

conversation_router.include_router(get_all_conversations_router)
conversation_router.include_router(get_conversation_router)
conversation_router.include_router(get_playground_conversation_router)
