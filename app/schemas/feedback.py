from pydantic import BaseModel, ConfigDict, validator, Field
from datetime import datetime
from typing import Optional

class FeedbackBase(BaseModel):
    booking_id: int
    rating: int 
    comment: Optional[str] = None

    @validator('rating')
    def validate_rating(cls, v):
        # Convert float to int if it's a whole number
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        
        return v

class Feedback(FeedbackBase):
    pass

class DisplayFeedback(FeedbackBase):
    user_id: int
    floor: int
    label: str
    created_at: datetime
    
