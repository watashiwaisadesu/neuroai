from src.infra.services.s3.s3_service_impl import S3UploaderServiceHandler
from src.infra.services.s3.s3_service import S3UploaderService

def get_s3_service() -> S3UploaderService:
    return S3UploaderServiceHandler()