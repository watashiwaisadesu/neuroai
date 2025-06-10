import pytest
from httpx import AsyncClient
from httpx import ASGITransport

from src.features.auth.dependencies import get_register_user_use_case
from src.main import app

@pytest.fixture
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

@pytest.fixture
def override_register_user_use_case(mocker):
    mock_use_case = mocker.AsyncMock()
    app.dependency_overrides[get_register_user_use_case] = lambda: mock_use_case
    return mock_use_case