# src/features/bot/api/dependencies.py (Example path)

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from typing import List, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status, Path  # Import Path

# Import services, entities, exceptions from appropriate locations
from src.features.bot.application.services.bot_access_service import BotAccessService
from src.features.bot.application.services.dependencies import get_bot_access_service

from src.features.bot.domain.entities.bot_entity import BotEntity
from src.features.bot.exceptions.bot_exceptions import BotNotFoundError, BotAccessDeniedError
from src.features.conversation.dependencies import get_process_incoming_message_use_case
from src.features.conversation.domain.services.process_incoming_message_command import ProcessIncomingMessageCommand
from src.features.identity.dependencies import get_current_user  # Adjust import if user provider is elsewhere
from src.features.identity.domain.entities.user_entity import UserEntity






def require_single_bot_access(allowed_roles: Optional[List[str]] = None):
    """
    Factory that returns a dependency function ('_check_access') to check
    access rights for a single bot specified by `bot_uid` in the path.

    Args:
        allowed_roles: Optional list of participant roles allowed access.
                       If None, any participation role grants access (owner always has access).

    Returns:
        An asynchronous function suitable for use with `fastapi.Depends`.
        This function returns the BotEntity if access is granted, otherwise
        raises HTTPException (404 Not Found or 403 Forbidden).
    """
    async def _check_access(
        # Get bot_uid from the path parameter.
        # Ensure the path parameter in your route (e.g., "/{bot_uid}/...") matches this name.
        uid: UUID = Path(..., title="The UID of the Bot to access", description="Bot's unique identifier from the URL path."),
        # Get the currently authenticated user
        current_user: UserEntity = Depends(get_current_user),
        # Get the access service instance
        access_service: BotAccessService = Depends(get_bot_access_service)
    ) -> BotEntity: # Return the entity on success
        """
        The actual dependency function executed by FastAPI for each request.
        Checks access and returns the BotEntity or raises HTTPException.
        """
        logger.debug(f"Dependency check: User {current_user.uid} accessing bot {uid}. Required roles: {allowed_roles}")
        try:
            # Call the service method to perform the check and retrieve the bot
            bot_entity = await access_service.check_single_bot_access(
                user_uid=current_user.uid,
                bot_uid=uid,
                allowed_roles=allowed_roles
            )
            # If no exception was raised, access is granted. Return the bot entity.
            logger.debug(f"Access granted for user {current_user.uid} to bot {uid}.")
            return bot_entity
        except BotNotFoundError as e:
            logger.warning(f"Bot not found during access check: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e) # Use message from custom exception
            )
        except BotAccessDeniedError as e:
            logger.warning(f"Access denied during access check: {e}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e) # Use message from custom exception
            )
        except Exception as e:
            # Catch any other unexpected errors during the access check
            logger.error(f"Unexpected error checking access for bot {uid} by user {current_user.uid}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An internal error occurred while checking bot access."
            )
    # Return the inner function, which FastAPI will call
    return _check_access


#
# async def get_list_of_accessible_bots(
#     current_user: UserEntity = Depends(get_current_user),
#     access_service: BotAccessService = Depends(get_bot_access_service),
#     # Optional: Add query parameters here if you want API-level filtering,
#     # otherwise filtering logic should be in the use case/service.
#     # Example: allowed_roles_query: Optional[List[str]] = Query(None, alias="role")
# ) -> List[BotEntity]:
#     """
#     FastAPI Dependency that returns a list of BotEntity objects
#     accessible to the currently authenticated user.
#
#     Raises:
#         HTTPException 500 if an unexpected error occurs during retrieval.
#     """
#     logger.debug(f"Dependency: Getting accessible bots for user {current_user.uid}")
#     try:
#         # Call the service method to get the list of bots
#         # Pass any relevant filters from query params if implemented
#         accessible_bots = await access_service.get_accessible_bots(
#             user=current_user
#             # allowed_roles=allowed_roles_query # Example if filtering by query param
#         )
#         logger.debug(f"Dependency: Found {len(accessible_bots)} accessible bots for user {current_user.uid}")
#         return accessible_bots
#     except Exception as e:
#         # Catch unexpected errors during the fetch process
#         logger.error(f"Dependency: Unexpected error getting accessible bots for user {current_user.uid}: {e}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="An internal error occurred while retrieving accessible bots."
#         )


# def get_handle_playground_connection_use_case(
#     process_message_command: ProcessIncomingMessageCommand = Depends(get_process_incoming_message_use_case)
# ) -> IHandlePlaygroundConnectionCommand:
#     """
#     Provides an instance of the IHandlePlaygroundConnectionCommand use case.
#     This is an API-level use case orchestrator.
#     """
#     logger.debug("Providing HandlePlaygroundConnectionCommand Use Case")
#     return HandlePlaygroundConnectionCommandImpl(
#         process_message_command=process_message_command
#     )