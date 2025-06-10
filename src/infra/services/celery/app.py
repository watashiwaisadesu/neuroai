from celery import Celery
from src.config import Settings


_settings: Settings = Settings()

# celery -A src.infra.services.celery.app worker --loglevel=info
celery = Celery(
    "worker",
    broker=_settings.REDIS_URL,
    backend=_settings.REDIS_URL,
)


celery.autodiscover_tasks([
    "src.infra.services.email.send_verification_email_task",
])
