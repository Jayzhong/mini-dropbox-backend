from typing import Protocol, Optional
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