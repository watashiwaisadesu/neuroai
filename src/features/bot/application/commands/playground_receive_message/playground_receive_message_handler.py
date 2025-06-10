from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass
from datetime import datetime, timezone

from src.core.mediator.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
from src.features.bot.application.commands.playground_receive_message.playground_receive_message_command import PlaygroundReceiveMessageCommand
from src.features.bot.application.commands.playground_send_message.playground_send_message_command import \
    PlaygroundSendMessageCommand
from src.features.bot.domain.entities.bot_entity import BotEntity
from src.features.conversation.api.v1.dtos.process_incoming_message_dto import ProcessIncomingMessageResponseDTO
from src.features.conversation.domain.enums import ChatPlatform
from src.features.conversation.domain.services.process_incoming_message_command import ProcessIncomingMessageCommand # This import is still needed for type hinting the command we'll dispatch




@dataclass
class PlaygroundReceiveMessageCommandHandler(
    BaseCommandHandler[PlaygroundReceiveMessageCommand, None]
):
    # _process_message_command: ProcessIncomingMessageCommand # This direct dependency is no longer needed
    _mediator: Mediator

    async def __call__(self, command: PlaygroundReceiveMessageCommand) -> None:
        logger.info(f"Processing PlaygroundReceiveMessageCommand for bot {command.bot_uid} from user {command.user_uid}")

        # Use the resolved target_bot_entity from the command
        target_bot: BotEntity = command.target_bot_entity

        try:
            # Create the ProcessIncomingMessageCommand
            # The ProcessIncomingMessageCommand itself needs to be a BaseCommand and have an associated handler
            # Assuming ProcessIncomingMessageCommand takes an input_dto directly or similar structure.
            process_chat_command = ProcessIncomingMessageCommand(
                platform=ChatPlatform.PLAYGROUND,
                sender_id=str(command.user_uid),
                bot_uid=target_bot.uid,
                content=command.message_content,
                timestamp=datetime.now(timezone.utc),
                sender_number=f"playground_{command.user_uid}",  # A unique identifier for playground user's "number"
                sender_nickname=f"Playground User {command.user_uid}"
                # Placeholder, ideally fetch user's real nickname/email
            )
            # Dispatch the ProcessIncomingMessageCommand via the mediator
            response_data: ProcessIncomingMessageResponseDTO = await self._mediator.execute(process_chat_command)

            message_to_send: str = ""
            if response_data.ai_response_generated and response_data.ai_response_content:
                message_to_send = response_data.ai_response_content
                logger.info(f"AI response generated for playground bot {command.bot_uid}. Dispatching send command.")
            elif not response_data.ai_response_generated and response_data.message:
                message_to_send = response_data.message
                logger.info(f"System message generated for playground bot {command.bot_uid}. Dispatching send command.")
            elif response_data.ai_response_generated and not response_data.ai_response_content:
                logger.warning(f"AI response was marked as generated but content is missing for bot {command.bot_uid}. UID: {response_data.ai_message_uid}")
                message_to_send = "An AI response was expected but no content was provided."
            else:
                logger.warning(f"No AI response or system message generated for bot {command.bot_uid}. Defaulting to generic message.")
                message_to_send = "I'm not sure how to respond to that."

            send_command = PlaygroundSendMessageCommand(
                websocket=command.websocket,
                message_content=message_to_send
            )
            await self._mediator.execute(send_command)

        except Exception as e:
            logger.error(f"Error processing PlaygroundReceiveMessageCommand for bot {command.bot_uid}: {e}", exc_info=True)
            error_send_command = PlaygroundSendMessageCommand(
                websocket=command.websocket,
                message_content=f"Error processing your request: {str(e)}"
            )
            await self._mediator.execute(error_send_command)