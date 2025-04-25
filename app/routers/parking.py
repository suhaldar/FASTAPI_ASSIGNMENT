from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import parking as models
from ..schemas import parking as schemas
from ..utils.security import get_current_user, get_current_active_admin
from ..models.user import User

router = APIRouter()

@router.get("/parking-slots", response_model=List[schemas.ParkingSlot])
def list_parking_slots(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    slots = db.query(models.ParkingSlot).offset(skip).limit(limit).all()
    return slots

@router.post("/parking-slots", response_model=schemas.ParkingSlot)
def create_parking_slot(
    slot: schemas.ParkingSlotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    db_slot = models.ParkingSlot(**slot.dict())
    db.add(db_slot)
    db.commit()
    db.refresh(db_slot)
    return db_slot

@router.put("/parking-slots/{slot_id}", response_model=schemas.ParkingSlot)
def update_parking_slot(
    slot_id: int,
    slot_update: schemas.ParkingSlotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    db_slot = db.query(models.ParkingSlot).filter(models.ParkingSlot.id == slot_id).first()
    if not db_slot:
        raise HTTPException(status_code=404, detail="Parking slot not found")
    
    for key, value in slot_update.dict().items():
        setattr(db_slot, key, value)
    
    db.commit()
    db.refresh(db_slot)
    return db_slot

@router.delete("/parking-slots/{slot_id}")
def delete_parking_slot(
    slot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    db_slot = db.query(models.ParkingSlot).filter(models.ParkingSlot.id == slot_id).first()
    if not db_slot:
        raise HTTPException(status_code=404, detail="Parking slot not found")
    
    db.delete(db_slot)
    db.commit()
    return {"message": "Parking slot deleted successfully"}

@router.post("/parking-slots/bulk", response_model=List[schemas.ParkingSlot])
def create_bulk_parking_slots(
    slots: List[schemas.ParkingSlotCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    db_slots = []
    for slot in slots:
        db_slot = models.ParkingSlot(**slot.dict())
        db.add(db_slot)
        db_slots.append(db_slot)
    
    db.commit()
    for slot in db_slots:
        db.refresh(slot)
    return db_slots

@router.put("/parking-slots/{slot_id}/maintenance")
def set_maintenance_mode(
    slot_id: int,
    maintenance: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    db_slot = db.query(models.ParkingSlot).filter(models.ParkingSlot.id == slot_id).first()
    if not db_slot:
        raise HTTPException(status_code=404, detail="Parking slot not found")
    
    db_slot.status = models.SlotStatus.MAINTENANCE if maintenance else models.SlotStatus.FREE
    db.commit()
    return {"message": f"Maintenance mode {'enabled' if maintenance else 'disabled'} for slot {slot_id}"} 