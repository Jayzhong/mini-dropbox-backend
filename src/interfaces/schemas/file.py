from datetime import datetime
from typing import Optional, List, Literal
from uuid import UUID
from pydantic import BaseModel, Field

# --- Request Schemas ---

class CreateFolderRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    parent_id: Optional[UUID] = Field(None, description="ID of the parent folder. Null for root folder.")

class UploadFileRequest(BaseModel):
    # This Pydantic model will be used for validation of metadata.
    # The actual file content will be handled by FastAPI's UploadFile.
    name: str = Field(..., min_length=1, max_length=255)
    folder_id: UUID
    mime_type: str = Field(..., min_length=1)


# --- Response Schemas ---

class FolderResponse(BaseModel):
    id: UUID
    name: str
    parent_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }

class FileResponse(BaseModel):
    id: UUID
    name: str
    folder_id: UUID
    user_id: UUID
    size_bytes: int
    mime_type: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }

class ListContentResponse(BaseModel):
    folders: List[FolderResponse] = Field(default_factory=list)
    files: List[FileResponse] = Field(default_factory=list)

# --- Share Links ---

class CreateShareLinkRequest(BaseModel):
    file_id: UUID
    expires_at: Optional[datetime] = Field(None, description="Optional expiration timestamp")

class ShareLinkResponse(BaseModel):
    id: UUID
    file_id: UUID
    token: str
    expires_at: Optional[datetime]
    is_disabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class AccessShareLinkResponse(BaseModel):
    download_url: str
