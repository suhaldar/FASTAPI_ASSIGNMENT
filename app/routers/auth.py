"""Authentication router module."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Dict

from ..database import get_db
from ..models import user as user_models
from ..schemas import user as user_schemas
from ..utils.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user
)

router = APIRouter()

@router.post("/register")
async def register_user(
    request: user_schemas.User,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    Args:
        request: User data for registration
        db: Database session
    
    Returns:
        Success message
    
    Raises:
        HTTPException: If username already exists
    """
    try:
        db_user = db.query(user_models.User).filter(
            user_models.User.username == request.username
        ).first()
        
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        hashed_password = get_password_hash(request.password)
        db_user = user_models.User(
            username=request.username,
            email=request.email,
            password=hashed_password,
            role=request.role
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return {"message": "User created successfully"}
    
    except HTTPException:
        # Re-raise HTTP exceptions as they are
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering user: {request.username}"
        ) from e

@router.post("/login", response_model=Dict[str, str])
def login(
    request: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Login user and return JWT token.
    
    Args:
        request: Login credentials
        db: Database session
    
    Returns:
        JWT access token
    
    Raises:
        HTTPException: If credentials are invalid
    """
    user = db.query(user_models.User).filter(
        user_models.User.username == request.username
    ).first()

    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

        
