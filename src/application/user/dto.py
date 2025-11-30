from dataclasses import dataclass

@dataclass
class RegisterUserInputDTO:
    """Input DTO for the RegisterUserUseCase."""
    email: str
    password: str

@dataclass
class UserOutputDTO:
    """Output DTO for User-related operations."""
    id: str # UUID will be converted to string for DTO
    email: str
    created_at: datetime
    updated_at: datetime
