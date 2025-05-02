from pydantic import BaseModel
from typing import Optional
from enum import Enum

class SlotStatus(str, Enum):
    FREE = "free"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"

class ParkingSlot(BaseModel):
    floor: int
    label: str
    status: Optional[SlotStatus] = SlotStatus.FREE

class DisplayParkingSlot(BaseModel):
    floor: int
    label: str
    status: SlotStatus
    
    class Config:
        orm_mode = True