from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from uuid import UUID

@dataclass
class CreateFolderInputDTO:
    user_id: UUID
    name: str
    parent_id: Optional[UUID] = None

@dataclass
class FolderResponseDTO:
    id: UUID
    name: str
    parent_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

@dataclass
class UploadFileInputDTO:
    user_id: UUID
    folder_id: UUID
    name: str
    size_bytes: int
    mime_type: str
    content: bytes # The actual file content

@dataclass
class FileResponseDTO:
    id: UUID
    name: str
    folder_id: UUID
    user_id: UUID
    size_bytes: int
    mime_type: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

@dataclass
class ListContentResponseDTO:
    folders: List[FolderResponseDTO]
    files: List[FileResponseDTO]

# --- Share Links ---

@dataclass
class CreateShareLinkInputDTO:
    user_id: UUID
    file_id: UUID
    expires_at: Optional[datetime] = None

@dataclass
class ShareLinkResponseDTO:
    id: UUID
    file_id: UUID
    token: str
    expires_at: Optional[datetime]
    is_disabled: bool
    created_at: datetime
    updated_at: datetime

@dataclass
class AccessShareLinkInputDTO:
    token: str
