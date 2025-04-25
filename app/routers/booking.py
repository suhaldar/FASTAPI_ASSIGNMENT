from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database import get_db
from ..models import booking as models
from ..models import parking as parking_models
from ..schemas import booking as schemas
from ..utils.security import get_current_user
from ..models.user import User

router = APIRouter()

@router.post("/bookings", response_model=schemas.Booking)
def create_booking(
    booking: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "admin":
        raise HTTPException(
            status_code=400,
            detail="Admins cannot create bookings"
        )

    # Check if slot exists and is available
    slot = db.query(parking_models.ParkingSlot).filter(
        parking_models.ParkingSlot.id == booking.slot_id
    ).first()
    
    if not slot:
        raise HTTPException(status_code=404, detail="Parking slot not found")
    
    if slot.status != parking_models.SlotStatus.FREE:
        raise HTTPException(status_code=400, detail="Parking slot is not available")
    
    # Create booking
    db_booking = models.Booking(
        user_id=current_user.id,
        slot_id=booking.slot_id,
        status="active"
    )
    
    # Update slot status
    slot.status = parking_models.SlotStatus.OCCUPIED
    
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

@router.get("/bookings", response_model=List[schemas.Booking])
def list_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "admin":
        return db.query(models.Booking).all()
    return db.query(models.Booking).filter(models.Booking.user_id == current_user.id).all()

@router.put("/bookings/{booking_id}/cancel")
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to cancel this booking")
    
    if booking.status != "active":
        raise HTTPException(status_code=400, detail="Booking is not active")
    
    # Update booking status
    booking.status = "cancelled"
    booking.end_time = datetime.utcnow()
    
    # Free up the parking slot
    slot = db.query(parking_models.ParkingSlot).filter(
        parking_models.ParkingSlot.id == booking.slot_id
    ).first()
    slot.status = parking_models.SlotStatus.FREE
    
    db.commit()
    return {"message": "Booking cancelled successfully"} 