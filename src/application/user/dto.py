from dataclasses import dataclass
from datetime import datetime

@dataclass
class RegisterUserInputDTO:
    """Input DTO for the RegisterUserUseCase."""
    email: str
    password: str

@dataclass
class LoginUserInputDTO:
    """Input DTO for the LoginUserUseCase."""
    email: str
    password: str

@dataclass
class UserOutputDTO:
    """Output DTO for User-related operations."""
    id: str # UUID will be converted to string for DTO
    email: str
    created_at: datetime
    updated_at: datetime

@dataclass
class TokenOutputDTO:
    """Output DTO for authentication tokens."""
    access_token: str
    token_type: str = "bearer"