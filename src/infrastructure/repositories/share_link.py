from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.files.interfaces import ShareLinkRepository
from src.domain.files.entity import ShareLink
from src.infrastructure.database.models.share_link import ShareLinkModel


class SqlAlchemyShareLinkRepository(ShareLinkRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: ShareLinkModel) -> ShareLink:
        return ShareLink(
            id=model.id,
            file_id=model.file_id,
            user_id=model.user_id,
            token=model.token,
            expires_at=model.expires_at,
            is_disabled=model.is_disabled,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: ShareLink) -> ShareLinkModel:
        return ShareLinkModel(
            id=entity.id,
            file_id=entity.file_id,
            user_id=entity.user_id,
            token=entity.token,
            expires_at=entity.expires_at,
            is_disabled=entity.is_disabled,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def save(self, share_link: ShareLink) -> ShareLink:
        model = self._to_model(share_link)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_token(self, token: str) -> Optional[ShareLink]:
        result = await self.session.execute(select(ShareLinkModel).where(ShareLinkModel.token == token))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_id(self, share_link_id: UUID) -> Optional[ShareLink]:
        result = await self.session.execute(select(ShareLinkModel).where(ShareLinkModel.id == share_link_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_file(self, file_id: UUID) -> List[ShareLink]:
        result = await self.session.execute(select(ShareLinkModel).where(ShareLinkModel.file_id == file_id))
        return [self._to_entity(m) for m in result.scalars().all()]

    async def disable(self, share_link_id: UUID) -> None:
        await self.session.execute(
            update(ShareLinkModel)
            .where(ShareLinkModel.id == share_link_id)
            .values(is_disabled=True)
        )
