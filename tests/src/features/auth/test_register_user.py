from uuid import uuid4

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient


from src.features.auth.api.dtos.register_user_dto import RegisterUserReadDTO
from src.features.auth.dependencies import get_register_user_use_case
from src.main import app

@pytest.mark.anyio
async def test_register_user_success(async_client, override_register_user_use_case):
    # Arrange
    mock_user_id = uuid4()
    mock_response = RegisterUserReadDTO(
        uid=mock_user_id,
        email="test@example.com",
    )
    override_register_user_use_case.return_value = mock_response

    # Act
    payload = {
        "user_type": "individual",
        "email": "test@example.com",
        "password": "StrongPassword123"
    }
    response = await async_client.post("/auth/register", json=payload)

    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["email"] == "test@example.com"
    assert response.json()["uid"] == str(mock_user_id)

#
# @pytest.mark.anyio
# async def test_register_user_already_exists(mocker):
#     mock_use_case = mocker.AsyncMock()
#     mock_use_case.side_effect = UserAlreadyExistsError(message="User already exists.")
#
#     app.dependency_overrides[get_register_user_use_case] = lambda: mock_use_case
#
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         payload = {
#             "email": "test@example.com",
#             "password": "StrongPassword123",
#             "first_name": "Test",
#             "last_name": "User"
#         }
#         response = await ac.post("/register", json=payload)
#
#     assert response.status_code == status.HTTP_409_CONFLICT
#     assert response.json()["detail"] == "User already exists."
#
#     app.dependency_overrides.clear()
#
# @pytest.mark.anyio
# async def test_register_user_internal_server_error(mocker):
#     mock_use_case = mocker.AsyncMock()
#     mock_use_case.side_effect = Exception("Unexpected Error")
#
#     app.dependency_overrides[get_register_user_use_case] = lambda: mock_use_case
#
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         payload = {
#             "email": "test@example.com",
#             "password": "StrongPassword123",
#             "first_name": "Test",
#             "last_name": "User"
#         }
#         response = await ac.post("/register", json=payload)
#
#     assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
#
#     app.dependency_overrides.clear()
