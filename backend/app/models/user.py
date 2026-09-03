"""User model."""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"))
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"))
    is_active = Column(Boolean, default=True)
    phone = Column(String(20))
    avatar_url = Column(String(500))
    last_login = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
