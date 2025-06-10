# src/infra/services/s3/event_handlers/avatar_upload_handler.py

from dataclasses import dataclass
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
import io

from src.core.base.event import BaseEventHandler
from src.core.mediator.mediator import Mediator
from src.features.identity.domain.events.user_avatar_events import (
    UserAvatarUploadRequestedEvent,
    UserAvatarUploadCompletedEvent
)
from src.infra.services.s3.s3_service import S3UploaderService




@dataclass(kw_only=True)
class AvatarUploadRequestedEventHandler(BaseEventHandler[UserAvatarUploadRequestedEvent, None]):
    """Infrastructure handler that uploads avatar to S3"""
    _s3_service: S3UploaderService
    _mediator: Mediator

    async def handle(self, event: UserAvatarUploadRequestedEvent) -> None:
        try:
            # Upload file to S3
            response = await self._s3_service.upload_file(
                file_data=event.avatar_file_data,  # Pass the BytesIO object
                filename=event.file_name,
                content_type=event.content_type
            )
            file_url = response["file_url"]

            # Publish completion event
            upload_completed_event = UserAvatarUploadCompletedEvent(
                request_id=event.request_id,
                user_uid=event.user_uid,
                file_url=file_url,
                file_size=len(event.avatar_file_data),  # Use the actual size of the bytes data
                content_type=event.content_type,  # Use the content type from the event
            )

            await self._mediator.publish([upload_completed_event])

            logger.info(f"Avatar uploaded successfully for user {event.user_uid}")

        except Exception as e:
            logger.error(f"Failed to upload avatar for user {event.user_uid}: {e}")
            # Could publish a failure event here for error handling
            raise


