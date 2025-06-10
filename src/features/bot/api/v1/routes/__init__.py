from fastapi import APIRouter

from src.features.bot.api.v1.routes.bot_documents.delete_documents import delete_documents_router
from src.features.bot.api.v1.routes.bot_documents.upload_documents import upload_documents_router
from src.features.bot.api.v1.routes.bot_management.create_bot import create_bot_router
from src.features.bot.api.v1.routes.bot_management.delete_bot import delete_bot_router
from src.features.bot.api.v1.routes.bot_management.duplicate_bot import duplicate_bot_router
from src.features.bot.api.v1.routes.bot_management.get_last_active_bots import last_active_bots_router
from src.features.bot.api.v1.routes.bot_management.get_user_bots import get_user_bots_router
from src.features.bot.api.v1.routes.bot_management.transfer_bot import transfer_bot_router
from src.features.bot.api.v1.routes.bot_management.update_bot import update_bot_router

from src.features.bot.api.v1.routes.bot_participants.get_participants import get_participants_router
from src.features.bot.api.v1.routes.bot_participants.link_participant import link_participant_router
from src.features.bot.api.v1.routes.bot_participants.unlink_participant import unlink_participant_router
from src.features.bot.api.v1.routes.bot_participants.update_participant import update_participant_router
from src.features.bot.api.v1.routes.bot_playground import playground_router

from src.features.bot.api.v1.routes.bot_services.get_services import get_services_router
from src.features.bot.api.v1.routes.bot_services.link_service import link_service_router
from src.features.bot.api.v1.routes.bot_services.unlink_service import unlink_service_router


bot_router = APIRouter(prefix="/v1/bots", tags=["Bots"])
bot_participant_router = APIRouter(prefix="/v1/bots", tags=["Bot Participants"])
bot_services_router = APIRouter(prefix="/v1/bots", tags=["Bot Services"])

bot_documents_router = APIRouter(prefix="/v1/bots", tags=["Bot Documents"])



bot_router.include_router(create_bot_router)
bot_router.include_router(get_user_bots_router)
bot_router.include_router(delete_bot_router)
bot_router.include_router(update_bot_router)
bot_router.include_router(duplicate_bot_router)
bot_router.include_router(transfer_bot_router)
bot_router.include_router(last_active_bots_router)

bot_router.include_router(playground_router)


bot_participant_router.include_router(link_participant_router)
bot_participant_router.include_router(update_participant_router)
bot_participant_router.include_router(unlink_participant_router)
bot_participant_router.include_router(get_participants_router)


bot_services_router.include_router(link_service_router)
bot_services_router.include_router(unlink_service_router)
bot_services_router.include_router(get_services_router)


bot_documents_router.include_router(upload_documents_router)
bot_documents_router.include_router(delete_documents_router)
