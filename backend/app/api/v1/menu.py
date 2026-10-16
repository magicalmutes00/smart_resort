"""Menu routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from uuid import UUID

from app.core.database import get_db
from app.core.rbac import RequirePermission, Permission
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


class MenuItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    base_price: float = Field(..., gt=0)
    preparation_time: int = Field(..., ge=0)
    category_id: UUID
    is_available: bool = True


@router.post("/items", response_model=MenuItemResponse, status_code=201)
def create_item(
    payload: MenuItemCreate,
    current: dict = Depends(RequirePermission(Permission.MENU_CREATE)),
    db: Session = Depends(get_db),
):
    """Create a new menu item."""
    category = db.query(MenuCategory).filter(MenuCategory.id == payload.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    item = MenuItem(
        property_id=category.property_id,
        category_id=payload.category_id,
        name=payload.name,
        description=payload.description,
        base_price=payload.base_price,
        preparation_time=payload.preparation_time,
        is_available=payload.is_available,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return MenuItemResponse.model_validate(item)
