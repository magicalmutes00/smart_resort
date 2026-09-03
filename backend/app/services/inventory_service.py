"""Inventory service with recipe-based consumption."""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.inventory import InventoryItem, InventoryTransaction


class InventoryService:
    """Service for inventory management and recipe-based consumption."""

    def __init__(self, db: Session):
        self.db = db

    def create_item(
        self,
        name: str,
        category: str,
        unit: str,
        property_id: Optional[str] = None,
        quantity: float = 0,
        min_level: float = 0,
        max_level: Optional[float] = None,
        cost_per_unit: float = 0,
    ) -> InventoryItem:
        """Create a new inventory item."""
        item = InventoryItem(
            property_id=property_id,
            name=name,
            category=category,
            unit=unit,
            quantity=quantity,
            min_level=min_level,
            max_level=max_level,
            cost_per_unit=cost_per_unit,
            is_active=True,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def adjust_stock(
        self,
        item_id: str,
        quantity: float,
        transaction_type: str,
        reference_id: Optional[str] = None,
        notes: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> InventoryItem:
        """Record a stock movement transaction."""
        item = self.db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
        if not item:
            raise ValueError("Inventory item not found")

        old_qty = float(item.quantity)

        if transaction_type == "PURCHASE":
            item.quantity = (old_qty or 0) + quantity
        elif transaction_type in ("SALE", "WASTE", "ADJUSTMENT"):
            item.quantity = max((old_qty or 0) - quantity, 0)
        elif transaction_type == "RETURN":
            item.quantity = (old_qty or 0) + quantity
        else:
            raise ValueError(f"Unknown transaction type: {transaction_type}")

        tx = InventoryTransaction(
            item_id=item.id,
            transaction_type=transaction_type,
            quantity=quantity,
            reference_id=reference_id,
            notes=notes,
            created_by=user_id,
        )
        self.db.add(tx)
        self.db.commit()
        self.db.refresh(item)
        return item

    def consume_for_order(
        self,
        order_id: str,
        items: list[dict],
    ) -> list[InventoryTransaction]:
        """Consume inventory based on recipe for order items."""
        # In MVP: simplified consumption based on menu item names
        # Real implementation would use recipes table
        transactions = []
        for item_data in items:
            menu_item_name = item_data.get("name", "")
            quantity = item_data.get("quantity", 1)

            # Map menu items to inventory items
            consumption_map = {
                "Tea": {"name": "Tea Powder", "qty_per_unit": 8, "unit": "g"},
                "Masala Tea": {"name": "Tea Powder", "qty_per_unit": 10, "unit": "g"},
                "Coffee": {"name": "Coffee Powder", "qty_per_unit": 10, "unit": "g"},
            }

            if menu_item_name in consumption_map:
                inv_name = consumption_map[menu_item_name]["qty_per_unit"]
                qty_needed = quantity * 8  # simplified

                inv_item = self.db.query(InventoryItem).filter(
                    InventoryItem.name.ilike(f"%{menu_item_name.split()[0]}%"),
                    InventoryItem.is_active == True,
                ).first()

                if inv_item:
                    self.adjust_stock(
                        item_id=str(inv_item.id),
                        quantity=qty_needed,
                        transaction_type="RECIPE_CONSUMPTION",
                        reference_id=order_id,
                        notes=f"Consumed for order {order_id}",
                    )
                    transactions.append({
                        "item": inv_item.name,
                        "quantity": qty_needed,
                    })

        return transactions

    def get_low_stock(self, property_id: Optional[str] = None) -> list[InventoryItem]:
        """Return all items below minimum level."""
        query = self.db.query(InventoryItem).filter(
            InventoryItem.is_active == True,
            InventoryItem.quantity < InventoryItem.min_level,
        )
        if property_id:
            query = query.filter(InventoryItem.property_id == property_id)
        return query.all()

    def get_low_stock_count(self, property_id: Optional[str] = None) -> int:
        """Count of low-stock items for notifications."""
        return len(self.get_low_stock(property_id))
