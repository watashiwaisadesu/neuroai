from dependency_injector import containers, providers
from src.config import Settings
from src.core.mediator.mediator import Mediator
from src.features.identity.domain.events.user_registered_events import UserRegisteredEvent
from src.features.notification.application.event_handlers.oauth_login_successful_event_handler import \
    OAuthLoginSuccessfulEventHandler
from src.features.notification.application.event_handlers.oauth_user_created_event_handler import \
    OAuthUserRegisteredEventHandler
from src.features.notification.application.event_handlers.send_password_reset_email_event_handler import \
    SendPasswordResetEmailEventHandler
from src.features.notification.application.event_handlers.send_password_reset_email_handler import \
    SendEmailChangeConfirmationEventHandler
from src.features.notification.application.event_handlers.send_user_verification_email_handler import SendUserVerificationEmailEventHandler
from src.features.notification.infra.providers.smtp_email_sender import SmtpEmailSender



class NotificationContainer(containers.DeclarativeContainer):
    mediator = providers.Dependency(instance_of=Mediator)
    config = providers.DelegatedSingleton(Settings)

    # Email sender service
    email_sender = providers.Factory(
        SmtpEmailSender,
        frontend_url=config.provided.FRONTEND_URL
    )

    send_user_verification_email_event_handler = providers.Factory(
        SendUserVerificationEmailEventHandler,
        email_sender=email_sender
    )

    send_password_reset_email_event_handler = providers.Factory(
        SendPasswordResetEmailEventHandler,
        email_sender=email_sender
    )

    send_email_change_confirmation_event_handler = providers.Factory(
        SendEmailChangeConfirmationEventHandler,
        email_sender=email_sender
    )

    oauth_user_created_event_handler = providers.Factory(
        OAuthUserRegisteredEventHandler,
        email_sender=email_sender
    )

    oauth_login_successful_event_handler = providers.Factory(
        OAuthLoginSuccessfulEventHandler,
        email_sender=email_sender
    )




