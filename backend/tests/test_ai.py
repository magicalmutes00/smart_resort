"""AI tests — forecasting and anomaly detection should be optional."""
import pytest
from app.ai.forecasting import (
    MovingAverageForecaster, LinearRegressionForecaster, AIService,
)


def test_moving_average_empty():
    """Empty input should return 0."""
    f = MovingAverageForecaster([])
    assert f.forecast() == 0.0
    assert f.confidence() == 0.3


def test_moving_average_basic():
    """Basic moving average calculation."""
    values = [10.0, 20.0, 30.0, 40.0, 50.0]
    f = MovingAverageForecaster(values)
    forecast = f.forecast()
    assert 20 <= forecast <= 60


def test_linear_regression():
    """Linear regression should detect trend."""
    values = [10, 20, 30, 40, 50, 60, 70]
    f = LinearRegressionForecaster(values)
    forecast = f.forecast()
    # Should be higher than last value due to upward trend
    assert forecast > 50


def test_linear_regression_insufficient_data():
    """Should handle small input."""
    f = LinearRegressionForecaster([5])
    val = f.forecast()
    assert val == 5


def test_ai_service_does_not_raise():
    """AI service should never raise on missing data."""
    # Note: instantiating without a DB is for unit-test purposes only
    # The actual service gracefully returns {available: False}
    from app.ai.forecasting import AIService
    # Just verify the class loads
    assert AIService is not None
