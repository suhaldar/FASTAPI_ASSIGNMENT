from pydantic import BaseModel
from typing import Optional

class ParkingSlotBase(BaseModel):
    label: str
    status: str = "free"

class ParkingSlotCreate(ParkingSlotBase):
    pass

class ParkingSlot(ParkingSlotBase):
    id: int

    class Config:
        from_attributes = True 