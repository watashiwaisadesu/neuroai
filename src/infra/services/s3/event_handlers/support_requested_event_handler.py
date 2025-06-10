from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass

from src.core.base.event import BaseEventHandler
from src.core.mediator.mediator import Mediator
from src.features.support.domain.events.support_uploaded_event import SupportUploadedEvent, UploadedAttachmentData
from src.features.support.domain.events.support_requested_event import (
    SupportRequestedEvent,
)
from src.infra.services.s3.s3_service import S3UploaderService




@dataclass(kw_only=True)
class SupportRequestedEventHandler(BaseEventHandler[SupportRequestedEvent, None]):
    """
    Infrastructure handler that uploads support request attachments to S3
    and publishes an event upon completion.
    """
    _s3_service: S3UploaderService
    _mediator: Mediator

    async def handle(self, event: SupportRequestedEvent) -> None:
        logger.info(f"Handling support attachment upload for request_id: {event.uid}")
        uploaded_attachments_data: List[UploadedAttachmentData] = [] # Changed variable name and type
        try:
            if event.attachments:
                for attachment_data in event.attachments:  # Iterate over the list of attachment data dictionaries
                    # Extract pre-read data and metadata
                    file_data = attachment_data.get('file_data')
                    filename = attachment_data.get('filename')
                    content_type = attachment_data.get('content_type')

                    if not file_data or not filename or not content_type:
                        logger.warning(
                            f"Skipping incomplete attachment data for request_id: {event.uid}. "
                            f"Missing file_data, filename, or content_type."
                        )
                        continue

                    upload_response = await self._s3_service.upload_file(
                        file_data=file_data,
                        filename=filename,
                        content_type=content_type
                    )
                    uploaded_attachments_data.append({
                        "file_url": upload_response["file_url"],
                        "file_name": upload_response["file_name"],  # Ensure S3 service returns this
                        "content_type": upload_response["content_type"],  # Ensure S3 service returns this
                        "file_size": upload_response["file_size"],  # Ensure S3 service returns this
                    })

            # Publish the completion event with the new S3 URLs
            attachments_uploaded_event = SupportUploadedEvent(
                uid=event.uid,
                user_uid=event.user_uid,
                email=event.email,
                subject=event.subject,
                message=event.message,
                category=event.category,
                attachments_data=uploaded_attachments_data,
            )
            await self._mediator.publish([attachments_uploaded_event])
            logger.info(f"Successfully processed attachments for request_id: {event.uid}.")

        except Exception as e:
            logger.error(f"Failed to upload attachments for request_id {event.uid}: {e}", exc_info=True)
            # Optionally, publish a failure event here for robust error handling.
            raise