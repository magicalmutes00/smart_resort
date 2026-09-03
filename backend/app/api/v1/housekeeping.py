"""Housekeeping routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID

from app.core.database import get_db
from app.models.housekeeping import HousekeepingTask

router = APIRouter()


class HousekeepingTaskResponse(BaseModel):
    id: UUID
    room_id: Optional[UUID]
    task_type: str
    status: str
    priority: str
    notes: Optional[str]
    assigned_staff_id: Optional[UUID]

    class Config:
        from_attributes = True


@router.get("/tasks", response_model=dict)
def list_housekeeping_tasks(
    status: Optional[str] = None,
    room_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """List housekeeping tasks."""
    query = db.query(HousekeepingTask)
    if status:
        query = query.filter(HousekeepingTask.status == status)
    if room_id:
        query = query.filter(HousekeepingTask.room_id == room_id)

    tasks = query.order_by(HousekeepingTask.created_at.desc()).all()
    return {"data": [HousekeepingTaskResponse.model_validate(t) for t in tasks]}


@router.post("/tasks", status_code=201)
def create_housekeeping_task(
    task_type: str = Query(...),
    room_id: UUID = Query(...),
    priority: str = Query("NORMAL"),
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Create a housekeeping task."""
    task = HousekeepingTask(
        task_type=task_type,
        room_id=room_id,
        priority=priority,
        notes=notes,
        status="PENDING"
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return HousekeepingTaskResponse.model_validate(task)


@router.patch("/tasks/{task_id}/status")
def update_housekeeping_status(
    task_id: UUID,
    status: str = Query(...),
    db: Session = Depends(get_db)
):
    """Update housekeeping task status."""
    task = db.query(HousekeepingTask).filter(HousekeepingTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = status
    db.commit()
    return {"id": task.id, "status": task.status}
