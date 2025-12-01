from uuid import UUID
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

# Infrastructure
from src.infrastructure.database.main import get_db_session
from src.infrastructure.database.uow import SqlAlchemyUnitOfWork
from src.infrastructure.repositories.system import SqlAlchemySystemRepository
from src.infrastructure.repositories.user import SqlAlchemyUserRepository
from src.infrastructure.repositories.file import SqlAlchemyFolderRepository, SqlAlchemyFileRepository
from src.infrastructure.repositories.share_link import SqlAlchemyShareLinkRepository
from src.infrastructure.services.security import Argon2PasswordHasher
from src.infrastructure.services.auth import JwtTokenService
from src.infrastructure.services.storage import S3StorageService

# Application - Interfaces
from src.application.common.interfaces import UserRepository, PasswordHasher, UnitOfWork, TokenService
from src.application.system.interfaces import SystemRepository # Re-importing for clarity
from src.application.files.interfaces import FolderRepository, FileRepository, StorageService, ShareLinkRepository

# Application - Use Cases
from src.application.system.use_cases import GetSystemHealthUseCase
from src.application.user.use_cases import RegisterUserUseCase, LoginUserUseCase
from src.application.files.use_cases import (
    CreateFolderUseCase,
    ListFolderContentUseCase,
    UploadFileUseCase,
    DownloadFileUseCase,
    CreateShareLinkUseCase,
    DisableShareLinkUseCase,
    AccessShareLinkUseCase,
)

# Domain
from src.domain.user.entity import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

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


async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    token_service: TokenService = Depends(get_token_service),
    user_repo: UserRepository = Depends(get_user_repo),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Short-circuit if already set by a higher-level dependency
    cached_user = getattr(request.state, "current_user", None)
    if cached_user:
        return cached_user

    try:
        payload = token_service.decode_access_token(token)
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = UUID(user_id_str)
    except ValueError: # Catches errors from token_service.decode_access_token
        raise credentials_exception
    except Exception: # Catches UUID conversion errors
        raise credentials_exception

    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception

    # Cache on request state for downstream dependencies/handlers
    request.state.current_user = user
    return user


# --- File and Folder Dependencies ---
def get_folder_repo(
    session: AsyncSession = Depends(get_db_session)
) -> FolderRepository:
    return SqlAlchemyFolderRepository(session)

def get_file_repo(
    session: AsyncSession = Depends(get_db_session)
) -> FileRepository:
    return SqlAlchemyFileRepository(session)

def get_storage_service() -> StorageService:
    return S3StorageService()

def get_share_link_repo(
    session: AsyncSession = Depends(get_db_session)
) -> ShareLinkRepository:
    return SqlAlchemyShareLinkRepository(session)


def get_create_folder_use_case(
    folder_repo: FolderRepository = Depends(get_folder_repo),
    uow: UnitOfWork = Depends(get_uow)
) -> CreateFolderUseCase:
    return CreateFolderUseCase(folder_repo, uow)

def get_list_folder_content_use_case(
    folder_repo: FolderRepository = Depends(get_folder_repo),
    file_repo: FileRepository = Depends(get_file_repo)
) -> ListFolderContentUseCase:
    return ListFolderContentUseCase(folder_repo, file_repo)

def get_upload_file_use_case(
    file_repo: FileRepository = Depends(get_file_repo),
    folder_repo: FolderRepository = Depends(get_folder_repo),
    storage_service: StorageService = Depends(get_storage_service),
    uow: UnitOfWork = Depends(get_uow)
) -> UploadFileUseCase:
    return UploadFileUseCase(file_repo, folder_repo, storage_service, uow)

def get_download_file_use_case(
    file_repo: FileRepository = Depends(get_file_repo),
    storage_service: StorageService = Depends(get_storage_service)
) -> DownloadFileUseCase:
    return DownloadFileUseCase(file_repo, storage_service)

def get_create_share_link_use_case(
    file_repo: FileRepository = Depends(get_file_repo),
    share_repo: ShareLinkRepository = Depends(get_share_link_repo),
    uow: UnitOfWork = Depends(get_uow)
) -> CreateShareLinkUseCase:
    return CreateShareLinkUseCase(file_repo, share_repo, uow)

def get_disable_share_link_use_case(
    share_repo: ShareLinkRepository = Depends(get_share_link_repo),
    file_repo: FileRepository = Depends(get_file_repo),
    uow: UnitOfWork = Depends(get_uow)
) -> DisableShareLinkUseCase:
    return DisableShareLinkUseCase(share_repo, file_repo, uow)

def get_access_share_link_use_case(
    share_repo: ShareLinkRepository = Depends(get_share_link_repo),
    file_repo: FileRepository = Depends(get_file_repo),
    storage_service: StorageService = Depends(get_storage_service)
) -> AccessShareLinkUseCase:
    return AccessShareLinkUseCase(share_repo, file_repo, storage_service)
