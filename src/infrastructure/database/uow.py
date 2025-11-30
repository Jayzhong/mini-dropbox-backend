from sqlalchemy.ext.asyncio import AsyncSession
from src.application.common.interfaces import UnitOfWork

class SqlAlchemyUnitOfWork(UnitOfWork):
    """
    Implementation of UnitOfWork using SQLAlchemy AsyncSession.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
