from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import feedback as models
from ..schemas import feedback as schemas
from ..utils.security import get_current_user, get_current_active_admin
from ..models.user import User

router = APIRouter()

@router.post("/feedback", response_model=schemas.Feedback)
def create_feedback(
    feedback: schemas.FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify that the booking exists and belongs to the user
    booking = db.query(models.Booking).filter(
        models.Booking.id == feedback.booking_id,
        models.Booking.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found or does not belong to current user"
        )
    
    db_feedback = models.Feedback(
        user_id=current_user.id,
        **feedback.dict()
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

@router.get("/feedback", response_model=List[schemas.Feedback])
def list_feedback(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "admin":
        return db.query(models.Feedback).all()
    return db.query(models.Feedback).filter(models.Feedback.user_id == current_user.id).all()

@router.get("/feedback/{booking_id}", response_model=schemas.Feedback)
def get_booking_feedback(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(models.Feedback).filter(models.Feedback.booking_id == booking_id)
    
    if current_user.role != "admin":
        query = query.filter(models.Feedback.user_id == current_user.id)
    
    feedback = query.first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    return feedback 