from fastapi import APIRouter

from src.features.announcement.api.v1.routes.create_announcement import create_announcement_router
from src.features.announcement.api.v1.routes.get_all_announcements import  \
    get_all_announcements_router

announcement_router = APIRouter(prefix="/v1/announcements", tags=["Announcements"])


announcement_router.include_router(create_announcement_router)
announcement_router.include_router(get_all_announcements_router)