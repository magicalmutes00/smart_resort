"""Orders routes with full business logic."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Header, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from uuid import UUID
import uuid

from app.core.database import get_db
from app.core.rbac import RequirePermission, get_user_with_role
from app.services.order_service import OrderService

router = APIRouter()


class OrderItemCreate(BaseModel):
    menu_item_id: UUID
    variant_id: Optional[UUID] = None
    quantity: int = Field(default=1, ge=1)
    notes: Optional[str] = None


class OrderCreate(BaseModel):
    table_id: Optional[UUID] = None
    room_id: Optional[UUID] = None
    lake_seat_id: Optional[UUID] = None
    order_type: str = Field(default="DINE_IN", pattern="^(DINE_IN|ROOM_SERVICE|LAKE|TAKEOUT|DELIVERY)$")
    items: list[OrderItemCreate] = Field(..., min_length=1)
    notes: Optional[str] = None
    special_instructions: Optional[str] = None


class OrderResponse(BaseModel):
    id: UUID
    order_number: str
    status: str
    order_type: str
    total_amount: float
    notes: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


def _serialize_order(order) -> dict:
    return {
        "id": str(order.id),
        "order_number": order.order_number,
        "status": order.status,
        "order_type": order.order_type,
        "total_amount": float(order.total_amount),
        "notes": order.notes,
        "created_at": order.created_at.isoformat() if order.created_at else None,
    }


async def _emit_order_events(db: Session):
    """Background task to emit queued events."""
    service = OrderService(db)
    await service.emit_events()


@router.post("/", response_model=dict, status_code=201)
async def create_order(
    order_data: OrderCreate,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current: dict = Depends(get_user_with_role),
):
    """Create a new order.

    Supports idempotency via Idempotency-Key header.
    Requires authentication for all order types.
    """
    if not order_data.items:
        raise HTTPException(status_code=400, detail="Order must have at least one item")

    if idempotency_key is None:
        idempotency_key = str(uuid.uuid4())

    service = OrderService(db)
    try:
        order = service.create_order(
            items=[item.model_dump() for item in order_data.items],
            order_type=order_data.order_type,
            table_id=str(order_data.table_id) if order_data.table_id else None,
            room_id=str(order_data.room_id) if order_data.room_id else None,
            lake_seat_id=str(order_data.lake_seat_id) if order_data.lake_seat_id else None,
            property_id=current.get("property_id"),
            staff_id=current.get("id"),
            notes=order_data.notes,
            special_instructions=order_data.special_instructions,
            idempotency_key=idempotency_key,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Emit events in background
    if background_tasks:
        background_tasks.add_task(_emit_order_events, db)

    return _serialize_order(order)


@router.get("/", response_model=dict)
def list_orders(
    status: Optional[str] = None,
    order_type: Optional[str] = Query(None, alias="type"),
    kitchen: bool = False,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current: dict = Depends(RequirePermission("orders.read")),
):
    """List orders with optional filters."""
    service = OrderService(db)
    offset = (page - 1) * limit

    if kitchen:
        orders = service.get_kitchen_queue()
    else:
        orders = service.list_orders(
            status=status,
            order_type=order_type,
            limit=limit,
            offset=offset,
        )

    return {
        "data": [_serialize_order(o) for o in orders],
        "meta": {"count": len(orders)},
    }


@router.get("/{order_id}", response_model=dict)
def get_order(
    order_id: UUID,
    db: Session = Depends(get_db),
    current: dict = Depends(RequirePermission("orders.read")),
):
    """Get a specific order."""
    service = OrderService(db)
    order = service.get_order(str(order_id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return _serialize_order(order)


@router.patch("/{order_id}/status", response_model=dict)
async def update_status(
    order_id: UUID,
    new_status: str = Query(..., alias="status"),
    notes: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current: dict = Depends(RequirePermission("orders.status_update")),
):
    """Update order status with state machine validation."""
    service = OrderService(db)
    try:
        order = service.transition_status(
            order_id=str(order_id),
            new_status=new_status,
            changed_by=current.get("id"),
            notes=notes,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if background_tasks:
        background_tasks.add_task(_emit_order_events, db)

    return {"id": str(order.id), "status": order.status}


@router.post("/{order_id}/cancel", response_model=dict)
async def cancel_order(
    order_id: UUID,
    notes: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current: dict = Depends(RequirePermission("orders.cancel")),
):
    """Cancel an order if in a cancellable state."""
    service = OrderService(db)
    try:
        order = service.transition_status(
            order_id=str(order_id),
            new_status="CANCELLED",
            changed_by=current.get("id"),
            notes=notes,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if background_tasks:
        background_tasks.add_task(_emit_order_events, db)

    return {"id": str(order.id), "status": order.status}
