from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.main import get_db_session
from src.infrastructure.repositories.system import SqlAlchemySystemRepository
from src.application.system.interfaces import SystemRepository
from src.application.system.use_cases import GetSystemHealthUseCase

# 1. Inject Session into Repo Implementation
def get_system_repo(
    session: AsyncSession = Depends(get_db_session)
) -> SystemRepository:
    return SqlAlchemySystemRepository(session)

# 2. Inject Repo Interface into Use Case
def get_health_use_case(
    repo: SystemRepository = Depends(get_system_repo)
) -> GetSystemHealthUseCase:
    return GetSystemHealthUseCase(repo)
