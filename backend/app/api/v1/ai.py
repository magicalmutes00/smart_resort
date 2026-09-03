"""AI routes — optional forecasting and anomaly detection."""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date

from app.core.database import get_db
from app.core.rbac import RequirePermission
from app.ai.forecasting import AIService

router = APIRouter()


class ForecastResponse(BaseModel):
    value: Optional[float]
    confidence: float
    available: bool


class InventoryForecastResponse(BaseModel):
    days_remaining: Optional[float]
    depletion_date: Optional[str]
    current_stock: Optional[float]
    available: bool


class AnomalyResponse(BaseModel):
    anomaly: bool
    score: float
    direction: Optional[str]
    pct_deviation: Optional[float]
    available: bool


@router.get("/forecast/demand")
async def forecast_demand(
    item_name: str = Query(..., description="Menu item name (partial)"),
    days_back: int = Query(30, ge=7),
    db: Session = Depends(get_db),
    current: dict = Depends(RequirePermission("reports.read")),
):
    """Forecast demand for a menu item."""
    svc = AIService(db)
    result = svc.forecast_demand(item_name, days_back)
    return ForecastResponse(
        value=result.get("value"),
        confidence=result.get("confidence", 0.0),
        available=result.get("available", False),
    )


@router.get("/forecast/inventory-depletion")
async def forecast_inventory_depletion(
    item_name: str = Query(...),
    consumption_per_day: float = Query(0, ge=0),
    db: Session = Depends(get_db),
    current: dict = Depends(RequirePermission("reports.read")),
):
    """Forecast when inventory will run out."""
    svc = AIService(db)
    result = svc.forecast_inventory_depletion(item_name, consumption_per_day)
    return InventoryForecastResponse(
        days_remaining=result.get("days_remaining"),
        depletion_date=result.get("depletion_date"),
        current_stock=result.get("current_stock"),
        available=result.get("available", False),
    )


@router.get("/forecast/tea-demand-tomorrow")
async def forecast_tea_tomorrow(
    db: Session = Depends(get_db),
    current: dict = Depends(RequirePermission("reports.read")),
):
    """Quick tea demand forecast for tomorrow."""
    svc = AIService(db)
    result = svc.forecast_tea_demand_tomorrow()
    return ForecastResponse(
        value=result.get("value"),
        confidence=result.get("confidence", 0.0),
        available=result.get("available", False),
    )


@router.get("/forecast/sales-revenue")
async def forecast_sales(
    days_back: int = Query(30, ge=7),
    db: Session = Depends(get_db),
    current: dict = Depends(RequirePermission("reports.read")),
):
    """Forecast total sales revenue."""
    svc = AIService(db)
    result = svc.forecast_sales_revenue(days_back)
    return ForecastResponse(
        value=result.get("value"),
        confidence=result.get("confidence", 0.0),
        available=result.get("available", False),
    )


@router.get("/anomaly/sales")
async def detect_sales_anomaly(
    item_name: str = Query(...),
    days_back: int = Query(14, ge=7),
    db: Session = Depends(get_db),
    current: dict = Depends(RequirePermission("reports.read")),
):
    """Detect sales anomaly for an item."""
    svc = AIService(db)
    result = svc.detect_sales_anomaly(item_name, days_back)
    return AnomalyResponse(
        anomaly=result.get("anomaly", False),
        score=result.get("score", 0.0),
        direction=result.get("direction"),
        pct_deviation=result.get("pct_deviation"),
        available=result.get("available", False),
    )


@router.get("/forecast/peak-hours")
async def forecast_peak_hours(
    db: Session = Depends(get_db),
    current: dict = Depends(RequirePermission("reports.read")),
):
    """Predict busiest hours today."""
    svc = AIService(db)
    result = svc.peak_hours_forecast()
    return {
        "peak_hours": result.get("peak_hours", []),
        "available": result.get("available", False),
    }
