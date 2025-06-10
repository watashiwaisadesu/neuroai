from src.infra.services.email.app import mail, create_message
from asgiref.sync import async_to_sync
from src.infra.services.celery.app import celery


@celery.task()
def send_email(recipients: list[str], subject: str, body: str):
    message = create_message(recipients=recipients, subject=subject, body=body)
    async_to_sync(mail.send_message)(message)
    print(f"Email sent: {message}")