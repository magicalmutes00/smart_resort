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
# Entrypoint
# --------------------------------------------------------------------------- #
def run() -> dict:
    """Execute all scheduled steps and return a summary of what happened."""
    summary = {
        "tasks_assigned": 0,
        "housekeeping_assigned": 0,
        "maintenance_assigned": 0,
        "escalated": 0,
        "unassignable": 0,
    }
    now = datetime.utcnow()
    db = SessionLocal()
    try:
        assign_tasks(db, summary)
        assign_housekeeping(db, summary)
        assign_maintenance(db, summary)
        escalate_tasks(db, summary, now)
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("auto_assign job failed; transaction rolled back")
        raise
    finally:
        db.close()

    logger.info(
        "auto_assign complete: %s assigned, %s housekeeping, %s maintenance, "
        "%s escalated, %s unassignable",
        summary["tasks_assigned"],
        summary["housekeeping_assigned"],
        summary["maintenance_assigned"],
        summary["escalated"],
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
