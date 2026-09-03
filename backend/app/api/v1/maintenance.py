"""Maintenance routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID

from app.core.database import get_db
from app.models.maintenance import MaintenanceRequest

router = APIRouter()


class MaintenanceRequestResponse(BaseModel):
    id: UUID
    room_id: Optional[UUID]
    description: str
    priority: str
    status: str
    assigned_staff_id: Optional[UUID]
    resolution_notes: Optional[str]

    class Config:
        from_attributes = True


@router.get("/requests", response_model=dict)
def list_maintenance_requests(
    status: Optional[str] = None,
    room_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """List maintenance requests."""
    query = db.query(MaintenanceRequest)
    if status:
        query = query.filter(MaintenanceRequest.status == status)
    if room_id:
        query = query.filter(MaintenanceRequest.room_id == room_id)

    requests = query.order_by(MaintenanceRequest.created_at.desc()).all()
    return {"data": [MaintenanceRequestResponse.model_validate(r) for r in requests]}


@router.post("/requests", status_code=201)
def create_maintenance_request(
    room_id: UUID = Query(...),
    description: str = Query(...),
    priority: str = Query("NORMAL"),
    db: Session = Depends(get_db)
):
    """Create a maintenance request."""
    request = MaintenanceRequest(
        room_id=room_id,
        description=description,
        priority=priority,
        status="PENDING"
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return MaintenanceRequestResponse.model_validate(request)


@router.patch("/requests/{request_id}/status")
def update_maintenance_status(
    request_id: UUID,
    status: str = Query(...),
    resolution_notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Update maintenance request status."""
    request = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    request.status = status
    if resolution_notes:
        request.resolution_notes = resolution_notes
    db.commit()
    return {"id": request.id, "status": request.status}
