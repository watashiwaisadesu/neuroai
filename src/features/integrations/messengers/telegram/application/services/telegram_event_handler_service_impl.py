from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from datetime import timezone
from typing import Any, Optional
from uuid import UUID

from src.core.mediator.mediator import Mediator
from src.features.bot.exceptions.bot_exceptions import BotNotFoundError
from src.features.conversation.api.v1.dtos.process_incoming_message_dto import ProcessIncomingMessageResponseDTO
from src.features.conversation.domain.enums import ChatPlatform
from src.features.conversation.domain.exceptions.chat_exceptions import ConversationProcessingError
from src.features.conversation.domain.services.process_incoming_message_command import ProcessIncomingMessageCommand
from src.features.integrations.messengers.telegram.application.services.telegram_event_handler_service import \
    TelegramEventHandlerService
from src.features.integrations.messengers.telegram.application.services.telethon_client_service import \
    TelethonClientService




class TelegramEventHandlerServiceHandler(TelegramEventHandlerService):
    _mediator: Mediator
    _telethon_service: TelethonClientService

    def __init__(
        self,
        telethon_service: TelethonClientService,
        mediator: Mediator,
    ):
        self._telethon_service = telethon_service
        self._mediator = mediator
        logger.debug("TelegramEventHandlerServiceImpl initialized.")

    async def handle_new_telethon_message(
        self,
        event: Any,  # telethon.events.NewMessage.Event
        telethon_client_instance: Any,  # TelethonClient instance
        associated_bot_uid: UUID,  # BotEntity UID
        service_uid: UUID,  # BotServiceEntity UID
    ):
        try:
            # Validate event type
            if not (hasattr(event, "is_private") and hasattr(event, "is_group")):
                logger.warning(f"Unexpected event type: {type(event)}")
                return

            if not event.is_private and not event.is_group:
                logger.debug(f"Ignoring non-private/group message ID {getattr(event, 'id', 'N/A')}.")
                return

            message_text = getattr(event, "raw_text", None)
            if not message_text:
                logger.debug(f"Ignoring message ID {getattr(event, 'id', 'N/A')} with no text.")
                return

            if not event.sender_id:
                logger.error(f"Message ID {getattr(event, 'id', 'N/A')} has no sender_id.")
                return

            sender_id_tele = str(event.sender_id)
            sender_nickname: Optional[str] = None
            sender_phone: Optional[str] = None

            try:
                sender_entity = await event.get_sender()
                if sender_entity:
                    sender_nickname = getattr(sender_entity, "username", None)
                    sender_phone = getattr(sender_entity, "phone", None)
            except Exception as e_get_sender:
                logger.warning(f"Error getting sender info for sender ID {sender_id_tele}: {e_get_sender}")

            me = await telethon_client_instance.get_me()
            if not me:
                logger.error("Could not determine 'me' (bot's own TG account). Cannot process.")
                return
            our_bot_telegram_user_id = str(me.id)

            logger.info(
                f"Telegram Handler (Bot: {associated_bot_uid}, Service: {service_uid}, TG Account: {our_bot_telegram_user_id}): "
                f"Msg from sender {sender_id_tele} ('{sender_nickname or 'ID_ONLY'}'): '{message_text[:50]}...'"
            )

            message_timestamp = event.message.date
            if message_timestamp.tzinfo is None:
                message_timestamp = message_timestamp.replace(tzinfo=timezone.utc)
            else:
                message_timestamp = message_timestamp.astimezone(timezone.utc)

            # Create the command to send via mediator
            command = ProcessIncomingMessageCommand(
                platform=ChatPlatform.TELEGRAM,
                sender_id=sender_id_tele,
                bot_uid=associated_bot_uid,
                content=message_text,
                timestamp=message_timestamp,
                sender_nickname=sender_nickname,
                sender_number=sender_phone,
            )

            response_data: ProcessIncomingMessageResponseDTO = await self._mediator.execute(command)

            # Reply to the Telegram message if AI response generated
            if response_data.ai_response_generated and response_data.ai_response_content:
                await event.reply(response_data.ai_response_content)
            elif response_data.message:
                await event.reply(response_data.message)
            elif response_data.ai_response_generated and not response_data.ai_response_content:
                logger.warning(
                    f"AI response generated but content missing. Msg UID: {response_data.ai_message_uid}"
                )

            logger.debug(f"Message from {sender_id_tele} dispatched via mediator.")

        except (ConversationProcessingError, BotNotFoundError) as core_processing_error:
            logger.error(f"Core processing error for sender {sender_id_tele}: {core_processing_error}", exc_info=True)
            await event.reply("I'm having a little trouble processing that. Please try again soon.")
        except Exception as unexpected_error:
            logger.error(f"Unexpected error for sender {sender_id_tele}: {unexpected_error}", exc_info=True)
            await event.reply("An unexpected error occurred. Our team has been notified.")
        except Exception as outer_e:
            logger.error(f"Critical outer error for sender {getattr(event, 'sender_id', 'Unknown')}: {outer_e}", exc_info=True)
