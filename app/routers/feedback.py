from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import and_

from ..database import get_db
from ..models import feedback as models_feedback
from ..models import booking as models_booking
from ..models import parking as models_parking
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
    floor: Optional[int] = None,
    label: Optional[str] = None,
    booking_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins is prohibited from viewing feedback"
        )
    # Start with base query
    query = db.query(
        models_feedback.Feedback,
        models_parking.ParkingSlot.floor,
        models_parking.ParkingSlot.label
    )
    
    # Join with Booking and ParkingSlot for floor and label filtering
    query = query.join(
        models_booking.Booking,
        models_feedback.Feedback.booking_id == models_booking.Booking.id
    ).join(
        models_parking.ParkingSlot,
        and_(
            models_booking.Booking.floor_id == models_parking.ParkingSlot.floor,
            models_booking.Booking.label_id == models_parking.ParkingSlot.label
        )
    )
    
    # Apply role-based filtering
    if current_user.role != "admin":
        query = query.filter(models_feedback.Feedback.user_id == current_user.id)
    
    # Apply optional floor filter
    if floor is not None:
        query = query.filter(models_parking.ParkingSlot.floor == floor)
    
    # Apply optional label filter
    if label is not None:
        query = query.filter(models_parking.ParkingSlot.label == label)
    
    if booking_id is not None:
        query = query.filter(models_feedback.Feedback.booking_id == booking_id)
    # Execute query and format results
    results = query.all()
    
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No feedback found matching the criteria"
        )
    
    # Format results to match DisplayFeedback schema
    feedback_list = []
    for feedback, floor, label in results:
        feedback_dict = {
            "id": feedback.id,
            "user_id": feedback.user_id,
            "booking_id": feedback.booking_id,
            "rating": feedback.rating,
            "comment": feedback.comment,
            "created_at": feedback.created_at,
            "floor": floor,
            "label": label
        }
        feedback_list.append(feedback_dict)
    
    return feedback_list

@router.get("/feedback/manage", response_model=List[schemas_feedback.DisplayFeedback])
def manage_feedback(
    booking_id: Optional[int] = None,
    floor: Optional[int] = None,
    label: Optional[str] = None,
    min_rating: Optional[int] = None,
    max_rating: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Manage feedback entries with advanced filtering options.
    Only accessible by admin users.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User {current_user.username} is prohibited from viewing feedback"
        )
    # Start with base query
    query = db.query(
        models_feedback.Feedback,
        models_parking.ParkingSlot.floor,
        models_parking.ParkingSlot.label
    )
    
    # Join with Booking and ParkingSlot for floor and label filtering
    query = query.join(
        models_booking.Booking,
        models_feedback.Feedback.booking_id == models_booking.Booking.id
    ).join(
        models_parking.ParkingSlot,
        and_(
            models_booking.Booking.floor_id == models_parking.ParkingSlot.floor,
            models_booking.Booking.label_id == models_parking.ParkingSlot.label
        )
    )
    
    # Apply filters
    if booking_id is not None:
        query = query.filter(models_feedback.Feedback.booking_id == booking_id)
    
    if floor is not None:
        query = query.filter(models_parking.ParkingSlot.floor == floor)
    
    if label is not None:
        query = query.filter(models_parking.ParkingSlot.label == label)
    
    if min_rating is not None:
        query = query.filter(models_feedback.Feedback.rating >= min_rating)
    
    if max_rating is not None:
        query = query.filter(models_feedback.Feedback.rating <= max_rating)
    
    # Order by creation date, newest first
    query = query.order_by(models_feedback.Feedback.created_at.desc())
    
    # Execute query and format results
    results = query.all()
    
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No feedback found matching the criteria"
        )
    
    # Format results to match DisplayFeedback schema
    feedback_list = []
    for feedback, floor, label in results:
        feedback_dict = {
            "booking_id": feedback.booking_id,
            "user_id": feedback.user_id,
            "rating": feedback.rating,
            "comment": feedback.comment,
            "created_at": feedback.created_at,
            "floor": floor,
            "label": label
        }
        feedback_list.append(feedback_dict)
    
    return feedback_list

