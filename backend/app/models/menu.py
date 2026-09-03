"""Menu models."""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Numeric, Integer, UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class MenuCategory(Base):
    __tablename__ = "menu_categories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)


class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"))
    category_id = Column(UUID(as_uuid=True), ForeignKey("menu_categories.id"))
    name = Column(String(200), nullable=False)
    description = Column(Text)
    base_price = Column(Numeric(10, 2), nullable=False)
    image_url = Column(String(500))
    is_available = Column(Boolean, default=True)
    preparation_time = Column(Integer, default=15)
    tax_rate = Column(Numeric(5, 2), default=5.00)


class MenuItemVariant(Base):
    __tablename__ = "menu_item_variants"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    menu_item_id = Column(UUID(as_uuid=True), ForeignKey("menu_items.id"), nullable=False)
    name = Column(String(100), nullable=False)
    price_modifier = Column(Numeric(10, 2), default=0)


class MenuItemAddon(Base):
    __tablename__ = "menu_item_addons"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    menu_item_id = Column(UUID(as_uuid=True), ForeignKey("menu_items.id"), nullable=False)
    name = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), default=0)
