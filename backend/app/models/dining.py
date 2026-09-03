"""Dining-related SQLAlchemy models."""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, UUID, Text
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class RestaurantTable(Base):
    __tablename__ = "restaurant_tables"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"))
    table_number = Column(String(20), nullable=False)
    capacity = Column(Integer, default=4)
    is_active = Column(Boolean, default=True)
    location = Column(String(100))
    status = Column(String(20), default="AVAILABLE")
    created_at = Column(DateTime, server_default=func.now())


class LakeZone(Base):
    __tablename__ = "lake_zones"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"))
    name = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class LakeSeat(Base):
    __tablename__ = "lake_seats"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("lake_zones.id"), nullable=False)
    seat_code = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
