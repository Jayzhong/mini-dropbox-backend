from typing import Protocol, BinaryIO, Optional, List
from uuid import UUID
from src.domain.files.entity import Folder, File, ShareLink

class StorageService(Protocol):
    """
    Abstract interface for Blob Storage operations.
    """
    async def upload_file(self, key: str, data: BinaryIO, content_type: str) -> None:
        """Uploads a file-like object to storage."""
        ...

    async def download_file(self, key: str) -> str:
        """Returns a presigned URL for downloading the file."""
        ...

    async def delete_file(self, key: str) -> None:
        """Deletes a file from storage."""
        ...

class FolderRepository(Protocol):
    """
    Abstract interface for Folder data access.
    """
    async def save(self, folder: Folder) -> Folder:
        ...

    async def get_by_id(self, folder_id: UUID) -> Optional[Folder]:
        ...

    async def list_by_parent(self, user_id: UUID, parent_id: Optional[UUID]) -> List[Folder]:
        ...

class FileRepository(Protocol):
    """
    Abstract interface for File data access.
    """
    async def save(self, file: File) -> File:
        ...

    async def get_by_id(self, file_id: UUID) -> Optional[File]:
        ...

    async def list_by_folder(self, user_id: UUID, folder_id: Optional[UUID]) -> List[File]:
        ...

class ShareLinkRepository(Protocol):
    """
    Abstract interface for ShareLink data access.
    """
    async def save(self, share_link: ShareLink) -> ShareLink:
        ...

    async def get_by_token(self, token: str) -> Optional[ShareLink]:
        ...

    async def get_by_id(self, share_link_id: UUID) -> Optional[ShareLink]:
        ...

    async def list_by_file(self, file_id: UUID) -> List[ShareLink]:
        ...

    async def disable(self, share_link_id: UUID) -> None:
        ...
