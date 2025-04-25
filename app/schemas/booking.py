from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BookingBase(BaseModel):
    slot_id: int

class BookingCreate(BookingBase):
    pass

class Booking(BookingBase):
    id: int
    user_id: int
    start_time: datetime
    end_time: Optional[datetime]
    status: str

    class Config:
        from_attributes = True 