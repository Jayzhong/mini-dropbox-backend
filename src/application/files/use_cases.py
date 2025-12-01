from uuid import UUID, uuid4
from datetime import datetime, timezone
import secrets
from typing import Optional, List, BinaryIO
import io

from src.application.common.interfaces import UnitOfWork
from src.application.files.interfaces import FolderRepository, FileRepository, StorageService, ShareLinkRepository
from src.application.files.dto import (
    CreateFolderInputDTO, FolderResponseDTO,
    UploadFileInputDTO, FileResponseDTO,
    ListContentResponseDTO,
    CreateShareLinkInputDTO, ShareLinkResponseDTO, AccessShareLinkInputDTO
)
from src.domain.files.entity import Folder, File, ShareLink
from src.domain.files.exceptions import (
    FolderNotFound,
    FolderAlreadyExists,
    FileNotFound,
    ShareLinkNotFound,
    ShareLinkDisabled,
    ShareLinkExpired,
)


class CreateFolderUseCase:
    def __init__(
        self,
        folder_repo: FolderRepository,
        uow: UnitOfWork
    ):
        self.folder_repo = folder_repo
        self.uow = uow

    async def execute(self, input_dto: CreateFolderInputDTO) -> FolderResponseDTO:
        # Check if parent folder exists and belongs to the user
        if input_dto.parent_id:
            parent_folder = await self.folder_repo.get_by_id(input_dto.parent_id)
            if not parent_folder or parent_folder.user_id != input_dto.user_id:
                raise FolderNotFound("Parent folder not found or does not belong to user.")

        # Check for existing folder with same name in the same parent
        existing_folders = await self.folder_repo.list_by_parent(input_dto.user_id, input_dto.parent_id)
        for folder in existing_folders:
            if folder.name == input_dto.name:
                raise FolderAlreadyExists(f"Folder with name '{input_dto.name}' already exists in this location.")

        new_folder = Folder(
            id=uuid4(),
            user_id=input_dto.user_id,
            name=input_dto.name,
            parent_id=input_dto.parent_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            deleted_at=None
        )
        await self.folder_repo.save(new_folder)
        await self.uow.commit()
        return FolderResponseDTO(
            id=new_folder.id,
            name=new_folder.name,
            parent_id=new_folder.parent_id,
            created_at=new_folder.created_at,
            updated_at=new_folder.updated_at,
            deleted_at=new_folder.deleted_at
        )


class ListFolderContentUseCase:
    def __init__(
        self,
        folder_repo: FolderRepository,
        file_repo: FileRepository
    ):
        self.folder_repo = folder_repo
        self.file_repo = file_repo

    async def execute(self, user_id: UUID, folder_id: Optional[UUID]) -> ListContentResponseDTO:
        # Check if folder exists and belongs to user if folder_id is not None
        if folder_id:
            folder = await self.folder_repo.get_by_id(folder_id)
            if not folder or folder.user_id != user_id:
                raise FolderNotFound("Folder not found or does not belong to user.")

        folders = await self.folder_repo.list_by_parent(user_id, folder_id)
        files = await self.file_repo.list_by_folder(user_id, folder_id)

        folder_dtos = [
            FolderResponseDTO(
                id=f.id, name=f.name, parent_id=f.parent_id,
                created_at=f.created_at, updated_at=f.updated_at, deleted_at=f.deleted_at
            ) for f in folders
        ]
        file_dtos = [
            FileResponseDTO(
                id=f.id, name=f.name, folder_id=f.folder_id, user_id=f.user_id,
                size_bytes=f.size_bytes, mime_type=f.mime_type,
                created_at=f.created_at, updated_at=f.updated_at, deleted_at=f.deleted_at
            ) for f in files
        ]

        return ListContentResponseDTO(folders=folder_dtos, files=file_dtos)


