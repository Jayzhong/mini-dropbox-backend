import pytest
from httpx import AsyncClient

# --- Helper (Duplicated for simplicity, usually in conftest or util) ---
async def get_auth_header(client: AsyncClient, email: str, password: str):
    await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    response = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_upload_and_download_file(async_client: AsyncClient):
    headers = await get_auth_header(async_client, "file_user@example.com", "pass123")

    # 1. Create a Folder
    folder_resp = await async_client.post("/api/v1/folders", json={"name": "Uploads"}, headers=headers)
    folder_id = folder_resp.json()["id"]

    # 2. Upload File
    file_content = b"Hello, Dropbox!"
    files = {'file': ('hello.txt', file_content, 'text/plain')}
    
    response = await async_client.post(
        f"/api/v1/files?folder_id={folder_id}",
        files=files,
        headers=headers
    )
    assert response.status_code == 201
    file_data = response.json()
    assert file_data["name"] == "hello.txt"
    assert file_data["size_bytes"] == len(file_content)
    file_id = file_data["id"]

    # 3. List Folder Content (Verify file is listed)
    response = await async_client.get(f"/api/v1/folders/{folder_id}/content", headers=headers)
    content = response.json()
    assert len(content["files"]) == 1
    assert content["files"][0]["id"] == file_id

    # 4. Download File (Get Presigned URL)
    response = await async_client.get(f"/api/v1/files/{file_id}/download", headers=headers, follow_redirects=False)
    assert response.status_code == 302
    redirect_url = response.headers["location"]
    assert "minio" in redirect_url or "localhost" in redirect_url # Verify it points to storage


@pytest.mark.asyncio
async def test_user_isolation_files(async_client: AsyncClient):
    # User 1 Uploads
    headers1 = await get_auth_header(async_client, "u1_files@example.com", "pass")
    f_resp = await async_client.post("/api/v1/folders", json={"name": "Private"}, headers=headers1)
    folder_id = f_resp.json()["id"]
    
    files = {'file': ('secret.txt', b'secret', 'text/plain')}
    upload_resp = await async_client.post(f"/api/v1/files?folder_id={folder_id}", files=files, headers=headers1)
    file_id = upload_resp.json()["id"]

    # User 2 Tries to Download
    headers2 = await get_auth_header(async_client, "u2_files@example.com", "pass")
    response = await async_client.get(f"/api/v1/files/{file_id}/download", headers=headers2)
    assert response.status_code == 404
