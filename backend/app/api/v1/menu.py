"""Menu routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from uuid import UUID

from app.core.database import get_db
from app.models.menu import MenuCategory, MenuItem, MenuItemVariant, MenuItemAddon

router = APIRouter()


class MenuItemResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    base_price: float
    image_url: Optional[str]
    is_available: bool
    preparation_time: int
    category_id: UUID

    class Config:
        from_attributes = True


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    display_order: int

    class Config:
        from_attributes = True


@router.get("/categories", response_model=dict)
def list_categories(db: Session = Depends(get_db)):
    """List menu categories."""
    categories = db.query(MenuCategory).order_by(MenuCategory.display_order).all()
    return {"data": [CategoryResponse.model_validate(c) for c in categories]}


@router.get("/items", response_model=dict)
def list_items(
    category_id: Optional[UUID] = None,
    available_only: bool = True,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List menu items."""
    query = db.query(MenuItem)
    if category_id:
        query = query.filter(MenuItem.category_id == category_id)
    if available_only:
        query = query.filter(MenuItem.is_available == True)
    if search:
        query = query.filter(MenuItem.name.ilike(f"%{search}%"))

    items = query.all()
    return {"data": [MenuItemResponse.model_validate(i) for i in items]}


@router.get("/items/{item_id}", response_model=MenuItemResponse)
def get_item(item_id: UUID, db: Session = Depends(get_db)):
    """Get a menu item by ID."""
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return MenuItemResponse.model_validate(item)
