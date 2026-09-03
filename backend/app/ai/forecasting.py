"""AI forecasting module — optional, modular, never blocks normal operations.

All AI features are additive only. Core operations work without this module.

Features:
- Demand forecasting (cups of tea, meals, etc.)
- Inventory depletion forecasting
- Staff workload forecasting
- Sales revenue forecasting
- Anomaly detection

Implementation uses statistical methods (moving averages, linear regression)
with clean abstraction for plugging in ML models later.
"""
from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from typing import Optional
import math

from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from collections import defaultdict

from app.models.order import Order, OrderItem
from app.models.menu import MenuItem
from app.models.inventory import InventoryItem


# ─── Forecasters ────────────────────────────────────────────────────────────────

class Forecaster(ABC):
    """Base forecaster interface. Swap implementations without changing callers."""

    @abstractmethod
    def forecast(self, days_ahead: int = 1) -> float:
        """Return forecasted value."""
        pass

    @abstractmethod
    def confidence(self) -> float:
        """Return confidence score 0–1."""
        pass


class MovingAverageForecaster(Forecaster):
    """Simple moving average — baseline implementation."""

    def __init__(self, historical_values: list[float]):
        self.values = historical_values

    def forecast(self, days_ahead: int = 1) -> float:
        if not self.values:
            return 0.0
        window = min(7, len(self.values))
        recent = self.values[-window:]
        avg = sum(recent) / len(recent)
        # Simple trend adjustment
        if len(recent) >= 2:
            trend = (recent[-1] - recent[0]) / len(recent)
            return max(0, avg + trend * days_ahead)
        return avg

    def confidence(self) -> float:
        if len(self.values) < 7:
            return 0.3
        if len(self.values) < 30:
            return 0.6
        return 0.8


class LinearRegressionForecaster(Forecaster):
    """Simple linear regression for trend-based forecasting."""

    def __init__(self, historical_values: list[float]):
        self.values = historical_values

    def forecast(self, days_ahead: int = 1) -> float:
        if len(self.values) < 3:
            return sum(self.values) / max(len(self.values), 1)

        n = len(self.values)
        x = list(range(n))
        y = self.values

        x_mean = sum(x) / n
        y_mean = sum(y) / n

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return y_mean

        slope = numerator / denominator
        intercept = y_mean - slope * x_mean

        return max(0, intercept + slope * (n - 1 + days_ahead))

    def confidence(self) -> float:
        # R² would require full regression — simplified confidence
        if len(self.values) < 14:
            return 0.4
        return 0.75


# ─── AI Service ────────────────────────────────────────────────────────────────

