from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum




class BookingSlot(BaseModel):
    user_id: int
    floor_id: str
    label_id: str
    start_time: datetime
    end_time: Optional[datetime]
    status: str

class CreateBookingSlot(BaseModel):
    floor_id: str
    label_id: str
    
    class Config:
        orm_mode = True

class DisplayBookingSlot(BaseModel):
    user_id: int
    floor_id: str
    label_id: str
    status: str
    
    class Config:
        orm_mode = True