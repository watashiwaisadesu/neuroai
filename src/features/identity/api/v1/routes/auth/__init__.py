from fastapi import APIRouter

from src.features.identity.api.v1.routes.auth.callback_google_oauth import callback_google_oauth_router
from src.features.identity.api.v1.routes.auth.request_change_email import request_change_email_router
from src.features.identity.api.v1.routes.auth.change_password import change_password_router
from src.features.identity.api.v1.routes.auth.initiate_google_oauth import initiate_google_oauth_router
from src.features.identity.api.v1.routes.auth.login_user import login_user_router
from src.features.identity.api.v1.routes.auth.logout_user import logout_user_router
from src.features.identity.api.v1.routes.auth.refresh_access_token import refresh_token_user_router
from src.features.identity.api.v1.routes.auth.register_user import register_user_router
from src.features.identity.api.v1.routes.auth.verify_password import verify_reset_password_router
from src.features.identity.api.v1.routes.auth.request_reset_password import request_reset_password_router
from src.features.identity.api.v1.routes.auth.verify_email import verify_email_router
from src.features.identity.api.v1.routes.auth.verify_user import verify_user_router


v1_auth_router = APIRouter(prefix="/v1/auth", tags=["auth"])



v1_auth_router.include_router(register_user_router)
v1_auth_router.include_router(login_user_router)
v1_auth_router.include_router(logout_user_router)
v1_auth_router.include_router(refresh_token_user_router)
v1_auth_router.include_router(initiate_google_oauth_router)
v1_auth_router.include_router(callback_google_oauth_router)
v1_auth_router.include_router(change_password_router)
v1_auth_router.include_router(request_reset_password_router)
v1_auth_router.include_router(request_change_email_router)
v1_auth_router.include_router(verify_reset_password_router)
v1_auth_router.include_router(verify_email_router)
v1_auth_router.include_router(verify_user_router)