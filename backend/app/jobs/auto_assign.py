"""Scheduled job: auto-assign pending work and escalate stale tasks.

Designed to run every 15 minutes from a scheduler (Render Cron Job):

    python -m app.jobs.auto_assign

What it does, in order, inside a single transaction:

1. Auto-assigns PENDING ``tasks`` to the least-loaded active staff member in the
   matching department and notifies them.
2. Auto-assigns PENDING ``housekeeping_tasks`` to housekeeping staff.
3. Auto-assigns PENDING ``maintenance_requests`` to maintenance staff.
4. Escalates work that has been open longer than ``CRON_ESCALATE_AFTER_MINUTES``
   by bumping its priority one step and notifying managers.
5. Flags food orders stuck in a non-terminal status (notifying assigned staff
   and managers) without changing order status.

Every action is recorded in ``audit_logs`` so there is a trail of who/what/when.
The job is idempotent: re-running it does not create duplicate assignments.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Iterable, Optional
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.audit import AuditLog, Notification
from app.models.housekeeping import HousekeepingTask
from app.models.maintenance import MaintenanceRequest
from app.models.order import Order
from app.models.role import Role
from app.models.staff import Staff
from app.models.task import Task, TaskAssignment
from app.models.user import User

logger = logging.getLogger("smartresort.cron")

# Statuses that still count as "open work" for workload balancing.
OPEN_STATUSES = ("PENDING", "ASSIGNED", "ACCEPTED", "IN_PROGRESS")

# task.type -> candidate staff departments (the seed stores the role name in
# staff.department, e.g. "HOUSEKEEPING" / "DELIVERY_STAFF").
TYPE_DEPARTMENTS: dict[str, tuple[str, ...]] = {
    "DELIVERY": ("DELIVERY_STAFF", "DELIVERY"),
    "HOUSEKEEPING": ("HOUSEKEEPING",),
    "MAINTENANCE": ("MAINTENANCE",),
    "KITCHEN": ("KITCHEN",),
    "SERVICE": ("WAITER", "SERVICE"),
}

# Ordered escalation ladder for task priority.
PRIORITY_LADDER = ("LOW", "NORMAL", "HIGH", "URGENT")


def _next_priority(priority: Optional[str]) -> Optional[str]:
    """Return the next priority up the ladder, or None if already at the top."""
    try:
        idx = PRIORITY_LADDER.index((priority or "NORMAL").upper())
    except ValueError:
        idx = PRIORITY_LADDER.index("NORMAL")
    if idx >= len(PRIORITY_LADDER) - 1:
        return None
    return PRIORITY_LADDER[idx + 1]


def _open_load(db: Session, staff_id: UUID) -> int:
    """Number of open work items currently assigned to a staff member."""
    return (
        db.query(Task).filter(
            Task.assigned_staff_id == staff_id, Task.status.in_(OPEN_STATUSES)
        ).count()
        + db.query(HousekeepingTask).filter(
            HousekeepingTask.assigned_staff_id == staff_id,
            HousekeepingTask.status.in_(OPEN_STATUSES),
        ).count()
        + db.query(MaintenanceRequest).filter(
            MaintenanceRequest.assigned_staff_id == staff_id,
            MaintenanceRequest.status.in_(OPEN_STATUSES),
        ).count()
    )


def _least_loaded_staff(
    db: Session, departments: Iterable[str]
) -> Optional[Staff]:
    """Pick the active staff member with the fewest open items."""
    staff_list = (
        db.query(Staff)
        .filter(
            Staff.is_active.is_(True),
            func.upper(Staff.department).in_([d.upper() for d in departments]),
        )
        .all()
    )
    if not staff_list:
        return None

    best: Optional[Staff] = None
    best_load = float("inf")
    for staff in staff_list:
        load = _open_load(db, staff.id)
        if load < best_load:
            best, best_load = staff, load
    return best


def _notify(
    db: Session,
    *,
    staff: Optional[Staff],
    user_id: Optional[UUID],
    property_id: Optional[UUID],
    title: str,
    body: str,
    kind: str,
    data: Optional[dict] = None,
) -> None:
    db.add(
        Notification(
            user_id=user_id or (staff.user_id if staff else None),
            staff_id=staff.id if staff else None,
            property_id=property_id,
            title=title,
            body=body,
            type=kind,
            is_read=False,
            data=data or {},
        )
    )


def _managers(db: Session, property_id: Optional[UUID]) -> list[User]:
    query = db.query(User).join(Role, User.role_id == Role.id).filter(
        Role.name.in_(("MANAGER", "OWNER", "SUPER_ADMIN")),
        User.is_active.is_(True),
    )
    if property_id is not None:
        query = query.filter(User.property_id == property_id)
    return query.all()


def _audit(db: Session, action: str, entity: str, entity_id: UUID, new_value: dict) -> None:
    db.add(
        AuditLog(action=action, entity=entity, entity_id=entity_id, new_value=new_value)
    )


# --------------------------------------------------------------------------- #
# Assignment steps
# --------------------------------------------------------------------------- #
def assign_tasks(db: Session, summary: dict) -> None:
    """Auto-assign PENDING general tasks."""
    tasks = (
        db.query(Task)
        .filter(Task.status == "PENDING", Task.assigned_staff_id.is_(None))
        .limit(settings.CRON_BATCH_SIZE)
        .all()
    )
    for task in tasks:
        departments = TYPE_DEPARTMENTS.get((task.type or "").upper(), ("SERVICE",))
        staff = _least_loaded_staff(db, departments)
        if staff is None:
            summary["unassignable"] += 1
            continue

        task.assigned_staff_id = staff.id
        task.status = "ASSIGNED"
        db.add(TaskAssignment(task_id=task.id, staff_id=staff.id))
        _notify(
            db,
            staff=staff,
            user_id=staff.user_id,
            property_id=task.property_id,
            title=f"New {task.type} task assigned",
            body=task.notes or f"A {task.priority.lower()} priority task needs attention.",
            kind="TASK_ASSIGNED",
            data={"task_id": str(task.id), "type": task.type},
        )
        _audit(
            db,
            "TASK_AUTO_ASSIGNED",
            "task",
            task.id,
            {"staff_id": str(staff.id), "status": "ASSIGNED"},
        )
        summary["tasks_assigned"] += 1


def assign_housekeeping(db: Session, summary: dict) -> None:
    """Auto-assign PENDING housekeeping tasks."""
    items = (
        db.query(HousekeepingTask)
        .filter(
            HousekeepingTask.status == "PENDING",
            HousekeepingTask.assigned_staff_id.is_(None),
        )
        .limit(settings.CRON_BATCH_SIZE)
        .all()
    )
    for item in items:
        staff = _least_loaded_staff(db, ("HOUSEKEEPING",))
        if staff is None:
            summary["unassignable"] += 1
            continue
        item.assigned_staff_id = staff.id
        item.status = "ASSIGNED"
        _notify(
            db,
            staff=staff,
            user_id=staff.user_id,
            property_id=item.property_id,
            title=f"New housekeeping task ({item.task_type})",
            body=item.notes or "A room needs cleaning.",
            kind="HOUSEKEEPING_ASSIGNED",
            data={"housekeeping_task_id": str(item.id)},
        )
        _audit(
            db,
            "HOUSEKEEPING_AUTO_ASSIGNED",
            "housekeeping_task",
            item.id,
            {"staff_id": str(staff.id), "status": "ASSIGNED"},
        )
        summary["housekeeping_assigned"] += 1


def assign_maintenance(db: Session, summary: dict) -> None:
    """Auto-assign PENDING maintenance requests."""
    items = (
        db.query(MaintenanceRequest)
        .filter(
            MaintenanceRequest.status == "PENDING",
            MaintenanceRequest.assigned_staff_id.is_(None),
        )
        .limit(settings.CRON_BATCH_SIZE)
        .all()
    )
    for item in items:
        staff = _least_loaded_staff(db, ("MAINTENANCE",))
        if staff is None:
            summary["unassignable"] += 1
            continue
        item.assigned_staff_id = staff.id
        item.status = "ASSIGNED"
        _notify(
            db,
            staff=staff,
            user_id=staff.user_id,
            property_id=item.property_id,
            title="New maintenance request",
            body=item.description or "A maintenance request needs attention.",
            kind="MAINTENANCE_ASSIGNED",
            data={"maintenance_request_id": str(item.id)},
        )
        _audit(
            db,
            "MAINTENANCE_AUTO_ASSIGNED",
            "maintenance_request",
            item.id,
            {"staff_id": str(staff.id), "status": "ASSIGNED"},
        )
        summary["maintenance_assigned"] += 1


# --------------------------------------------------------------------------- #
# Escalation step
# --------------------------------------------------------------------------- #
def escalate_tasks(db: Session, summary: dict, now: datetime) -> None:
    """Bump priority of stale open tasks and notify managers.

    Uses ``updated_at`` as the idle marker so a task escalates at most once per
    escalation window (changing priority refreshes ``updated_at``).
    """
    cutoff = now - timedelta(minutes=settings.CRON_ESCALATE_AFTER_MINUTES)
    stale = (
        db.query(Task)
        .filter(
            Task.status.in_(OPEN_STATUSES),
            Task.priority != "URGENT",
            Task.updated_at < cutoff,
        )
        .limit(settings.CRON_BATCH_SIZE)
        .all()
    )
    for task in stale:
        new_priority = _next_priority(task.priority)
        if new_priority is None:
            continue
        old_priority = task.priority
        task.priority = new_priority
        for manager in _managers(db, task.property_id):
            _notify(
                db,
                staff=None,
                user_id=manager.id,
                property_id=task.property_id,
                title=f"Task escalated to {new_priority}",
                body=(
                    f"A {task.type} task has been open for over "
                    f"{settings.CRON_ESCALATE_AFTER_MINUTES} minutes."
                ),
                kind="TASK_ESCALATED",
                data={"task_id": str(task.id), "from": old_priority, "to": new_priority},
            )
        _audit(
            db,
            "TASK_ESCALATED",
            "task",
            task.id,
            {"priority_from": old_priority, "priority_to": new_priority},
        )
        summary["escalated"] += 1


# --------------------------------------------------------------------------- #
# Food-order status check
# --------------------------------------------------------------------------- #
FOOD_ORDER_TERMINAL_STATUSES = ("COMPLETED", "CANCELLED")


def flag_stale_food_orders(db: Session, summary: dict, now: datetime) -> None:
    """Flag food orders stuck in a non-terminal status.

    This only checks and notifies; it never changes order status. It records one
    ``ORDER_STALE_FLAGGED`` audit per order/status snapshot so reruns do not spam
    recipients while an order stays untouched.
    """
    window_minutes = settings.CRON_ESCALATE_AFTER_MINUTES
    cutoff = now - timedelta(minutes=window_minutes)
    idle = func.coalesce(Order.updated_at, Order.created_at)
    stale = (
        db.query(Order)
        .filter(
            Order.status.notin_(FOOD_ORDER_TERMINAL_STATUSES),
            idle < cutoff,
        )
        .order_by(idle.asc())
        .limit(settings.CRON_BATCH_SIZE)
        .all()
    )
    if not stale:
        return

    latest_flag = {}
    for flag in (
        db.query(AuditLog)
        .filter(
            AuditLog.action == "ORDER_STALE_FLAGGED",
            AuditLog.entity == "order",
            AuditLog.entity_id.in_([order.id for order in stale]),
        )
        .order_by(AuditLog.created_at.desc())
        .all()
    ):
        if flag.entity_id not in latest_flag:
            latest_flag[flag.entity_id] = flag

    for order in stale:
        marker = order.updated_at or order.created_at
        if marker is None:
            continue
        marker_iso = marker.isoformat()
        previous_flag = latest_flag.get(order.id)
        previous_value = (previous_flag.new_value or {}) if previous_flag else {}
        if (
            previous_value.get("status") == order.status
            and previous_value.get("order_updated_at") == marker_iso
        ):
            continue

        age_minutes = max(0, int((now - marker).total_seconds() // 60))
        payload = {
            "order_id": str(order.id),
            "order_number": order.order_number,
            "status": order.status,
            "order_type": order.order_type,
            "age_minutes": age_minutes,
            "property_id": str(order.property_id) if order.property_id else None,
            "staff_id": str(order.staff_id) if order.staff_id else None,
        }
        notified_user_ids = set()
        if order.staff_id is not None:
            staff = (
                db.query(Staff)
                .filter(Staff.id == order.staff_id, Staff.is_active.is_(True))
                .first()
            )
            if staff is not None and staff.user_id is not None:
                _notify(
                    db,
                    staff=staff,
                    user_id=staff.user_id,
                    property_id=order.property_id,
                    title=f"Food order {order.order_number} stuck in {order.status}",
                    body=(
                        f"Food order {order.order_number} ({order.order_type}) has been in "
                        f"{order.status} for {age_minutes} minutes."
                    ),
                    kind="ORDER_STALE",
                    data=payload,
                )
                notified_user_ids.add(staff.user_id)
        for manager in _managers(db, order.property_id):
            if manager.id in notified_user_ids:
                continue
            _notify(
                db,
                staff=None,
                user_id=manager.id,
                property_id=order.property_id,
                title=f"Food order {order.order_number} stuck in {order.status}",
                body=(
                    f"Food order {order.order_number} ({order.order_type}) has been in "
                    f"{order.status} for {age_minutes} minutes."
                ),
                kind="ORDER_STALE",
                data=payload,
            )
            notified_user_ids.add(manager.id)
        _audit(
            db,
            "ORDER_STALE_FLAGGED",
            "order",
            order.id,
            {
                "status": order.status,
                "order_updated_at": marker_iso,
                "age_minutes": age_minutes,
                "notified_user_ids": sorted(
                    str(user_id) for user_id in notified_user_ids
                ),
            },
        )
        summary["food_orders_flagged"] += 1


# --------------------------------------------------------------------------- #
# Entrypoint
# --------------------------------------------------------------------------- #
def run() -> dict:
    """Execute all scheduled steps and return a summary of what happened."""
    summary = {
        "tasks_assigned": 0,
        "housekeeping_assigned": 0,
        "maintenance_assigned": 0,
        "escalated": 0,
        "food_orders_flagged": 0,
        "unassignable": 0,
    }
    now = datetime.utcnow()
    db = SessionLocal()
    try:
        assign_tasks(db, summary)
        assign_housekeeping(db, summary)
        assign_maintenance(db, summary)
        escalate_tasks(db, summary, now)
        flag_stale_food_orders(db, summary, now)
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("auto_assign job failed; transaction rolled back")
        raise
    finally:
        db.close()

    logger.info(
        "auto_assign complete: %s assigned, %s housekeeping, %s maintenance, "
        "%s escalated, %s food orders flagged, %s unassignable",
        summary["tasks_assigned"],
        summary["housekeeping_assigned"],
        summary["maintenance_assigned"],
        summary["escalated"],
        summary["food_orders_flagged"],
        summary["unassignable"],
    )
    return summary


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s",
    )
    summary = run()
    print("auto_assign summary:", summary)


if __name__ == "__main__":
    main()
