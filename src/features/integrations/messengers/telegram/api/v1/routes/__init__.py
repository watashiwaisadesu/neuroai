from fastapi import APIRouter

from src.features.integrations.messengers.telegram.api.v1.routes.reassign_user import reassign_telegram_link_router
from src.features.integrations.messengers.telegram.api.v1.routes.request_code import request_code_router
from src.features.integrations.messengers.telegram.api.v1.routes.submit_code import submit_code_router

telegram_auth_router = APIRouter(
    prefix="/v1/telegram", # Base prefix for telegram integrations
    tags=["Telegram Auth"]
)
telegram_auth_router.include_router(request_code_router)
telegram_auth_router.include_router(submit_code_router)
telegram_auth_router.include_router(reassign_telegram_link_router)

