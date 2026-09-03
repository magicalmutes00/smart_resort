"""Analytics service — real revenue and metrics from DB."""
from datetime import datetime, date, timedelta
from typing import Optional
from sqlalchemy import func, and_, extract
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.reservation import Reservation, GuestFolio, FolioItem
from app.models.inventory import InventoryItem, InventoryTransaction
from app.models.task import Task
from app.models.staff import Staff


class AnalyticsService:
    """Generate real analytics from database aggregates."""

    def __init__(self, db: Session):
        self.db = db

    def revenue_report(
        self,
        date_from: date,
        date_to: date,
        group_by: str = "day",
        property_id: Optional[str] = None,
    ) -> list[dict]:
        """Revenue broken down by day/week/month."""
        date_filter = and_(
            Order.created_at >= datetime.combine(date_from, datetime.min.time()),
            Order.created_at <= datetime.combine(date_to, datetime.max.time()),
            Order.status.in_(["COMPLETED", "DELIVERED"]),
        )

        if property_id:
            date_filter = and_(date_filter, Order.property_id == property_id)

        query = self.db.query(
            func.date(Order.created_at).label("date"),
            func.sum(Order.total_amount).label("total"),
        ).filter(date_filter).group_by(func.date(Order.created_at))

        results = query.all()
        return [{"date": str(r.date), "revenue": float(r.total or 0)} for r in results]

    def orders_summary(
        self,
        date_from: date,
        date_to: date,
        property_id: Optional[str] = None,
    ) -> dict:
        """Order counts and values by status and type."""
        date_filter = and_(
            Order.created_at >= datetime.combine(date_from, datetime.min.time()),
            Order.created_at <= datetime.combine(date_to, datetime.max.time()),
        )

        if property_id:
            date_filter = and_(date_filter, Order.property_id == property_id)

        total = self.db.query(func.count(Order.id)).filter(date_filter).scalar() or 0
        completed = self.db.query(func.count(Order.id)).filter(
            date_filter, Order.status == "COMPLETED"
        ).scalar() or 0
        pending = self.db.query(func.count(Order.id)).filter(
            date_filter, Order.status.in_(["CREATED", "CONFIRMED", "ACCEPTED", "PREPARING"])
        ).scalar() or 0

        total_revenue = self.db.query(func.sum(Order.total_amount)).filter(
            date_filter, Order.status == "COMPLETED"
        ).scalar() or 0

        by_type = self.db.query(
            Order.order_type,
            func.count(Order.id),
            func.sum(Order.total_amount),
        ).filter(date_filter).group_by(Order.order_type).all()

        return {
            "total_orders": total,
            "completed_orders": completed,
            "pending_orders": pending,
            "total_revenue": float(total_revenue),
            "by_type": [
                {
                    "type": t,
                    "count": c,
                    "revenue": float(r or 0),
                }
                for t, c, r in by_type
            ],
        }

    def occupancy_report(
        self,
        date_from: date,
        date_to: date,
        property_id: Optional[str] = None,
    ) -> dict:
        """Room occupancy metrics."""
        date_filter = and_(
            Reservation.check_in <= date_to,
            Reservation.check_out >= date_from,
            Reservation.status.in_(["CONFIRMED", "CHECKED_IN"]),
        )
        if property_id:
            date_filter = and_(date_filter, Reservation.property_id == property_id)

        total_reservations = self.db.query(func.count(Reservation.id)).filter(
            date_filter
        ).scalar() or 0

        checked_in = self.db.query(func.count(Reservation.id)).filter(
            date_filter, Reservation.status == "CHECKED_IN"
        ).scalar() or 0

        cancelled = self.db.query(func.count(Reservation.id)).filter(
            date_filter, Reservation.status == "CANCELLED"
        ).scalar() or 0

        return {
            "total_reservations": total_reservations,
            "checked_in": checked_in,
            "cancelled": cancelled,
            "occupancy_rate": round((checked_in / max(total_reservations, 1)) * 100, 1),
        }

    def top_selling_items(
        self,
        date_from: date,
        date_to: date,
        limit: int = 10,
        property_id: Optional[str] = None,
    ) -> list[dict]:
        """Top selling menu items."""
        date_filter = and_(
            Order.created_at >= datetime.combine(date_from, datetime.min.time()),
            Order.created_at <= datetime.combine(date_to, datetime.max.time()),
            Order.status.in_(["COMPLETED", "DELIVERED"]),
        )
        if property_id:
            date_filter = and_(date_filter, Order.property_id == property_id)

        from app.models.order import OrderItem
        from app.models.menu import MenuItem

        results = (
            self.db.query(
                MenuItem.name,
                func.sum(OrderItem.quantity).label("qty"),
                func.count(Order.id).label("order_count"),
            )
            .join(OrderItem, OrderItem.menu_item_id == MenuItem.id)
            .join(Order, Order.id == OrderItem.order_id)
            .filter(date_filter)
            .group_by(MenuItem.name)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(limit)
            .all()
        )

        return [
            {"name": name, "quantity": int(qty), "order_count": int(count)}
            for name, qty, count in results
        ]

    def staff_productivity(
        self,
        date_from: date,
        date_to: date,
        property_id: Optional[str] = None,
    ) -> list[dict]:
        """Staff task completion metrics."""
        date_filter = and_(
            Task.created_at >= datetime.combine(date_from, datetime.min.time()),
            Task.created_at <= datetime.combine(date_to, datetime.max.time()),
        )
        if property_id:
            date_filter = and_(date_filter, Task.property_id == property_id)

        results = (
            self.db.query(
                Staff.id,
                func.count(Task.id).label("total_tasks"),
                func.sum(
                    func.cast(Task.status == "COMPLETED", Integer)
                ).label("completed"),
            )
            .join(Task, Task.assigned_staff_id == Staff.id)
            .filter(date_filter)
            .group_by(Staff.id)
            .all()
        )

        return [
            {
                "staff_id": str(staff_id),
                "total_tasks": total,
                "completed": completed or 0,
                "completion_rate": round((completed or 0) / max(total, 1) * 100, 1),
            }
            for staff_id, total, completed in results
        ]

    def low_stock_items(
        self,
        property_id: Optional[str] = None,
    ) -> list[dict]:
        """Inventory items below minimum level."""
        query = self.db.query(InventoryItem).filter(
            InventoryItem.quantity < InventoryItem.min_level,
            InventoryItem.is_active == True,
        )
        if property_id:
            query = query.filter(InventoryItem.property_id == property_id)

        items = query.all()
        return [
            {
                "id": str(item.id),
                "name": item.name,
                "category": item.category,
                "current": float(item.quantity),
                "minimum": float(item.min_level),
                "unit": item.unit,
            }
            for item in items
        ]

    def peak_hours(
        self,
        date_from: date,
        date_to: date,
        property_id: Optional[str] = None,
    ) -> list[dict]:
        """Order volume by hour of day."""
        date_filter = and_(
            Order.created_at >= datetime.combine(date_from, datetime.min.time()),
            Order.created_at <= datetime.combine(date_to, datetime.max.time()),
        )
        if property_id:
            date_filter = and_(date_filter, Order.property_id == property_id)

        results = (
            self.db.query(
                extract("hour", Order.created_at).label("hour"),
                func.count(Order.id).label("count"),
            )
            .filter(date_filter)
            .group_by(extract("hour", Order.created_at))
            .order_by("hour")
            .all()
        )

        return [{"hour": int(r.hour), "order_count": r.count} for r in results]

    def dashboard_summary(
        self,
        today: date,
        property_id: Optional[str] = None,
    ) -> dict:
        """Today's key metrics for dashboard."""
        today_filter = and_(
            func.date(Order.created_at) == today,
        )
        if property_id:
            today_filter = and_(today_filter, Order.property_id == property_id)

        today_revenue = (
            self.db.query(func.sum(Order.total_amount))
            .filter(today_filter, Order.status == "COMPLETED")
            .scalar() or 0
        )
        today_orders = (
            self.db.query(func.count(Order.id))
            .filter(today_filter)
            .scalar() or 0
        )
        pending_tasks = (
            self.db.query(func.count(Task.id))
            .filter(Task.status.in_(["PENDING", "ASSIGNED", "IN_PROGRESS"]))
            .scalar() or 0
        )
        low_stock = (
            self.db.query(func.count(InventoryItem.id))
            .filter(
                InventoryItem.quantity < InventoryItem.min_level,
                InventoryItem.is_active == True,
            )
            .scalar() or 0
        )

        return {
            "today_revenue": float(today_revenue),
            "today_orders": today_orders,
            "pending_tasks": pending_tasks,
            "low_stock_count": low_stock,
        }
