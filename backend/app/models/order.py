"""Order-related models."""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Numeric, Integer, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Order(Base):
    __tablename__ = "orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number = Column(String(50), unique=True, nullable=False)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"))
    customer_id = Column(UUID(as_uuid=True), ForeignKey("guests.id"))
    table_id = Column(UUID(as_uuid=True), ForeignKey("restaurant_tables.id"))
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id"))
    lake_seat_id = Column(UUID(as_uuid=True), ForeignKey("lake_seats.id"))
    staff_id = Column(UUID(as_uuid=True), ForeignKey("staff.id"))
    status = Column(String(30), default="CREATED", index=True)
    order_type = Column(String(30), default="DINE_IN")
    total_amount = Column(Numeric(12, 2), default=0)
    notes = Column(Text)
    special_instructions = Column(Text)
    idempotency_key = Column(String(100), unique=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(UUID(as_uuid=True), ForeignKey("menu_items.id"))
    variant_id = Column(UUID(as_uuid=True), ForeignKey("menu_item_variants.id"))
    quantity = Column(Integer, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    notes = Column(Text)


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    status = Column(String(30), nullable=False)
    notes = Column(Text)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
