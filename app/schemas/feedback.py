from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class FeedbackBase(BaseModel):
    booking_id: int
    rating: int
    comment: Optional[str] = None

class Feedback(FeedbackBase):
    pass

class DisplayFeedback(FeedbackBase):
    user_id: int
    floor: int
    label: str
    created_at: datetime
    
