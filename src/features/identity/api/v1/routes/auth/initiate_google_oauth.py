# src/features/identity/api/routers/initiate_google_oauth_router.py
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

from src.core.mediator.mediator import Mediator
from src.features.identity.api.v1.dtos.auth.initiate_google_oauth_dto import InitiateGoogleOauthResponseDTO
from src.features.identity.application.queries.auth.initiate_google_oauth.initiate_google_oauth_query import \
    InitiateGoogleOauthQuery



initiate_google_oauth_router = APIRouter()


@initiate_google_oauth_router.get("/oauth/google/initiate", response_class=RedirectResponse)
@inject
async def initiate_google_oauth(
        mediator: Mediator = Depends(Provide["mediator"]),
):
    """
    Initiate Google OAuth flow - redirects to Google authorization page
    """
    try:
        # Create initiate Google OAuth query
        query = InitiateGoogleOauthQuery()

        # Execute query through mediator
        result: InitiateGoogleOauthResponseDTO = await mediator.query(query)

        logger.info(f"Google OAuth URL generated: {result.url}")

        return RedirectResponse(url=result.url, status_code=302)

    except Exception as e:
        logger.error(f"Unexpected error during Google OAuth initiation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate Google OAuth flow."
        )