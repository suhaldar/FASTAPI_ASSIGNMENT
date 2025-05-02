from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import feedback as models_feedback
from ..models import booking as models_booking
from ..schemas import feedback as schemas_feedback
from ..utils.security import get_current_user, get_current_active_admin
from ..models.user import User

router = APIRouter()

@router.post("/feedback")
def create_feedback(
    feedback: schemas_feedback.Feedback,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins cannot create feedback"
        )
    # Verify that the booking exists and belongs to the user
    booking = db.query(models_booking.Booking).filter(
        models_booking.Booking.id == feedback.booking_id,
        models_booking.Booking.user_id == current_user.id
    ).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found or does not belong to current user"
        )
    
    db_feedback = models_feedback.Feedback(
        user_id=current_user.id,
        **feedback.dict()
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return {"message": "Feedback created successfully"}

@router.get("/feedback", response_model=List[schemas_feedback.DisplayFeedback])
def list_feedback(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Admin can see all feedback, users can only see their own
    if current_user.role == "admin":
        feedback = db.query(models_feedback.Feedback).all()
    else:
        feedback = db.query(models_feedback.Feedback).filter(
            models_feedback.Feedback.user_id == current_user.id
        ).all()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No feedback found"
        )
    
    return feedback


@router.get("/feedback/{booking_id}", response_model=schemas_feedback.DisplayFeedback)
def get_booking_feedback(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(models_feedback.Feedback).filter(models_feedback.Feedback.booking_id == booking_id)
    
    if current_user.role != "admin":
        query = query.filter(models_feedback.Feedback.user_id == current_user.id)
    
    feedback = query.first()    
    if not feedback:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
    
    return feedback 
