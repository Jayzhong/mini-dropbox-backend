from passlib.context import CryptContext
from src.application.common.interfaces import PasswordHasher

# Switch to Argon2
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class Argon2PasswordHasher(PasswordHasher):
    """
    Implementation of the PasswordHasher interface using Argon2 (via passlib).
    """
    async def hash(self, password: str) -> str:
        return pwd_context.hash(password)

    async def verify(self, password: str, hashed_password: str) -> bool:
        return pwd_context.verify(password, hashed_password)