from sqlalchemy import Column, Integer, String, Boolean, Enum, UniqueConstraint
from ..database import Base

import enum

class SlotStatus(str, enum.Enum):
    """Enum for parking slot status."""
    FREE = "free"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"
    
class ParkingSlot(Base):
    __tablename__ = "parking_slots"
    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    floor = Column(Integer)
    label = Column(String)
    status = Column(String)
    
    __table_args__ = (
        UniqueConstraint('floor', 'label', name='uix_floor_label'),
    ) 