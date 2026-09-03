"""Staff and Guest models."""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Date, UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Staff(Base):
    __tablename__ = "staff"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    employee_id = Column(String(50), unique=True)
    department = Column(String(100))
    hire_date = Column(Date)
    is_active = Column(Boolean, default=True)
    phone = Column(String(20))
    emergency_contact = Column(String(200))
    created_at = Column(DateTime, server_default=func.now())


class Guest(Base):
    __tablename__ = "guests"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255))
    phone = Column(String(20))
    identity_type = Column(String(50))
    identity_number = Column(String(100))
    address = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
