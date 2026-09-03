"""Staff auto-assignment service (rule-based, extensible to ML)."""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.staff import Staff
from app.models.task import Task


class AutoAssignmentService:
    """Rule-based staff assignment with extensible hooks for intelligent assignment."""

    # Rules: department match, active staff, lower current workload first
    @staticmethod
    def assign_task(
        db: Session,
        task: Task,
        property_id: Optional[str] = None,
    ) -> Optional[Staff]:
        """Assign task to best available staff member."""
        dept = task.type  # Simplified: use task type as department
        if dept == "DELIVERY":
            dept = "Delivery"
        elif dept == "HOUSEKEEPING":
            dept = "Housekeeping"
        elif dept == "MAINTENANCE":
            dept = "Maintenance"
        else:
            dept = "Service"

        # Find active staff in department with lowest open task count
        staff_list = db.query(Staff).filter(
            Staff.is_active == True,
            Staff.department.ilike(f"%{dept}%")
        ).all()

        if not staff_list:
            return None

        # Count open tasks per staff
        best = None
        best_load = float('inf')
        for s in staff_list:
            open_tasks = db.query(Task).filter(
                Task.assigned_staff_id == s.id,
                Task.status.in_(["PENDING", "ASSIGNED", "IN_PROGRESS"])
            ).count()
            if open_tasks < best_load:
                best_load = open_tasks
                best = s

        if best:
            task.assigned_staff_id = best.id
            task.status = "ASSIGNED"
            db.commit()
            return best

        return None
