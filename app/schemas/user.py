"""User schema module."""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr

    @validator('email')
    def email_must_be_valid(cls, v: str) -> str:
        """Validate email format."""
        if not v:
            raise ValueError('Email must not be empty')
        return v

class UserCreate(UserBase):
    """User creation schema."""
    password: str
    role: Optional[str] = "user"

    @validator('password')
    def password_must_be_strong(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

    @validator('role')
    def role_must_be_valid(cls, v: str) -> str:
        """Validate user role."""
        valid_roles = ["user", "admin"]
        if v not in valid_roles:
            raise ValueError('Role must be either user or admin')
        return v

class User(UserBase):
    """User response schema."""
    id: int
    role: str

    class Config:
        """Pydantic config."""
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str 