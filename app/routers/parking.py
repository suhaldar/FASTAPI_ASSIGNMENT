from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import tuple_
from typing import List

from ..database import get_db
from ..models import parking as parking_models
from ..schemas import parking as parking_schemas
from ..utils.security import get_current_user, get_current_active_admin
from ..models.user import User

router = APIRouter()

@router.get("/parking-slots", response_model=List[parking_schemas.DisplayParkingSlot])
def list_parking_slots(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    display_slots = db.query(parking_models.ParkingSlot).limit(limit).all()
    if not display_slots:
        raise HTTPException(status_code=404, detail="No parking slots found")
    return display_slots

@router.post("/parking-slots")
def create_parking_slot(
    slot: parking_schemas.ParkingSlot,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    # Validate floor
    if slot.floor < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Floor number cannot be negative"
        )
    
    # Check if slot with same floor and label already exists
    existing_slot = db.query(parking_models.ParkingSlot).filter(
        parking_models.ParkingSlot.floor == slot.floor,
        parking_models.ParkingSlot.label == slot.label
    ).first()
    
    if existing_slot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Parking slot with floor '{slot.floor}' and label '{slot.label}' already exists"
        )
    
    db_slot = parking_models.ParkingSlot(floor=slot.floor, label=slot.label, status=slot.status)
    db.add(db_slot)
    db.commit()
    db.refresh(db_slot)
    return {"message": f"Parking slot with floor '{db_slot.floor}' and label '{db_slot.label}' created successfully"}


@router.put("/parking-slots/")
def update_parking_slot(
    slot_update: parking_schemas.ParkingSlot,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    db_slot = db.query(parking_models.ParkingSlot).filter(parking_models.ParkingSlot.floor == slot_update.floor, parking_models.ParkingSlot.label == slot_update.label).first()
    if not db_slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parking slot with floor '{slot_update.floor}' and label '{slot_update.label}' not found"
        )
    
    # Check if the status is being repeated
    if slot_update.status == db_slot.status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Parking slot with floor '{db_slot.floor}' and '{db_slot.label}' is already in '{db_slot.status}' status"
        )
    
    # Update the slot
    db_slot.status = slot_update.status
    db.commit()
    db.refresh(db_slot)
    return {"message": f"Parking slot with floor '{db_slot.floor}' and label '{db_slot.label}' is updated to '{db_slot.status}' status"}


@router.delete("/parking-slots/{floor}/{label}")
def delete_parking_slot(
    floor:int,
    label: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    db_slot = db.query(parking_models.ParkingSlot).filter(parking_models.ParkingSlot.floor == floor, parking_models.ParkingSlot.label == label).first()
    if not db_slot:
        raise HTTPException(status_code=404, detail=f"Parking slot with floor '{floor}' and label '{label}' not found")
    
    db.delete(db_slot)
    db.commit()
    return {"message": f"Parking slot with floor '{floor}' and label '{label}' deleted successfully"}


@router.post("/parking-slots/bulk")
def create_bulk_parking_slots(
    slots: List[parking_schemas.ParkingSlot],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    # Get all floor-label combinations from input
    input_combinations = {(slot.floor, slot.label) for slot in slots}
    
    # Single query to get existing slots
    existing_slots = db.query(parking_models.ParkingSlot).filter(
        tuple_(parking_models.ParkingSlot.floor, parking_models.ParkingSlot.label).in_(input_combinations)
    ).all()
    
    # Create set of existing combinations
    existing_combinations = {(slot.floor, slot.label) for slot in existing_slots}
    
    # Filter out existing slots and create new ones
    new_slots = [
        parking_models.ParkingSlot(floor=slot.floor, label=slot.label, status=slot.status)
        for slot in slots
        if (slot.floor, slot.label) not in existing_combinations
    ]
    
    # Bulk insert new slots
    db.bulk_save_objects(new_slots)
    db.commit()
    
    return {
        "message": "Bulk creation completed",
        "created": len(new_slots),
        "skipped": len(existing_slots),
        "skipped_slots": [f"Floor {slot.floor}, Label {slot.label}" for slot in existing_slots]
    }


@router.put("/parking-slots/bulk")
def update_bulk_parking_slots(
    slots: List[parking_schemas.ParkingSlot],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    # Get all floor-label combinations from input
    input_combinations = {(slot.floor, slot.label) for slot in slots}
    
    # Single query to get existing slots
    existing_slots = db.query(parking_models.ParkingSlot).filter(
        tuple_(parking_models.ParkingSlot.floor, parking_models.ParkingSlot.label).in_(input_combinations)
    ).all()
    
    # Create mapping of existing slots
    slot_map = {(slot.floor, slot.label): slot for slot in existing_slots}
    
    updated_count = 0
    not_found = []
    
    for slot in slots:
        key = (slot.floor, slot.label)
        if key in slot_map:
            db_slot = slot_map[key]
            db_slot.status = slot.status
            updated_count += 1
        else:
            not_found.append(f"Floor {slot.floor}, Label {slot.label}")
    
    db.commit()
    
    return {
        "message": "Bulk update completed",
        "updated": updated_count,
        "not_found": len(not_found),
        "not_found_slots": not_found
    } 


@router.put("/parking-slots/maintenance")
def set_maintenance_mode(
    floor: int = None,
    label: str = None,
    maintenance: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    query = db.query(parking_models.ParkingSlot)
    
    # If no parameters provided, update all slots
    if floor is None and label is None:
        slots = query.all()
    else:
        # Build query based on provided criteria
        if floor is not None and label is not None:
            query = query.filter(parking_models.ParkingSlot.floor == floor, parking_models.ParkingSlot.label == label)
        elif floor is not None:
            query = query.filter(parking_models.ParkingSlot.floor == floor)
        elif label is not None:
            query = query.filter(parking_models.ParkingSlot.label == label)
        
        slots = query.all()
    
    if not slots:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No parking slots found matching the criteria"
        )
    
    # Update all matching slots
    for slot in slots:
        if maintenance:
            slot.status = parking_schemas.SlotStatus.MAINTENANCE
        else:
            slot.status = parking_schemas.SlotStatus.FREE
    
    db.commit()
    
    return {
        "message": f"Maintenance mode {'enabled' if maintenance else 'disabled'} for {len(slots)} slot(s)",
        "updated_slots": [f"Floor {slot.floor}, Label {slot.label}" for slot in slots]
    }

