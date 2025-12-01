from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.files.interfaces import FolderRepository, FileRepository
from src.domain.files.entity import Folder, File
from src.infrastructure.database.models.file import FolderModel, FileModel

class SqlAlchemyFolderRepository(FolderRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: FolderModel) -> Folder:
        return Folder(
            id=model.id,
            user_id=model.user_id,
            name=model.name,
            parent_id=model.parent_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at
        )

    def _to_model(self, entity: Folder) -> FolderModel:
        return FolderModel(
            id=entity.id,
            user_id=entity.user_id,
            name=entity.name,
            parent_id=entity.parent_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at
        )

    async def save(self, folder: Folder) -> Folder:
        model = self._to_model(folder)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, folder_id: UUID) -> Optional[Folder]:
        result = await self.session.execute(select(FolderModel).where(FolderModel.id == folder_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_parent(self, user_id: UUID, parent_id: Optional[UUID]) -> List[Folder]:
        query = select(FolderModel).where(
            FolderModel.user_id == user_id,
            FolderModel.parent_id == parent_id,
            FolderModel.deleted_at.is_(None)
        )
        result = await self.session.execute(query)
        return [self._to_entity(m) for m in result.scalars().all()]


class SqlAlchemyFileRepository(FileRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: FileModel) -> File:
        return File(
            id=model.id,
            user_id=model.user_id,
            folder_id=model.folder_id,
            name=model.name,
            size_bytes=model.size_bytes,
            mime_type=model.mime_type,
            storage_key=model.storage_key,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at
        )

    def _to_model(self, entity: File) -> FileModel:
        return FileModel(
            id=entity.id,
            user_id=entity.user_id,
            folder_id=entity.folder_id,
            name=entity.name,
            size_bytes=entity.size_bytes,
            mime_type=entity.mime_type,
            storage_key=entity.storage_key,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at
        )

    async def save(self, file: File) -> File:
        model = self._to_model(file)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, file_id: UUID) -> Optional[File]:
        result = await self.session.execute(select(FileModel).where(FileModel.id == file_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_folder(self, user_id: UUID, folder_id: Optional[UUID]) -> List[File]:
        query = select(FileModel).where(
            FileModel.user_id == user_id,
            FileModel.folder_id == folder_id,
            FileModel.deleted_at.is_(None)
        )
        result = await self.session.execute(query)
        return [self._to_entity(m) for m in result.scalars().all()]
