from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.system.interfaces import SystemRepository
from src.domain.system.entity import SystemHealth

class SqlAlchemySystemRepository(SystemRepository):
    """
    Implementation of the SystemRepository using SQLAlchemy.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_system_health(self) -> SystemHealth:
        # Execute a raw SQL query to get the current time from DB
        result = await self.session.execute(text("SELECT now()"))
        db_time = result.scalar()
        
        # Map to Domain Entity
        return SystemHealth(database_time=db_time)
