"""Reservation and guest folio models."""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, UUID, Numeric, Date
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"))
    guest_id = Column(UUID(as_uuid=True), ForeignKey("guests.id"))
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id"))
    check_in = Column(Date, nullable=False)
    check_out = Column(Date, nullable=False)
    status = Column(String(30), default="PENDING")
    total_amount = Column(Numeric(12, 2))
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class GuestFolio(Base):
    __tablename__ = "guest_folios"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reservation_id = Column(UUID(as_uuid=True), ForeignKey("reservations.id"))
    guest_id = Column(UUID(as_uuid=True), ForeignKey("guests.id"))
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id"))
    total_charges = Column(Numeric(12, 2), default=0)
    paid_amount = Column(Numeric(12, 2), default=0)
    status = Column(String(30), default="OPEN")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class FolioItem(Base):
    __tablename__ = "folio_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    folio_id = Column(UUID(as_uuid=True), ForeignKey("guest_folios.id", ondelete="CASCADE"))
    item_type = Column(String(50), nullable=False)
    description = Column(String(250), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    reference_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, server_default=func.now())
