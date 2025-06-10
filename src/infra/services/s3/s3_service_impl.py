# src/infra/services/s3/s3_uploader_service_impl.py

import aioboto3
import uuid
import magic
from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from fastapi import UploadFile, HTTPException, status
from botocore.exceptions import ClientError
from src.infra.services.s3.s3_service import S3UploaderService
from src.config import Settings

aws_settings = Settings()



MB = 1024 * 1024
SUPPORTED_FILE_TYPES = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "application/pdf": "pdf"
}

class S3UploaderServiceHandler(S3UploaderService):
    async def _get_s3_client(self):
        session = aioboto3.Session()
        return session.client(
            "s3",
            aws_access_key_id=aws_settings.AWS_ACCESS_KEY,
            aws_secret_access_key=aws_settings.AWS_SECRET_KEY,
            region_name=aws_settings.AWS_REGION,
        ), aws_settings.AWS_BUCKET_NAME

    async def upload_file(self, file_data: bytes, filename: str, content_type: str) -> dict:
        """
        Uploads file data (bytes) to S3, using provided filename and content type.

        Args:
            file_data: The binary content of the file.
            filename: The original name of the file.
            content_type: The MIME type of the file.

        Returns:
            A dictionary containing the uploaded file's name and URL.

        Raises:
            HTTPException: If file size is unsupported, file type is unsupported, or S3 upload fails.
        """
        s3, bucket = await self._get_s3_client()
        contents = file_data # Now contents is directly the bytes data

        if not (0 < len(contents) <= 5 * MB):
            raise HTTPException(400, "Supported file size is 0 - 5 MB")

        # Use the provided content_type directly for validation
        if content_type not in SUPPORTED_FILE_TYPES:
            raise HTTPException(400, f"Unsupported file type: {content_type}")

        extension = SUPPORTED_FILE_TYPES[content_type]
        # Generate a unique file name using UUID and the correct extension
        file_name = f"{uuid.uuid4()}.{extension}"
        file_size = len(contents)
        file_url = f"https://{bucket}.s3.amazonaws.com/{file_name}"

        async with s3 as client:
            try:
                await client.put_object(
                    Bucket=bucket,
                    Key=file_name,
                    Body=contents,
                    ContentType=content_type, # Use the provided content_type
                    ACL="public-read", # Adjust ACL as per your requirements
                )

                return {
                    "file_name": filename,  # Original filename
                    "file_url": file_url,
                    "content_type": content_type,
                    "file_size": file_size,  # Size of the uploaded bytes
                }
            except ClientError as err:
                # Log the error for debugging
                print(f"S3 Client Error: {err}")
                raise HTTPException(500, f"S3 Upload Failed: {err}")
            except Exception as e:
                # Catch any other unexpected errors during upload
                print(f"An unexpected error occurred during S3 upload: {e}")
                raise HTTPException(500, f"An unexpected error occurred: {e}")

    async def download_file(self, file_name: str) -> tuple[bytes, str]:
        s3, bucket = await self._get_s3_client()

        async with s3 as client:
            try:
                response = await client.get_object(Bucket=bucket, Key=file_name)
                return await response["Body"].read(), response["ContentType"]
            except ClientError as err:
                logger.error(str(err))
                raise HTTPException(status_code=404, detail="File not found")
