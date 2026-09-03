"""Room model."""
from sqlalchemy import Column, String, DateTime, ForeignKey, UUID, Numeric, Integer, Text, JSON
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Room(Base):
    __tablename__ = "rooms"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"))
    number = Column(String(20), nullable=False)
    room_type_id = Column(UUID(as_uuid=True), ForeignKey("room_types.id"))
    floor = Column(Integer)
    status = Column(String(20), default="AVAILABLE")
    created_at = Column(DateTime, server_default=func.now())


class RoomType(Base):
    __tablename__ = "room_types"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    base_price = Column(Numeric(12, 2), nullable=False)
    max_occupancy = Column(Integer, default=2)
    amenities = Column(JSON, default=list)
