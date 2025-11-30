from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# Infrastructure
from src.infrastructure.database.main import get_db_session
from src.infrastructure.database.uow import SqlAlchemyUnitOfWork
from src.infrastructure.repositories.system import SqlAlchemySystemRepository
from src.infrastructure.repositories.user import SqlAlchemyUserRepository
from src.infrastructure.services.security import Argon2PasswordHasher
from src.infrastructure.services.auth import JwtTokenService

# Application - Interfaces
from src.application.common.interfaces import UserRepository, PasswordHasher, UnitOfWork, TokenService
from src.application.system.interfaces import SystemRepository # Re-importing for clarity

# Application - Use Cases
from src.application.system.use_cases import GetSystemHealthUseCase
from src.application.user.use_cases import RegisterUserUseCase, LoginUserUseCase


# --- System Dependencies ---
def get_system_repo(
    session: AsyncSession = Depends(get_db_session)
) -> SystemRepository:
    return SqlAlchemySystemRepository(session)

def get_health_use_case(
    repo: SystemRepository = Depends(get_system_repo)
) -> GetSystemHealthUseCase:
    return GetSystemHealthUseCase(repo)

# --- User Dependencies ---
def get_password_hasher() -> PasswordHasher:
    return Argon2PasswordHasher()

def get_uow(
    session: AsyncSession = Depends(get_db_session)
) -> UnitOfWork:
    return SqlAlchemyUnitOfWork(session)

def get_user_repo(
    session: AsyncSession = Depends(get_db_session)
) -> UserRepository:
    return SqlAlchemyUserRepository(session)

def get_token_service() -> TokenService:
    return JwtTokenService()

def get_register_user_use_case(
    user_repo: UserRepository = Depends(get_user_repo),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    uow: UnitOfWork = Depends(get_uow)
) -> RegisterUserUseCase:
    return RegisterUserUseCase(user_repo, password_hasher, uow)

def get_login_user_use_case(
    user_repo: UserRepository = Depends(get_user_repo),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    token_service: TokenService = Depends(get_token_service),
    uow: UnitOfWork = Depends(get_uow) # Login is a read, but for consistency we provide UoW
) -> LoginUserUseCase:
    return LoginUserUseCase(user_repo, password_hasher, token_service, uow)
