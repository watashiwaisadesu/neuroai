from typing import Protocol
from fastapi import UploadFile


class S3UploaderService(Protocol):
    async def upload_file(self, file_data: bytes, filename: str, content_type: str) -> dict: ...
    async def download_file(self, file_name: str) -> tuple[bytes, str]: ...