"""User schema module."""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional

class User(BaseModel):
    username:str
    email:str
    password:str
    role: Optional[str] = "user"  # Default to "user" if not specified
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('role')
    def validate_role(cls, v):
        if v and v.lower() not in ['admin', 'user']:
            raise ValueError('Role must be either "admin" or "user"')
        return v.lower() if v else "user"

class Login(BaseModel):
    username:str
    password:str


class Token(BaseModel):
    access_token: str
    token_type: str 

class TokenData(BaseModel):
    username:Optional[str]=None