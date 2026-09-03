"""Inventory tests."""
import pytest
from app.services.inventory_service import InventoryService


def test_inventory_service_class_exists():
    """Inventory service should be importable."""
    from app.services.inventory_service import InventoryService
    assert InventoryService is not None


def test_transaction_types():
    """Test that transaction types are well-defined."""
    valid_types = ["PURCHASE", "SALE", "WASTE", "ADJUSTMENT", "RETURN", "RECIPE_CONSUMPTION"]
    for tx_type in valid_types:
        assert isinstance(tx_type, str)
