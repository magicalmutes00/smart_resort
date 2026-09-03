"""Housekeeping model."""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class HousekeepingTask(Base):
    __tablename__ = "housekeeping_tasks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"))
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id"))
    task_type = Column(String(50), nullable=False)
    status = Column(String(30), default="PENDING")
    assigned_staff_id = Column(UUID(as_uuid=True), ForeignKey("staff.id"))
    priority = Column(String(20), default="NORMAL")
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
