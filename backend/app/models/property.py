"""Property model."""
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Property(Base):
    __tablename__ = "properties"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    address = Column(Text)
    phone = Column(String(50))
    email = Column(String(255))
    timezone = Column(String(50), default="UTC")
    is_active = Column(Boolean, default=True)
    settings = Column(JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
