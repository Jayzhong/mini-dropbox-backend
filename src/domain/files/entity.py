from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

@dataclass
class Folder:
    """
    Domain Entity representing a Folder.
    """
    id: UUID
    user_id: UUID
    name: str
    parent_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

@dataclass
class File:
    """
    Domain Entity representing a File.
    """
    id: UUID
    user_id: UUID
    folder_id: UUID
    name: str
    size_bytes: int
    mime_type: str
    storage_key: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


@dataclass
class ShareLink:
    """
    Domain Entity representing a public, read-only share link for a file.
    """
    id: UUID
    file_id: UUID
    user_id: UUID
    token: str
    expires_at: Optional[datetime]
    is_disabled: bool
    created_at: datetime
    updated_at: datetime
