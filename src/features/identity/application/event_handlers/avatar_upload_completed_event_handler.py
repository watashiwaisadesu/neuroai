# src/features/identity/application/event_handlers/avatar_upload_completed_handler.py

from dataclasses import dataclass
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger

from src.core.base.event import BaseEventHandler
from src.core.mediator.mediator import Mediator
from src.features.identity.domain.events.user_avatar_events import (
    UserAvatarUploadCompletedEvent
)
from src.features.identity.domain.repositories.user_unit_of_work import UserUnitOfWork




@dataclass(kw_only=True)
class AvatarUploadCompletedEventHandler(BaseEventHandler[UserAvatarUploadCompletedEvent, None]):
    """Domain handler that updates user's avatar URL after successful upload"""
    _unit_of_work: UserUnitOfWork
    _mediator: Mediator

    async def handle(self, event: UserAvatarUploadCompletedEvent) -> None:
        async with self._unit_of_work as uow:
            user = await uow.user_repository.find_by_uid(event.user_uid)
            if not user:
                logger.error(f"User {event.user_uid} not found for avatar update")
                return

            # Store old URL
            old_avatar_url = user.avatar_file_url

            # Update avatar URL
            user.update_avatar(event.file_url)
            await uow.user_repository.update(user)


            logger.info(f"User {user.uid} avatar URL updated to: {event.file_url}")