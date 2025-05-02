"""User model module."""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .. database import Base
import enum
from typing import Optional

class UserRole(str, enum.Enum):
    """Enum for user roles."""
    ADMIN = "admin"
    USER = "user"

class User(Base):
    """User model for database."""
    __tablename__ = "users"
    id: int = Column(Integer, primary_key=True, index=True)
    username: str = Column(String, unique=True, index=True)
    email: str = Column(String, unique=True, index=True)
    password: str = Column(String)
    role: Optional[str] = Column(String, default=UserRole.USER)
    
    # Relationships
    bookings = relationship("Booking", back_populates="user") 