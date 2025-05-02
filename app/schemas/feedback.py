from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Feedback(BaseModel):
    booking_id: int
    rating: int
    comment: Optional[str] = None


class DisplayFeedback(BaseModel):
    booking_id: int
    rating: int
    comment: Optional[str] = None
    
    class Config:
        orm_mode = True
