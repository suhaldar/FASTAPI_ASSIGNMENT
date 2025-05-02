"""Database configuration module."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from typing import Generator

SQLALCHEMY_DATABASE_URL = "sqlite:///./parking_system.db"

try:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

except SQLAlchemyError as e:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Database connection error: {str(e)}"
    ) from e

Base = declarative_base()

def get_db() -> Generator:
    """
    Get database session.
    
    Yields:
        Database session
    
    Raises:
        HTTPException: If database error occurs
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        ) from e
    finally:
        db.close() 