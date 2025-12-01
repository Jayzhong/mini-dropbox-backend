import pytest
from httpx import AsyncClient
from uuid import UUID

# --- Helper to get Auth Header ---
async def get_auth_header(client: AsyncClient, email: str, password: str):
    # Register first
    await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    # Login
    response = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_create_and_list_folders(async_client: AsyncClient):
    # 1. Setup User
    headers = await get_auth_header(async_client, "folder_user@example.com", "securePass123")
    
    # 2. Create Root Folder
    response = await async_client.post(
        "/api/v1/folders",
        json={"name": "My Documents"},
        headers=headers
    )
    assert response.status_code == 201
    root_folder = response.json()
    assert root_folder["name"] == "My Documents"
    assert root_folder["parent_id"] is None
    root_id = root_folder["id"]

    # 3. Create Child Folder
    response = await async_client.post(
        "/api/v1/folders",
        json={"name": "Work", "parent_id": root_id},
        headers=headers
    )
    assert response.status_code == 201
    child_folder = response.json()
    assert child_folder["name"] == "Work"
    assert child_folder["parent_id"] == root_id

    # 4. List Root Content
    response = await async_client.get("/api/v1/folders/root/content", headers=headers)
    assert response.status_code == 200
    content = response.json()
    # Should verify "My Documents" is in root listing
    assert any(f["id"] == root_id for f in content["folders"])

    # 5. List Child Folder Content
    response = await async_client.get(f"/api/v1/folders/{root_id}/content", headers=headers)
    assert response.status_code == 200
    content = response.json()
    assert len(content["folders"]) == 1
    assert content["folders"][0]["id"] == child_folder["id"]


@pytest.mark.asyncio
async def test_create_duplicate_folder_fails(async_client: AsyncClient):
    headers = await get_auth_header(async_client, "dup_user@example.com", "securePass123")
    
    # Create first time
    await async_client.post("/api/v1/folders", json={"name": "Photos"}, headers=headers)
    
    # Create second time
    response = await async_client.post("/api/v1/folders", json={"name": "Photos"}, headers=headers)
    assert response.status_code == 409 # Conflict


@pytest.mark.asyncio
async def test_user_isolation_folders(async_client: AsyncClient):
    # User 1
    headers1 = await get_auth_header(async_client, "u1@example.com", "pass1")
    resp1 = await async_client.post("/api/v1/folders", json={"name": "Secret"}, headers=headers1)
    folder_id = resp1.json()["id"]

    # User 2
    headers2 = await get_auth_header(async_client, "u2@example.com", "pass2")
    
    # User 2 tries to access User 1's folder
    response = await async_client.get(f"/api/v1/folders/{folder_id}/content", headers=headers2)
    assert response.status_code == 404 # Not Found (hidden)


@pytest.mark.asyncio
async def test_folder_listing_includes_files(async_client: AsyncClient):
    """
    Regression: ensure files appear in folder content listings (guards against missing FileResponse import).
    """
    headers = await get_auth_header(async_client, "list_files_user@example.com", "pw")

    # Create folder
    folder_resp = await async_client.post("/api/v1/folders", json={"name": "Docs"}, headers=headers)
    folder_id = folder_resp.json()["id"]

    # Upload file into folder
    files = {"file": ("note.txt", b"abc123", "text/plain")}
    upload_resp = await async_client.post(f"/api/v1/files?folder_id={folder_id}", files=files, headers=headers)
    assert upload_resp.status_code == 201
    file_id = upload_resp.json()["id"]

    # List folder content and ensure file is present
    list_resp = await async_client.get(f"/api/v1/folders/{folder_id}/content", headers=headers)
    assert list_resp.status_code == 200
    payload = list_resp.json()
    assert "files" in payload
    assert any(f["id"] == file_id for f in payload["files"])
