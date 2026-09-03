"""Audit, notification, and supplier models."""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, UUID, Numeric, JSON
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    staff_id = Column(UUID(as_uuid=True), ForeignKey("staff.id"))
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"))
    title = Column(String(255), nullable=False)
    body = Column(Text)
    type = Column(String(50), nullable=False)
    is_read = Column(Boolean, default=False)
    data = Column(JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    entity = Column(String(50), nullable=False)
    entity_id = Column(UUID(as_uuid=True))
    old_value = Column(JSON)
    new_value = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(255))
    phone = Column(String(20))
    address = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
