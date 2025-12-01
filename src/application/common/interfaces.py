from typing import Protocol, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from src.domain.user.entity import User

class UnitOfWork(Protocol):
    """
    Abstract interface for Transaction Management.
    """
    async def commit(self) -> None:
        ...

    async def rollback(self) -> None:
        ...

class UserRepository(Protocol):
    """
    Abstract interface for User data access.
    """
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        ...

    async def get_by_email(self, email: str) -> Optional[User]:
        ...

    async def save(self, user: User) -> User:
        ...

class PasswordHasher(Protocol):
    """
    Abstract interface for password hashing operations.
    """
    async def hash(self, password: str) -> str:
        ...

    async def verify(self, password: str, hashed_password: str) -> bool:
        ...

class TokenService(Protocol):
    """
    Abstract interface for Token generation and validation.
    """
    def create_access_token(self, data: Dict[str, Any]) -> str:
        ...

    def decode_access_token(self, token: str) -> Dict[str, Any]:
        ...
