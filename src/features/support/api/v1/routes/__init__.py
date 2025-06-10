from fastapi import APIRouter

from src.features.support.api.v1.routes.create_support import create_support_router
from src.features.support.api.v1.routes.get_support_requests import get_supports_router

support_router = APIRouter(prefix="/v1/supports", tags=["Support"])

support_router.include_router(create_support_router)
support_router.include_router(get_supports_router)