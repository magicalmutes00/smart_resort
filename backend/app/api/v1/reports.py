"""Reports and analytics routes."""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID

from app.core.database import get_db
from app.core.rbac import RequirePermission
from app.services.analytics import AnalyticsService

router = APIRouter()


class RevenueReportResponse(BaseModel):
    date: str
    revenue: float


class OrdersSummaryResponse(BaseModel):
    total_orders: int
    completed_orders: int
    pending_orders: int
    total_revenue: float
    by_type: list[dict]


class OccupancyResponse(BaseModel):
    total_reservations: int
    checked_in: int
    cancelled: int
    occupancy_rate: float


@router.get("/revenue")
def get_revenue(
    date_from: date = Query(...),
    date_to: date = Query(...),
    group_by: str = Query("day", pattern="^(day|week|month)$"),
    property_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current: dict = Depends(RequirePermission("reports.read")),
):
    """Revenue report by period."""
    svc = AnalyticsService(db)
    return svc.revenue_report(
        date_from=date_from,
        date_to=date_to,
        group_by=group_by,
        property_id=str(property_id) if property_id else None,
    )


@router.get("/orders-summary")
def get_orders_summary(
    date_from: date = Query(...),
    date_to: date = Query(...),
    property_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current: dict = Depends(RequirePermission("reports.read")),
):
    """Order counts and revenue."""
    svc = AnalyticsService(db)
    return svc.orders_summary(
        date_from=date_from,
        date_to=date_to,
        property_id=str(property_id) if property_id else None,
    )


@router.get("/occupancy")
def get_occupancy(
    date_from: date = Query(...),
    date_to: date = Query(...),
    property_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current: dict = Depends(RequirePermission("reports.read")),
):
    """Occupancy metrics."""
    svc = AnalyticsService(db)
    return svc.occupancy_report(
        date_from=date_from,
        date_to=date_to,
        property_id=str(property_id) if property_id else None,
    )


@router.get("/low-stock")
def get_low_stock(
    property_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current: dict = Depends(RequirePermission("reports.read")),
):
    """Low stock items."""
    svc = AnalyticsService(db)
    return svc.low_stock_items(str(property_id) if property_id else None)


@router.get("/dashboard")
def get_dashboard_summary(
    property_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current: dict = Depends(RequirePermission("reports.read")),
):
    """Today's dashboard metrics."""
    from datetime import date
    svc = AnalyticsService(db)
    return svc.dashboard_summary(
        today=date.today(),
        property_id=str(property_id) if property_id else None,
    )
