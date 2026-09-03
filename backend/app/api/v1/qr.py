"""QR code management routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID

from app.core.database import get_db
from app.core.rbac import RequirePermission
from app.models.qr import QRCode

router = APIRouter()


class QRResponse(BaseModel):
    id: UUID
    code: str
    location_type: str
    location_id: UUID
    is_active: bool
    expires_at: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class QRCreate(BaseModel):
    code: str
    location_type: str
    location_id: UUID
    is_active: bool = True
    expires_at: Optional[str] = None


@router.get("/codes", response_model=dict)
def list_codes(
    property_id: Optional[UUID] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current: dict = Depends(RequirePermission("qr.read")),
):
    """List all QR codes."""
    query = db.query(QRCode)
    if property_id:
        query = query.filter(QRCode.property_id == property_id)
    if active_only:
        query = query.filter(QRCode.is_active == True)

    codes = query.all()
    return {"data": [QRResponse.model_validate(c) for c in codes]}


@router.post("/codes", response_model=QRResponse, status_code=201)
def create_code(
    data: QRCreate,
    db: Session = Depends(get_db),
    current: dict = Depends(RequirePermission("qr.create")),
):
    """Create a new QR code."""
    qr = QRCode(
        property_id=current.get("property_id"),
        code=data.code,
        location_type=data.location_type,
        location_id=data.location_id,
        is_active=data.is_active,
    )
    db.add(qr)
    db.commit()
    db.refresh(qr)
    return QRResponse.model_validate(qr)


@router.get("/codes/{qr_id}", response_model=QRResponse)
def get_code(
    qr_id: UUID,
    db: Session = Depends(get_db),
    current: dict = Depends(RequirePermission("qr.read")),
):
    """Get QR code by ID."""
    qr = db.query(QRCode).filter(QRCode.id == qr_id).first()
    if not qr:
        raise HTTPException(status_code=404, detail="QR code not found")
    return QRResponse.model_validate(qr)


@router.patch("/codes/{qr_id}/disable")
def disable_code(
    qr_id: UUID,
    db: Session = Depends(get_db),
    current: dict = Depends(RequirePermission("qr.update")),
):
    """Disable a QR code."""
    qr = db.query(QRCode).filter(QRCode.id == qr_id).first()
    if not qr:
        raise HTTPException(status_code=404, detail="QR code not found")
    qr.is_active = False
    db.commit()
    return {"id": str(qr.id), "is_active": False}
