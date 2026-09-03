"""Order service — encapsulates business logic for orders."""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem, OrderStatusHistory
from app.models.menu import MenuItem
from app.websocket.gateway import get_connection_manager


# Valid state transitions for orders
ORDER_STATE_TRANSITIONS = {
    "CREATED": ["CONFIRMED", "CANCELLED"],
    "CONFIRMED": ["ACCEPTED", "CANCELLED"],
    "ACCEPTED": ["PREPARING", "CANCELLED"],
    "PREPARING": ["READY"],
    "READY": ["OUT_FOR_DELIVERY", "DELIVERED"],
    "OUT_FOR_DELIVERY": ["DELIVERED"],
    "DELIVERED": ["COMPLETED"],
    "COMPLETED": [],
    "CANCELLED": [],
}

# Terminal states
TERMINAL_STATES = {"COMPLETED", "CANCELLED"}


class OrderService:
    """Service class for order operations."""

    def __init__(self, db: Session):
        self.db = db
        self._events = []

    def generate_order_number(self) -> str:
        """Generate a unique, human-readable order number."""
        return f"#{uuid.uuid4().hex[:6].upper()}"

    def create_order(
        self,
        items: list[dict],
        order_type: str = "DINE_IN",
        table_id: Optional[str] = None,
        room_id: Optional[str] = None,
        lake_seat_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        staff_id: Optional[str] = None,
        property_id: Optional[str] = None,
        notes: Optional[str] = None,
        special_instructions: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Order:
        """Create an order with full transaction safety."""
        # Idempotency check
        if idempotency_key:
            existing = self.db.query(Order).filter(
                Order.idempotency_key == idempotency_key
            ).first()
            if existing:
                return existing

        order = Order(
            order_number=self.generate_order_number(),
            property_id=property_id,
            customer_id=customer_id,
            table_id=table_id,
            room_id=room_id,
            lake_seat_id=lake_seat_id,
            staff_id=staff_id,
            status="CREATED",
            order_type=order_type,
            notes=notes,
            special_instructions=special_instructions,
            idempotency_key=idempotency_key,
        )
        self.db.add(order)
        self.db.flush()

        total = 0.0
        for item in items:
            menu_item = self.db.query(MenuItem).filter(
                MenuItem.id == item["menu_item_id"]
            ).first()
            if not menu_item:
                raise ValueError(f"Menu item not found: {item['menu_item_id']}")

            quantity = int(item.get("quantity", 1))
            unit_price = float(menu_item.base_price)

            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=menu_item.id,
                variant_id=item.get("variant_id"),
                quantity=quantity,
                unit_price=unit_price,
                notes=item.get("notes"),
            )
            self.db.add(order_item)
            total += unit_price * quantity

        order.total_amount = total
        history = OrderStatusHistory(order_id=order.id, status="CREATED")
        self.db.add(history)

        self.db.commit()
        self.db.refresh(order)

        # Fire async event
        self._events.append({
            "channel": f"orders:{order.order_type.lower()}",
            "event": "order:created",
            "data": self._serialize_order(order),
        })

        return order

    def transition_status(
        self,
        order_id: str,
        new_status: str,
        changed_by: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Order:
        """Transition an order to a new status with validation."""
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError(f"Order not found: {order_id}")

        current = order.status
        valid_next = ORDER_STATE_TRANSITIONS.get(current, [])
        if new_status not in valid_next:
            raise ValueError(
                f"Invalid transition: {current} → {new_status}. "
                f"Allowed: {valid_next}"
            )

        order.status = new_status
        history = OrderStatusHistory(
            order_id=order.id,
            status=new_status,
            notes=notes,
            changed_by=changed_by,
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(order)

        # Event emission
        channel_map = {
            "CREATED": f"orders:{order.order_type.lower()}",
            "CONFIRMED": f"orders:{order.order_type.lower()}",
            "ACCEPTED": "kitchen:all",
            "PREPARING": "kitchen:all",
            "READY": f"orders:{order.order_type.lower()}",
            "OUT_FOR_DELIVERY": "tasks:delivery",
            "DELIVERED": f"orders:{order.order_type.lower()}",
            "COMPLETED": f"orders:{order.order_type.lower()}",
            "CANCELLED": f"orders:{order.order_type.lower()}",
        }
        channel = channel_map.get(new_status, "orders:all")

        self._events.append({
            "channel": channel,
            "event": "order:status_changed",
            "data": self._serialize_order(order, status_history=[{
                "status": new_status,
                "notes": notes,
                "changed_at": datetime.utcnow().isoformat(),
            }]),
        })

        # When ready and a delivery is required, auto-create a delivery task
        if new_status == "READY" and order.order_type in ("ROOM_SERVICE", "LAKE", "DELIVERY"):
            self._create_delivery_task(order)

        return order

    def _create_delivery_task(self, order: Order):
        """Auto-create a delivery task for orders that require delivery."""
        from app.models.task import Task

        location_type = "ROOM" if order.room_id else "LAKE_SEAT" if order.lake_seat_id else "TABLE"
        location_id = order.room_id or order.lake_seat_id or order.table_id

        task = Task(
            type="DELIVERY",
            property_id=order.property_id,
            location_type=location_type,
            location_id=location_id,
            priority="NORMAL",
            status="PENDING",
            notes=f"Deliver order {order.order_number}",
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        self._events.append({
            "channel": "tasks:delivery",
            "event": "task:created",
            "data": {
                "id": str(task.id),
                "type": task.type,
                "location_type": task.location_type,
                "location_id": str(task.location_id) if task.location_id else None,
                "order_id": str(order.id),
                "order_number": order.order_number,
                "status": task.status,
            },
        })

    def get_order(self, order_id: str) -> Optional[Order]:
        return self.db.query(Order).filter(Order.id == order_id).first()

    def list_orders(
        self,
        status: Optional[str] = None,
        order_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Order]:
        query = self.db.query(Order)
        if status:
            query = query.filter(Order.status == status)
        if order_type:
            query = query.filter(Order.order_type == order_type)
        return (
            query.order_by(Order.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_kitchen_queue(self, station: Optional[str] = None) -> list[Order]:
        """Get orders for kitchen display (PREPARING, ACCEPTED, READY)."""
        statuses = ["ACCEPTED", "PREPARING", "READY"]
        query = self.db.query(Order).filter(Order.status.in_(statuses))
        query = query.filter(Order.order_type.in_(["DINE_IN", "TAKEOUT", "ROOM_SERVICE"]))
        return query.order_by(Order.created_at.asc()).all()

    def _serialize_order(self, order: Order, status_history: Optional[list] = None) -> dict:
        items = []
        for item in order.items:
            items.append({
                "id": str(item.id),
                "menu_item_id": str(item.menu_item_id),
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "notes": item.notes,
            })
        return {
            "id": str(order.id),
            "order_number": order.order_number,
            "status": order.status,
            "order_type": order.order_type,
            "total_amount": float(order.total_amount),
            "table_id": str(order.table_id) if order.table_id else None,
            "room_id": str(order.room_id) if order.room_id else None,
            "lake_seat_id": str(order.lake_seat_id) if order.lake_seat_id else None,
            "items": items,
            "notes": order.notes,
            "special_instructions": order.special_instructions,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "status_history": status_history or [],
        }

    async def emit_events(self):
        """Emit all queued events through the WebSocket gateway."""
        if not self._events:
            return
        manager = get_connection_manager()
        for ev in self._events:
            await manager.broadcast(ev["channel"], ev["event"], ev["data"])
        self._events.clear()
