from fastapi import APIRouter

# Import all your feature-specific routers
from src.features.announcement.api.v1.routes import announcement_router
from src.features.bot.api.v1.routes import bot_router, bot_participant_router, bot_services_router, bot_documents_router
from src.features.conversation.api.v1.routes import conversation_router
from src.features.identity.api.v1.routes.auth import v1_auth_router
from src.features.identity.api.v1.routes.profile import v1_users_router
from src.features.integrations.messengers import integrations_router
from src.features.prices.api.v1.routes import price_router
from src.features.support.api.v1.routes import support_router

# Create the main API router
main_api_router = APIRouter()

# Include all individual feature routers
main_api_router.include_router(v1_auth_router)
main_api_router.include_router(v1_users_router)
main_api_router.include_router(bot_router)
main_api_router.include_router(bot_participant_router)
main_api_router.include_router(bot_services_router)
main_api_router.include_router(bot_documents_router)
main_api_router.include_router(conversation_router)
main_api_router.include_router(integrations_router)
main_api_router.include_router(announcement_router)
main_api_router.include_router(support_router)
main_api_router.include_router(price_router)

