from fastapi import APIRouter

from src.features.integrations.messengers.telegram.api.v1.routes import telegram_auth_router

integrations_router = APIRouter(
    prefix="/integrations",
)

integrations_router.include_router(telegram_auth_router)