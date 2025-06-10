from fastapi import APIRouter

from src.features.identity.api.v1.routes.profile.get_me import get_me_router
from src.features.identity.api.v1.routes.profile.get_me_avatar import get_me_avatar_router

from src.features.identity.api.v1.routes.profile.update_me import update_me_router
from src.features.identity.api.v1.routes.profile.update_me_avatar import update_avatar_router

v1_users_router = APIRouter(prefix="/v1/users", tags=["Users"])



v1_users_router.include_router(get_me_router)
v1_users_router.include_router(update_me_router)
v1_users_router.include_router(update_avatar_router)
v1_users_router.include_router(get_me_avatar_router)
