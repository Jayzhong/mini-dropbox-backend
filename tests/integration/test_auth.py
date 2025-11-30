import pytest
import uuid
import jwt
from httpx import AsyncClient
from sqlalchemy import text # Still needed if we want to assert direct DB state after app interaction
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.config.settings import settings

@pytest.mark.asyncio
async def test_register_user_flow(async_client: AsyncClient, db_session: AsyncSession):
    """
    Integration test for User Registration Flow:
    1. Register valid user -> 201 Created
    2. Register same user again -> 409 Conflict
    """
    
    # Generate a unique email for this test run
    unique_email = f"test_user_{uuid.uuid4()}@example.com"
    password = "SecurePassword123!"

    payload = {
        "email": unique_email,
        "password": password
    }

    # 1. Successful Registration
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    
    data = response.json()
    assert data["email"] == unique_email
    assert "id" in data
    assert "password" not in data # Security check: password should not be returned
    assert "password_hash" not in data

    user_id = data["id"] # Keep this for potential future assertions or debugging

    # 2. Duplicate Registration
    response_duplicate = await async_client.post("/api/v1/auth/register", json=payload)
    assert response_duplicate.status_code == 409
    assert "already exists" in response_duplicate.json()["detail"]

    # No manual cleanup needed due to transactional test fixture (db_session rollback)

@pytest.mark.asyncio
async def test_login_user_flow(async_client: AsyncClient, db_session: AsyncSession):
    """
    Integration test for User Login Flow:
    1. Register a user.
    2. Login with correct credentials -> 200 OK, valid token.
    3. Login with incorrect password -> 401 Unauthorized.
    4. Login with non-existent user -> 401 Unauthorized.
    """
    unique_email = f"login_test_{uuid.uuid4()}@example.com"
    password = "SuperSecretPassword123!"

    # 1. Register a user first (via API call)
    register_payload = {
        "email": unique_email,
        "password": password
    }
    register_response = await async_client.post("/api/v1/auth/register", json=register_payload)
    assert register_response.status_code == 201
    registered_user_id = register_response.json()["id"]

    login_payload = {
        "email": unique_email,
        "password": password
    }

    # 2. Login with correct credentials
    login_response = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert login_response.status_code == 200, f"Expected 200, got {login_response.status_code}: {login_response.text}"
    
    token_data = login_response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    # Verify the token
    decoded_token = jwt.decode(
        token_data["access_token"], 
        settings.SECRET_KEY, 
        algorithms=[settings.ALGORITHM]
    )
    assert decoded_token["sub"] == registered_user_id
    assert decoded_token["email"] == unique_email
    assert "exp" in decoded_token


    # 3. Login with incorrect password
    incorrect_password_payload = {
        "email": unique_email,
        "password": "WrongPassword123!"
    }
    wrong_pass_response = await async_client.post("/api/v1/auth/login", json=incorrect_password_payload)
    assert wrong_pass_response.status_code == 401
    assert "Incorrect email or password" in wrong_pass_response.json()["detail"]

    # 4. Login with non-existent user
    non_existent_user_payload = {
        "email": f"non_existent_{uuid.uuid4()}@example.com",
        "password": "AnyPassword!"
    }
    non_existent_response = await async_client.post("/api/v1/auth/login", json=non_existent_user_payload)
    assert non_existent_response.status_code == 401
    assert "Incorrect email or password" in non_existent_response.json()["detail"]

    # No manual cleanup needed due to transactional test fixture (db_session rollback)