class AIService:
    """
    Optional AI layer. All methods return None or fallback data on failure.
    Never raises — AI is always optional.
    """

    def __init__(self, db: Session):
        self.db = db

    def _safe_forecast(self, forecaster: Forecaster) -> dict:
        """Wrap forecaster with error handling."""
        try:
            value = forecaster.forecast(days_ahead=1)
            confidence = forecaster.confidence()
            return {"value": round(value, 2), "confidence": confidence, "available": True}
        except Exception:
            return {"value": None, "confidence": 0.0, "available": False}

    def forecast_demand(
        self,
        menu_item_name: str,
        days_back: int = 30,
    ) -> dict:
        """Forecast demand for a specific menu item.

        Returns: {value: int, confidence: float, available: bool}
        """
        try:
            since = datetime.utcnow() - timedelta(days=days_back)
            results = (
                self.db.query(
                    func.date(Order.created_at).label("d"),
                    func.sum(OrderItem.quantity).label("qty"),
                )
                .join(OrderItem, OrderItem.order_id == Order.id)
                .join(MenuItem, MenuItem.id == OrderItem.menu_item_id)
                .filter(
                    MenuItem.name.ilike(f"%{menu_item_name}%"),
                    Order.created_at >= since,
                    Order.status.in_(["COMPLETED", "DELIVERED"]),
                )
                .group_by(func.date(Order.created_at))
                .order_by("d")
                .all()
            )

            if not results:
                return {"value": None, "confidence": 0.0, "available": False}

            daily_values = [float(r.qty or 0) for r in results]
            forecaster = MovingAverageForecaster(daily_values)
            return self._safe_forecast(forecaster)
        except Exception:
            return {"value": None, "confidence": 0.0, "available": False}

    def forecast_tea_demand_tomorrow(self) -> dict:
        """Quick forecast for tea demand tomorrow."""
        return self.forecast_demand("tea", days_back=30)

    def forecast_sales_revenue(
        self,
        days_back: int = 30,
    ) -> dict:
        """Forecast total sales revenue for tomorrow."""
        try:
            since = datetime.utcnow() - timedelta(days=days_back)
            results = (
                self.db.query(
                    func.date(Order.created_at).label("d"),
                    func.sum(Order.total_amount).label("revenue"),
                )
                .filter(
                    Order.created_at >= since,
                    Order.status.in_(["COMPLETED", "DELIVERED"]),
                )
                .group_by(func.date(Order.created_at))
                .order_by("d")
                .all()
            )

            if not results:
                return {"value": None, "confidence": 0.0, "available": False}

            revenue_values = [float(r.revenue or 0) for r in results]
            forecaster = LinearRegressionForecaster(revenue_values)
            return self._safe_forecast(forecaster)
        except Exception:
            return {"value": None, "confidence": 0.0, "available": False}

    def forecast_inventory_depletion(
        self,
        item_name: str,
        consumption_per_day: float,
    ) -> dict:
        """Forecast when an inventory item will run out.

        Args:
            item_name: Name of the inventory item
            consumption_per_day: Estimated daily consumption
        """
        try:
            item = self.db.query(InventoryItem).filter(
                InventoryItem.name.ilike(f"%{item_name}%"),
                InventoryItem.is_active == True,
            ).first()

            if not item:
                return {"days_remaining": None, "depletion_date": None, "available": False}

            current = float(item.quantity)
            consumption = consumption_per_day or (current / 30)  # fallback

            if consumption <= 0:
                return {"days_remaining": None, "depletion_date": None, "available": False}

            days_remaining = current / consumption
            depletion_date = date.today() + timedelta(days=int(days_remaining))

            return {
                "days_remaining": round(days_remaining, 1),
                "depletion_date": depletion_date.isoformat(),
                "current_stock": current,
                "estimated_daily_use": consumption,
                "available": True,
            }
        except Exception:
            return {"days_remaining": None, "depletion_date": None, "available": False}

    def detect_sales_anomaly(
        self,
        item_name: str,
        days_back: int = 14,
    ) -> dict:
        """Detect if sales for an item are unusually high or low.

        Returns anomaly score and direction.
        """
        try:
            since = datetime.utcnow() - timedelta(days=days_back)
            results = (
                self.db.query(
                    func.date(Order.created_at).label("d"),
                    func.sum(OrderItem.quantity).label("qty"),
                )
                .join(OrderItem, OrderItem.order_id == Order.id)
                .join(MenuItem, MenuItem.id == OrderItem.menu_item_id)
                .filter(
                    MenuItem.name.ilike(f"%{item_name}%"),
                    Order.created_at >= since,
                )
                .group_by(func.date(Order.created_at))
                .all()
            )

            if not results or len(results) < 3:
                return {"anomaly": False, "score": 0.0, "direction": None, "available": False}

            values = [float(r.qty or 0) for r in results]
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            std_dev = math.sqrt(variance) if variance > 0 else 1

            # Today's (or last day's) value
            latest = values[-1]
            z_score = (latest - mean) / std_dev if std_dev > 0 else 0

            # Flag if |z| > 1.5 (unusual)
            is_anomaly = abs(z_score) > 1.5
            direction = "high" if z_score > 0 else "low"
            pct_diff = round((z_score / mean * 100) if mean > 0 else 0, 1)

            return {
                "anomaly": is_anomaly,
                "score": round(z_score, 2),
                "direction": direction,
                "pct_deviation": pct_diff,
                "available": True,
            }
        except Exception:
            return {"anomaly": False, "score": 0.0, "direction": None, "available": False}

    def peak_hours_forecast(self) -> dict:
        """Predict which hours will be busiest today."""
        try:
            today = date.today()
            results = (
                self.db.query(
                    func.extract("hour", Order.created_at).label("hour"),
                    func.count(Order.id).label("count"),
                )
                .filter(
                    func.date(Order.created_at) == today,
                )
                .group_by(func.extract("hour", Order.created_at))
                .order_by(func.count(Order.id).desc())
                .limit(3)
                .all()
            )

            if not results:
                return {"peak_hours": [], "available": False}

            return {
                "peak_hours": [{"hour": int(r.hour), "orders": r.count} for r in results],
                "available": True,
            }
        except Exception:
            return {"peak_hours": [], "available": False}
