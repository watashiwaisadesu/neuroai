# src/features/chat/application/commands/process_incoming_message/process_incoming_message_command_impl.py

from src.infra.logging.setup_async_logging import async_logger
logger = async_logger
from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime, timezone
from uuid import uuid4

from src.core.base.command import BaseCommandHandler
from src.core.mediator.mediator import Mediator
from src.features.conversation.api.v1.dtos.process_incoming_message_dto import ProcessIncomingMessageResponseDTO
from src.features.bot.domain.entities.bot_entity import BotEntity
from src.features.conversation.domain.entities.conversation_entity import ConversationEntity
from src.features.conversation.domain.entities.message_entity import MessageEntity
from src.features.conversation.domain.enums import MessageRole
from src.features.conversation.domain.services.process_incoming_message_command import ProcessIncomingMessageCommand
from src.features.conversation.domain.uow.chat_unit_of_work import ConversationUnitOfWork
from src.features.generation.application.services.generation_service import IGenerationService
from src.features.bot.exceptions.bot_exceptions import BotNotFoundError
from src.features.conversation.domain.exceptions.chat_exceptions import ConversationProcessingError
from src.features.conversation.infra.services.helpers import _get_or_create_conversation
from src.features.conversation.domain.services.bot_lookup_service import BotLookupService





@dataclass(kw_only=True)
class ProcessIncomingMessageCommandHandler(
    BaseCommandHandler[ProcessIncomingMessageCommand, ProcessIncomingMessageResponseDTO]
):
    chat_uow: ConversationUnitOfWork
    bot_lookup_service: BotLookupService
    available_generation_services: Dict[str, IGenerationService]
    _mediator: Mediator

    async def __call__(
        self, command: ProcessIncomingMessageCommand
    ) -> ProcessIncomingMessageResponseDTO:
        logger.info(
            f"Processing incoming message for bot {command.bot_uid} on platform {command.platform.value} from sender {command.sender_id}"
        )
        bot: BotEntity
        conversation: ConversationEntity
        user_message_entity: MessageEntity
        ai_message_entity: Optional[MessageEntity] = None
        ai_response_generated = False
        ai_response_content: Optional[str] = None

        try:
            bot = await self.bot_lookup_service.get_bot(command.bot_uid)
            logger.debug(f"Found bot details: Name='{bot.name}', Owner='{bot.user_uid}'")
            conversation_owner_uid = bot.user_uid

            async with self.chat_uow:
                conversation = await _get_or_create_conversation(
                    self.chat_uow, command.platform, command.sender_id, command.bot_uid,
                    conversation_owner_uid, bot.name, command.sender_number, command.sender_nickname
                )

                # Create and persist user message
                user_message_entity = MessageEntity(
                    uid=uuid4(),
                    role=MessageRole.USER,
                    content=command.content,
                    timestamp=command.timestamp
                )

                # Add message to conversation entity (for in-memory state)
                conversation.add_message(user_message_entity)

                # Persist user message to database
                user_message_entity = await self.chat_uow.message_repository.create(
                    user_message_entity, conversation.uid
                )
                logger.debug(f"User message {user_message_entity.uid} persisted to database")

                should_generate_response = True
                if "help" in command.content.lower():
                    should_generate_response = False
                logger.debug(f"Should generate AI response: {should_generate_response}")

                if should_generate_response:
                    model_type_key = getattr(bot.ai_settings, 'generation_model', 'stub')
                    generation_service = self.available_generation_services.get(model_type_key)

                    if not generation_service:
                        msg = f"Generation service for '{model_type_key}' not available for bot {bot.uid}."
                        logger.error(msg)
                        raise ConversationProcessingError(msg)

                    message_history = [{"role": msg.role.value, "content": msg.content} for msg in conversation.messages]

                    logger.debug(f"Calling generation service {generation_service.__class__.__name__} for conversation {conversation.uid}")
                    ai_response_content = await generation_service.generate_response(
                        prompt_messages=message_history,
                        system_prompt=bot.ai_settings.instructions,
                        config=bot.ai_settings,
                        quota=bot.quota,
                        last_user_message=user_message_entity.content
                    )
                    logger.debug(f"Generation service returned: '{ai_response_content[:50]}...'")

                    if ai_response_content:
                        ai_response_generated = True
                        ai_message_entity = MessageEntity(
                            uid=uuid4(),
                            role=MessageRole.ASSISTANT,
                            content=ai_response_content,
                            timestamp=datetime.now(timezone.utc),
                        )
                        # Add AI message to conversation entity (for in-memory state)
                        conversation.add_message(ai_message_entity)

                        # Persist AI message to database
                        ai_message_entity = await self.chat_uow.message_repository.create(
                            ai_message_entity, conversation.uid
                        )
                    else:
                        logger.warning(f"Generation service returned empty content for conversation {conversation.uid}")
                else:
                    ai_response_content = "Connecting you to support."
                    ai_message_entity = MessageEntity(
                        role=MessageRole.ASSISTANT,
                        content=ai_response_content,
                        timestamp=datetime.now(timezone.utc),
                    )
                    conversation.add_message(ai_message_entity)
                    ai_message_entity = await self.chat_uow.message_repository.create(
                        ai_message_entity, conversation.uid
                    )
                    ai_response_generated = True

                await self.chat_uow.conversation_repository.update(conversation)
                logger.info(f"Conversation {conversation.uid} updated with new messages.")

            return ProcessIncomingMessageResponseDTO(
                conversation_uid=conversation.uid,
                user_message_uid=user_message_entity.uid,
                ai_response_generated=ai_response_generated,
                ai_message_uid=ai_message_entity.uid if ai_message_entity else None,
                ai_response_content=ai_message_entity.content if ai_message_entity else None,
                message="Message processed successfully."
            )

        except BotNotFoundError as e:
            logger.error(f"Processing failed: Bot not found - {e}")
            raise
        except ConversationProcessingError as e:
            logger.error(f"Processing failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unhandled error processing incoming message: {e}", exc_info=True)
            raise ConversationProcessingError(f"An unexpected error occurred: {e}") from e
