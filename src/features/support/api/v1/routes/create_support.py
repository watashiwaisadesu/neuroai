from src.infra.logging.setup_async_logging import async_logger
logger = async_logger

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File, status

from src.core.mediator.mediator import Mediator
from src.features.identity.dependencies import get_current_user
from src.features.identity.domain.entities.user_entity import UserEntity
from src.features.identity.exceptions.user_exceptions import UserNotFoundError
from src.features.support.api.v1.dtos.support_dtos import SupportInitiatedResponseDTO
from src.features.support.application.commands.create_support.create_support_command import \
    CreateSupportCommand
from src.features.support.domain.value_objects.support_enums import SupportCategory



create_support_router = APIRouter()
from typing import List, Optional, Dict, Union  # Import Dict and Union for type hinting

AttachmentData = Dict[str, Union[bytes, str]]

@create_support_router.post(
    "/",
    response_model=SupportInitiatedResponseDTO,
    summary="Submit a new technical support request",
    status_code=status.HTTP_202_ACCEPTED,
)
@inject
async def create_support(
        subject: Optional[str] = Form(None, description="A brief subject line for the support request."),
        message: str = Form(..., description="The detailed message or description of the support issue."),
        category: Optional[SupportCategory] = Form(None,
                                                   description="The category of the support request (e.g., 'technical_issue', 'billing')."),
        attachments: List[UploadFile] = File([], description="Optional image attachments for the request."),
        mediator: Mediator = Depends(Provide["mediator"]),
        current_user: UserEntity = Depends(get_current_user),
):
    """
    Allows authenticated users to submit a technical support request.
    The request, including any file attachments, will be processed asynchronously.
    """
    logger.info(f"Received submission for support request from user: {current_user.uid}")

    processed_attachments: List[AttachmentData] = []
    for attachment_file in attachments:
        if not attachment_file.filename:
            logger.warning(f"Skipping attachment with no filename for user {current_user.uid}")
            continue

        try:
            file_contents = await attachment_file.read()
            # Ensure file is explicitly closed after reading
            await attachment_file.close()

            processed_attachments.append({
                'file_data': file_contents,
                'filename': attachment_file.filename,
                'content_type': attachment_file.content_type
            })
        except Exception as e:
            logger.error(f"Failed to read attachment '{attachment_file.filename}' for user {current_user.uid}: {e}",
                         exc_info=True)
            # Depending on your error handling strategy, you might
            # raise an HTTPException here, or just log and continue without this file.
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to read attachment: {attachment_file.filename}"
            ) from e

    command = CreateSupportCommand(
        user_uid=current_user.uid,
        email=current_user.email,
        subject=subject,
        message=message,
        category=category,
        attachments=processed_attachments,  # Pass the processed attachments
    )
    # 2. Execute the command. The handler will validate and publish an event.
    try:
        response_dto = await mediator.execute(command)
        return response_dto
    except UserNotFoundError as e:
        logger.warning(f"Support request rejected for non-existent user UID in token: {current_user.uid}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        ) from e
    except Exception as e:
        logger.critical(f"Unhandled exception initiating support request for user {current_user.uid}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while initiating your request."
        ) from e