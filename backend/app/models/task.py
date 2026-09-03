"""Task-related models."""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Task(Base):
    __tablename__ = "tasks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"))
    type = Column(String(50), nullable=False)
    location_type = Column(String(50))
    location_id = Column(UUID(as_uuid=True))
    priority = Column(String(20), default="NORMAL")
    status = Column(String(30), default="PENDING", index=True)
    notes = Column(Text)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    assigned_staff_id = Column(UUID(as_uuid=True), ForeignKey("staff.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class TaskAssignment(Base):
    __tablename__ = "task_assignments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    staff_id = Column(UUID(as_uuid=True), ForeignKey("staff.id"), nullable=False)
    assigned_at = Column(DateTime, server_default=func.now())
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
