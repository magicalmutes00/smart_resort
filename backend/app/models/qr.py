"""QR Code model."""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, UUID, Text
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class QRCode(Base):
    __tablename__ = "qr_codes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"))
    code = Column(String(100), unique=True, nullable=False, index=True)
    location_type = Column(String(50), nullable=False)  # ROOM, TABLE, LAKE_SEAT, TEA_STALL
    location_id = Column(UUID(as_uuid=True), nullable=False)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
