"""Inventory routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID

from app.core.database import get_db
from app.models.inventory import InventoryItem, InventoryTransaction

router = APIRouter()


class InventoryItemResponse(BaseModel):
    id: UUID
    name: str
    category: str
    unit: str
    quantity: float
    min_level: float
    cost_per_unit: float

    class Config:
        from_attributes = True


class InventoryTransactionCreate(BaseModel):
    item_id: UUID
    transaction_type: str
    quantity: float
    notes: Optional[str] = None


@router.get("/", response_model=dict)
def list_inventory(
    category: Optional[str] = None,
    low_stock: bool = False,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List inventory items."""
    query = db.query(InventoryItem).filter(InventoryItem.is_active == True)
    if category:
        query = query.filter(InventoryItem.category == category)
    if search:
        query = query.filter(InventoryItem.name.ilike(f"%{search}%"))
    if low_stock:
        query = query.filter(InventoryItem.quantity < InventoryItem.min_level)

    items = query.all()
    return {"data": [InventoryItemResponse.model_validate(i) for i in items]}


@router.get("/{item_id}", response_model=InventoryItemResponse)
def get_inventory_item(item_id: UUID, db: Session = Depends(get_db)):
    """Get inventory item by ID."""
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return InventoryItemResponse.model_validate(item)


@router.post("/transactions", status_code=201)
def create_transaction(
    transaction_data: InventoryTransactionCreate,
    db: Session = Depends(get_db)
):
    """Record an inventory transaction."""
    item = db.query(InventoryItem).filter(InventoryItem.id == transaction_data.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    # Update quantity
    if transaction_data.transaction_type == "PURCHASE":
        item.quantity += transaction_data.quantity
    elif transaction_data.transaction_type in ["SALE", "WASTE", "ADJUSTMENT"]:
        item.quantity -= transaction_data.quantity

    # Record transaction
    transaction = InventoryTransaction(
        item_id=transaction_data.item_id,
        transaction_type=transaction_data.transaction_type,
        quantity=transaction_data.quantity,
        notes=transaction_data.notes
    )
    db.add(transaction)
    db.commit()

    return {"message": "Transaction recorded", "new_quantity": float(item.quantity)}
