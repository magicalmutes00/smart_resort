"""Tables and Lake zones routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID

from app.core.database import get_db
from app.core.rbac import RequirePermission
from app.models.dining import RestaurantTable, LakeZone, LakeSeat

router = APIRouter()


class TableResponse(BaseModel):
    id: UUID
    table_number: str
    capacity: int
    is_active: bool
    location: Optional[str]
    status: str

    class Config:
        from_attributes = True


class LakeZoneResponse(BaseModel):
    id: UUID
    name: str
    is_active: bool
    seat_count: Optional[int] = 0

    class Config:
        from_attributes = True


@router.get("/restaurant-tables", response_model=dict)
def list_tables(
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current: dict = Depends(RequirePermission("tables.read")),
):
    """List restaurant tables."""
    query = db.query(RestaurantTable)
    if is_active is not None:
        query = query.filter(RestaurantTable.is_active == is_active)
    tables = query.all()
    return {"data": [TableResponse.model_validate(t) for t in tables]}


@router.patch("/restaurant-tables/{table_id}/status")
def update_table_status(
    table_id: UUID,
    status: str = Query(..., pattern="^(AVAILABLE|OCCUPIED|RESERVED)$"),
    db: Session = Depends(get_db),
    current: dict = Depends(RequirePermission("tables.status_update")),
):
    """Update table status."""
    table = db.query(RestaurantTable).filter(RestaurantTable.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    table.status = status
    db.commit()
    return {"id": str(table.id), "status": table.status}


@router.get("/lake-zones", response_model=dict)
def list_lake_zones(
    db: Session = Depends(get_db),
    current: dict = Depends(RequirePermission("lake.read")),
):
    """List lake zones with seat counts."""
    zones = db.query(LakeZone).all()
    result = []
    for zone in zones:
        seat_count = db.query(LakeSeat).filter(LakeSeat.zone_id == zone.id).count()
        result.append({
            "id": str(zone.id),
            "name": zone.name,
            "is_active": zone.is_active,
            "seat_count": seat_count,
        })
    return {"data": result}
