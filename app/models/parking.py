from sqlalchemy import Column, Integer, String, Boolean, Enum
from ..database import Base
import enum

class SlotStatus(str, enum.Enum):
    FREE = "free"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"

class ParkingSlot(Base):
    __tablename__ = "parking_slots"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, unique=True, index=True)
    status = Column(String, default=SlotStatus.FREE) 