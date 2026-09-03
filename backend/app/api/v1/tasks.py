"""Tasks routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.models.task import Task, TaskAssignment

router = APIRouter()

TASK_STATUSES = ["PENDING", "ASSIGNED", "ACCEPTED", "IN_PROGRESS", "COMPLETED", "CANCELLED"]
TASK_TYPES = ["DELIVERY", "HOUSEKEEPING", "MAINTENANCE", "SERVICE", "KITCHEN"]
PRIORITIES = ["LOW", "NORMAL", "HIGH", "URGENT"]


class TaskCreate(BaseModel):
    type: str = Field(..., pattern="^(DELIVERY|HOUSEKEEPING|MAINTENANCE|SERVICE|KITCHEN)$")
    location_type: Optional[str] = None
    location_id: Optional[UUID] = None
    priority: str = Field(default="NORMAL", pattern="^(LOW|NORMAL|HIGH|URGENT)$")
    notes: Optional[str] = None


class TaskResponse(BaseModel):
    id: UUID
    type: str
    location_type: Optional[str]
    location_id: Optional[UUID]
    priority: str
    status: str
    notes: Optional[str]
    assigned_staff_id: Optional[UUID]
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task."""
    task = Task(**task_data.model_dump(), status="PENDING")
    db.add(task)
    db.commit()
    db.refresh(task)
    return TaskResponse.model_validate(task)


@router.get("/", response_model=dict)
def list_tasks(
    status: Optional[str] = None,
    assigned_to: Optional[UUID] = None,
    type: Optional[str] = Query(None, alias="type"),
    priority: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List tasks."""
    query = db.query(Task)
    if status:
        query = query.filter(Task.status == status)
    if assigned_to:
        query = query.filter(Task.assigned_staff_id == assigned_to)
    if type:
        query = query.filter(Task.type == type)
    if priority:
        query = query.filter(Task.priority == priority)

    query = query.order_by(Task.created_at.desc())
    total = query.count()
    tasks = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "data": [TaskResponse.model_validate(t) for t in tasks],
        "meta": {"total": total, "page": page, "per_page": limit}
    }


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: UUID, db: Session = Depends(get_db)):
    """Get task by ID."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task)


@router.patch("/{task_id}/status")
def update_task_status(
    task_id: UUID,
    status: str = Query(...),
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Update task status."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if status not in TASK_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status")

    task.status = status
    if notes:
        task.notes = notes
    db.commit()

    return {"id": task.id, "status": task.status}


@router.post("/{task_id}/assign")
def assign_task(task_id: UUID, staff_id: UUID, db: Session = Depends(get_db)):
    """Assign task to staff."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.assigned_staff_id = staff_id
    task.status = "ASSIGNED"
    db.add(TaskAssignment(task_id=task_id, staff_id=staff_id))
    db.commit()

    return {"id": task.id, "assigned_to": staff_id, "status": task.status}
