"""Purchase order models."""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, UUID, Numeric
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"))
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"))
    order_number = Column(String(50), unique=True, nullable=False)
    status = Column(String(30), default="DRAFT")
    total_amount = Column(Numeric(12, 2), default=0)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class PurchaseItem(Base):
    __tablename__ = "purchase_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("purchase_orders.id", ondelete="CASCADE"))
    inventory_item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id"))
    quantity = Column(Numeric(10, 3), nullable=False)
    unit_price = Column(Numeric(10, 2))
    received_quantity = Column(Numeric(10, 3), default=0)
