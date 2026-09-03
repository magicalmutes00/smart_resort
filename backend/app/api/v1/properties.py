"""Properties routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from uuid import UUID

from app.core.database import get_db
from app.models.property import Property

router = APIRouter()


class PropertyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    timezone: str = "UTC"


class PropertyResponse(BaseModel):
    id: UUID
    name: str
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    timezone: str
    is_active: bool

    class Config:
        from_attributes = True


@router.get("/", response_model=dict)
def list_properties(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List all properties."""
    query = db.query(Property)
    total = query.count()
    properties = query.offset((page - 1) * limit).limit(limit).all()
    return {
        "data": [PropertyResponse.model_validate(p) for p in properties],
        "meta": {"total": total, "page": page, "per_page": limit}
    }


@router.post("/", response_model=PropertyResponse, status_code=201)
def create_property(property_data: PropertyCreate, db: Session = Depends(get_db)):
    """Create a new property."""
    prop = Property(**property_data.model_dump())
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return PropertyResponse.model_validate(prop)


@router.get("/{property_id}", response_model=PropertyResponse)
def get_property(property_id: UUID, db: Session = Depends(get_db)):
    """Get property by ID."""
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return PropertyResponse.model_validate(prop)
