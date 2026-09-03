"""Role model."""
from sqlalchemy import Column, String, Text, UUID
import uuid
from app.core.database import Base


class Role(Base):
    __tablename__ = "roles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