class UploadFileUseCase:
    def __init__(
        self,
        file_repo: FileRepository,
        folder_repo: FolderRepository,
        storage_service: StorageService,
        uow: UnitOfWork
    ):
        self.file_repo = file_repo
        self.folder_repo = folder_repo
        self.storage_service = storage_service
        self.uow = uow

    async def execute(self, input_dto: UploadFileInputDTO) -> FileResponseDTO:
        # Check if folder exists and belongs to user
        folder = await self.folder_repo.get_by_id(input_dto.folder_id)
        if not folder or folder.user_id != input_dto.user_id:
            raise FolderNotFound("Destination folder not found or does not belong to user.")

        file_id = uuid4()
        storage_key = f"{input_dto.user_id}/{file_id}" # Simple storage key strategy

        # Upload to blob storage
        file_content_stream = io.BytesIO(input_dto.content) # Use BytesIO for file-like object
        await self.storage_service.upload_file(storage_key, file_content_stream, input_dto.mime_type)

        new_file = File(
            id=file_id,
            user_id=input_dto.user_id,
            folder_id=input_dto.folder_id,
            name=input_dto.name,
            size_bytes=input_dto.size_bytes,
            mime_type=input_dto.mime_type,
            storage_key=storage_key,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            deleted_at=None
        )
        await self.file_repo.save(new_file)
        await self.uow.commit()

        return FileResponseDTO(
            id=new_file.id,
            name=new_file.name,
            folder_id=new_file.folder_id,
            user_id=new_file.user_id,
            size_bytes=new_file.size_bytes,
            mime_type=new_file.mime_type,
            created_at=new_file.created_at,
            updated_at=new_file.updated_at,
            deleted_at=new_file.deleted_at
        )


class DownloadFileUseCase:
    def __init__(
        self,
        file_repo: FileRepository,
        storage_service: StorageService
    ):
        self.file_repo = file_repo
        self.storage_service = storage_service

    async def execute(self, user_id: UUID, file_id: UUID) -> str:
        # Check if file exists and belongs to user
        file = await self.file_repo.get_by_id(file_id)
        if not file or file.user_id != user_id:
            raise FileNotFound("File not found or does not belong to user.")

        # Return presigned URL
        presigned_url = await self.storage_service.download_file(file.storage_key)
        return presigned_url


class CreateShareLinkUseCase:
    def __init__(
        self,
        file_repo: FileRepository,
        share_repo: ShareLinkRepository,
        uow: UnitOfWork
    ):
        self.file_repo = file_repo
        self.share_repo = share_repo
        self.uow = uow

    async def execute(self, input_dto: CreateShareLinkInputDTO) -> ShareLinkResponseDTO:
        file = await self.file_repo.get_by_id(input_dto.file_id)
        if not file or file.user_id != input_dto.user_id:
            raise FileNotFound("File not found or does not belong to user.")

        token = secrets.token_urlsafe(32)
        now = datetime.now(timezone.utc)
        new_share = ShareLink(
            id=uuid4(),
            file_id=file.id,
            user_id=input_dto.user_id,
            token=token,
            expires_at=input_dto.expires_at,
            is_disabled=False,
            created_at=now,
            updated_at=now,
        )
        saved = await self.share_repo.save(new_share)
        await self.uow.commit()

        return ShareLinkResponseDTO(
            id=saved.id,
            file_id=saved.file_id,
            token=saved.token,
            expires_at=saved.expires_at,
            is_disabled=saved.is_disabled,
            created_at=saved.created_at,
            updated_at=saved.updated_at,
        )


class DisableShareLinkUseCase:
    def __init__(
        self,
        share_repo: ShareLinkRepository,
        file_repo: FileRepository,
        uow: UnitOfWork
    ):
        self.share_repo = share_repo
        self.file_repo = file_repo
        self.uow = uow

    async def execute(self, user_id: UUID, share_link_id: UUID) -> None:
        link = await self.share_repo.get_by_id(share_link_id)
        if not link:
            raise ShareLinkNotFound("Share link not found.")
        if link.user_id != user_id:
            raise ShareLinkNotFound("Share link not found.")  # hide existence

        await self.share_repo.disable(share_link_id)
        await self.uow.commit()


class AccessShareLinkUseCase:
    def __init__(
        self,
        share_repo: ShareLinkRepository,
        file_repo: FileRepository,
        storage_service: StorageService
    ):
        self.share_repo = share_repo
        self.file_repo = file_repo
        self.storage_service = storage_service

    async def execute(self, input_dto: AccessShareLinkInputDTO) -> str:
        link = await self.share_repo.get_by_token(input_dto.token)
        if not link:
            raise ShareLinkNotFound("Share link not found.")
        if link.is_disabled:
            raise ShareLinkDisabled("Share link disabled.")
        if link.expires_at and link.expires_at < datetime.now(timezone.utc):
            raise ShareLinkExpired("Share link expired.")

        file = await self.file_repo.get_by_id(link.file_id)
        if not file:
            raise FileNotFound("File not found.")

        return await self.storage_service.download_file(file.storage_key)
