"""Maintenance model."""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"))
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id"))
    requested_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    description = Column(Text, nullable=False)
    priority = Column(String(20), default="NORMAL")
    status = Column(String(30), default="PENDING")
    assigned_staff_id = Column(UUID(as_uuid=True), ForeignKey("staff.id"))
    resolution_notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
