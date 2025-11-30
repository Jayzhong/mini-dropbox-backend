from datetime import datetime
from pydantic import BaseModel, EmailStr
from uuid import UUID

class RegisterUserRequest(BaseModel):
    """
    Pydantic Schema for user registration request body.
    """
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    """
    Pydantic Schema for user login request body.
    """
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """
    Pydantic Schema for user response.
    """
    id: UUID
    email: EmailStr
    created_at: datetime
    updated_at: datetime

class TokenResponse(BaseModel):
    """
    Pydantic Schema for JWT token response.
    """
    access_token: str
    token_type: str