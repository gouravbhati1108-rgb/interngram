import pytest
from httpx import AsyncClient

from app.core.security import hash_password
from app.models import Student, User
from app.models.user import UserRole


@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient, db_session):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "new@test.com", "password": "TestPass123!", "role": "student", "name": "Test User"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "new@test.com"
    assert data["role"] == "student"

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "new@test.com", "password": "TestPass123!"},
    )
    assert login.status_code == 200
    assert "access_token" in login.json()


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
