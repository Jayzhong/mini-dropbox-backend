import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

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

    user_id = data["id"]

    # 2. Duplicate Registration
    response_duplicate = await async_client.post("/api/v1/auth/register", json=payload)
    assert response_duplicate.status_code == 409
    assert "already exists" in response_duplicate.json()["detail"]

    # Cleanup: Delete the created user to keep DB clean (best effort)
    # Note: In a real robust test suite, we might use a transaction rollback pattern or a dedicated test DB.
    await db_session.execute(
        text("DELETE FROM users WHERE id = :id"),
        {"id": user_id}
    )
    await db_session.commit()
