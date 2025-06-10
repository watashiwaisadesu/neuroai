# from fastapi import Depends, APIRouter
#
# from src.features.conversation.dependencies import get_process_incoming_message_use_case # Adjust this import path
#
# from src.features.conversation.api.dtos.process_incoming_message_dto import ProcessIncomingMessageInputDTO, \
#     ProcessIncomingMessageResponseDTO
# from src.features.conversation.domain.services.process_incoming_message_command import \
#     ProcessIncomingMessageCommand
#
# handle_message_test_router = APIRouter()
#
# @handle_message_test_router.post("/message", response_model=ProcessIncomingMessageResponseDTO)
# async def handle_message_http(
#     payload: ProcessIncomingMessageInputDTO,
#     use_case: ProcessIncomingMessageCommand = Depends(get_process_incoming_message_use_case)
# ):
#     """
#     Receives a user message, processes it, stores conversation turns,
#     and returns the AI's response.
#     """
#     response_dto = await use_case(payload)
#
#
#     return response_dto