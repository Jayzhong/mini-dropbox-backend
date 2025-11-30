from dataclasses import dataclass
from uuid import UUID
from datetime import datetime

@dataclass
class User:
    """
    Domain Entity representing a User.
    Pure Python, no database models or ORM logic.
    """
    id: UUID
    email: str
    password_hash: str
    created_at: datetime
    updated_at: datetime
