"""Inventory model."""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Numeric, Integer, UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class InventoryItem(Base):
    __tablename__ = "inventory_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"))
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    unit = Column(String(20), nullable=False)
    quantity = Column(Numeric(10, 3), default=0)
    min_level = Column(Numeric(10, 3), default=0)
    max_level = Column(Numeric(10, 3))
    cost_per_unit = Column(Numeric(10, 2), default=0)
    batch_number = Column(String(100))
    expiry_date = Column(String)  # Simplified for demo
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id"), nullable=False)
    transaction_type = Column(String(30), nullable=False)
    quantity = Column(Numeric(10, 3), nullable=False)
    reference_id = Column(UUID(as_uuid=True))
    notes = Column(Text)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
