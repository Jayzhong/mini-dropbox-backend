import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta, timezone


async def get_auth_header(client: AsyncClient, email: str, password: str):
    await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    response = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_and_access_share_link(async_client: AsyncClient):
    headers = await get_auth_header(async_client, "share_user@example.com", "pass123")

    # Create folder and upload file
    folder_resp = await async_client.post("/api/v1/folders", json={"name": "Public"}, headers=headers)
    folder_id = folder_resp.json()["id"]
    files = {"file": ("hello.txt", b"hello", "text/plain")}
    upload_resp = await async_client.post(f"/api/v1/files?folder_id={folder_id}", files=files, headers=headers)
    file_id = upload_resp.json()["id"]

    # Create share link
    create_resp = await async_client.post(
        "/api/v1/share-links",
        json={"file_id": file_id},
        headers=headers,
    )
    assert create_resp.status_code == 201
    token = create_resp.json()["token"]

    # Access publicly (no auth) expect redirect to presigned URL
    access_resp = await async_client.get(f"/api/v1/public/share/{token}", follow_redirects=False)
    assert access_resp.status_code == 302
    assert "location" in access_resp.headers
    assert "http" in access_resp.headers["location"]


@pytest.mark.asyncio
async def test_disable_share_link(async_client: AsyncClient):
    headers = await get_auth_header(async_client, "share_user2@example.com", "pass123")

    # Upload a file
    folder_resp = await async_client.post("/api/v1/folders", json={"name": "Docs"}, headers=headers)
    folder_id = folder_resp.json()["id"]
    upload_resp = await async_client.post(
        f"/api/v1/files?folder_id={folder_id}",
        files={"file": ("note.txt", b"note", "text/plain")},
        headers=headers,
    )
    file_id = upload_resp.json()["id"]

    # Create share link
    create_resp = await async_client.post(
        "/api/v1/share-links",
        json={"file_id": file_id},
        headers=headers,
    )
    link_id = create_resp.json()["id"]
    token = create_resp.json()["token"]

    # Disable
    disable_resp = await async_client.post(f"/api/v1/share-links/{link_id}/disable", headers=headers)
    assert disable_resp.status_code == 204

    # Access should 404
    access_resp = await async_client.get(f"/api/v1/public/share/{token}", follow_redirects=False)
    assert access_resp.status_code == 404


@pytest.mark.asyncio
async def test_expired_share_link(async_client: AsyncClient):
    headers = await get_auth_header(async_client, "share_user3@example.com", "pass123")

    # Upload a file
    folder_resp = await async_client.post("/api/v1/folders", json={"name": "Pics"}, headers=headers)
    folder_id = folder_resp.json()["id"]
    upload_resp = await async_client.post(
        f"/api/v1/files?folder_id={folder_id}",
        files={"file": ("pic.jpg", b"data", "image/jpeg")},
        headers=headers,
    )
    file_id = upload_resp.json()["id"]

    expired_at = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()

    # Create expired share link
    create_resp = await async_client.post(
        "/api/v1/share-links",
        json={"file_id": file_id, "expires_at": expired_at},
        headers=headers,
    )
    token = create_resp.json()["token"]

    access_resp = await async_client.get(f"/api/v1/public/share/{token}", follow_redirects=False)
    assert access_resp.status_code == 404
