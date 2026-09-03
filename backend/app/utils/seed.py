"""Seed development data.

Run with: python -m app.utils.seed

Creates:
- Property: Lake View Resort
- 11 roles + permissions
- 11 users (one per role)
- 10 rooms + room types
- 20 restaurant tables
- 2 lake zones + 20 seats
- Menu categories + 14 menu items
- Inventory items
- QR codes for all locations
"""
import uuid
from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import User
from app.models.role import Role
from app.models.property import Property
from app.models.menu import MenuCategory, MenuItem, MenuItemVariant, MenuItemAddon
from app.models.staff import Staff, Guest
from app.models.dining import RestaurantTable, LakeZone, LakeSeat
from app.models.rooms import Room, RoomType
from app.models.inventory import InventoryItem
from app.models.qr import QRCode


# Roles
ROLES = [
    ("SUPER_ADMIN", "Full system access"),
    ("OWNER", "Property owner"),
    ("MANAGER", "Property manager"),
    ("RECEPTIONIST", "Front desk staff"),
    ("CASHIER", "Payment processing"),
    ("KITCHEN", "Kitchen operations"),
    ("WAITER", "Table service"),
    ("DELIVERY_STAFF", "Food delivery"),
    ("HOUSEKEEPING", "Room cleaning"),
    ("MAINTENANCE", "Repairs and maintenance"),
    ("INVENTORY_MANAGER", "Stock management"),
]

# Test users — DEV ONLY
USERS = [
    ("admin@lakeview.com", "admin", "Admin", "User", "SUPER_ADMIN", "dev_admin_2024"),
    ("owner@lakeview.com", "owner", "Resort", "Owner", "OWNER", "dev_owner_2024"),
    ("manager@lakeview.com", "manager", "Resort", "Manager", "MANAGER", "dev_manager_2024"),
    ("reception@lakeview.com", "reception", "Front", "Desk", "RECEPTIONIST", "dev_reception_2024"),
    ("cashier@lakeview.com", "cashier", "Counter", "Cashier", "CASHIER", "dev_cashier_2024"),
    ("kitchen@lakeview.com", "kitchen", "Main", "Chef", "KITCHEN", "dev_kitchen_2024"),
    ("waiter@lakeview.com", "waiter", "Front", "Waiter", "WAITER", "dev_waiter_2024"),
    ("delivery@lakeview.com", "delivery", "Quick", "Delivery", "DELIVERY_STAFF", "dev_delivery_2024"),
    ("housekeeping@lakeview.com", "housekeeping", "Clean", "Staff", "HOUSEKEEPING", "dev_housekeeping_2024"),
    ("maintenance@lakeview.com", "maintenance", "Fix", "It", "MAINTENANCE", "dev_maintenance_2024"),
    ("inventory@lakeview.com", "inventory", "Stock", "Manager", "INVENTORY_MANAGER", "dev_inventory_2024"),
]

# Menu categories
CATEGORIES = [
    ("Tea & Coffee", 1),
    ("Snacks", 2),
    ("Main Course", 3),
    ("Beverages", 4),
    ("Desserts", 5),
    ("Breakfast", 6),
]

# Menu items
MENU_ITEMS = [
    ("Tea & Coffee", "Tea", "Hot Indian Tea", 15.0, 5),
    ("Tea & Coffee", "Masala Tea", "Spiced tea with ginger & cardamom", 25.0, 5),
    ("Tea & Coffee", "Coffee", "Hot filter coffee", 30.0, 6),
    ("Snacks", "Vada", "Crispy lentil doughnuts", 20.0, 8),
    ("Snacks", "Samosa", "Crispy pastry with potato filling", 20.0, 8),
    ("Snacks", "Pakoda", "Mixed vegetable fritters", 30.0, 8),
    ("Main Course", "Parotta", "Flaky layered bread", 30.0, 10),
    ("Main Course", "Chicken Biryani", "Aromatic basmati rice with chicken", 180.0, 20),
    ("Main Course", "Veg Fried Rice", "Wok-tossed rice with vegetables", 120.0, 15),
    ("Beverages", "Lime Soda", "Fresh lime with soda", 40.0, 3),
    ("Beverages", "Mango Juice", "Fresh mango pulp", 60.0, 4),
    ("Beverages", "Water Bottle", "500ml mineral water", 20.0, 1),
    ("Desserts", "Ice Cream", "Vanilla scoop", 50.0, 2),
    ("Breakfast", "Idli", "Steamed rice cakes (2 pcs)", 40.0, 8),
]

# Inventory
INVENTORY = [
    ("Tea Powder", "Beverages", "g", 5000, 1000, 1.0),
    ("Coffee Powder", "Beverages", "g", 3000, 500, 2.0),
    ("Milk", "Beverages", "L", 8, 10, 60.0),
    ("Sugar", "Beverages", "kg", 10, 5, 45.0),
    ("Ginger", "Vegetables", "kg", 2, 1, 80.0),
    ("Lime", "Fruits", "kg", 5, 2, 60.0),
    ("Bread", "Bakery", "pcs", 30, 10, 25.0),
    ("Chicken", "Meat", "kg", 15, 5, 220.0),
    ("Basmati Rice", "Grains", "kg", 50, 20, 90.0),
    ("Oil", "Cooking", "L", 20, 10, 180.0),
]


def seed():
    """Run the seed."""
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # --- Property
        prop = db.query(Property).first()
        if not prop:
            prop = Property(
                name="Lake View Resort",
                address="Lake Road, Kerala, India",
                phone="+91-9876543210",
                email="info@lakeview.com",
                timezone="Asia/Kolkata",
            )
            db.add(prop)
            db.commit()
            db.refresh(prop)
            print(f"  + Property: {prop.name}")

        # --- Roles
        role_map = {}
        for name, desc in ROLES:
            r = db.query(Role).filter(Role.name == name).first()
            if not r:
                r = Role(name=name, description=desc)
                db.add(r)
                db.flush()
            role_map[name] = r
        db.commit()
        print(f"  + {len(role_map)} roles")

        # --- Users + Staff
        for email, username, first, last, role_name, password in USERS:
            u = db.query(User).filter(User.email == email).first()
            if not u:
                u = User(
                    email=email,
                    username=username,
                    hashed_password=get_password_hash(password),
                    first_name=first,
                    last_name=last,
                    role_id=role_map[role_name].id,
                    property_id=prop.id,
                    is_active=True,
                )
                db.add(u)
                db.flush()

                # Create staff for non-customer roles
                if role_name not in ["SUPER_ADMIN", "OWNER"]:
                    s = Staff(
                        user_id=u.id,
                        employee_id=f"EMP-{username[:3].upper()}-{u.id.hex[:4]}",
                        department=role_name,
                        is_active=True,
                    )
                    db.add(s)
        db.commit()
        print(f"  + {len(USERS)} users")

        # --- Room types
        rt_deluxe = db.query(RoomType).filter(RoomType.name == "Deluxe").first()
        if not rt_deluxe:
            rt_deluxe = RoomType(
                name="Deluxe",
                description="Lake view deluxe room with AC",
                base_price=3500.0,
                max_occupancy=2,
                amenities=["AC", "TV", "WiFi", "Lake View"],
            )
            db.add(rt_deluxe)
            db.flush()
        print("  + Room types")

        # --- Rooms 101-110
        existing_room_numbers = {r.number for r in db.query(Room).all()}
        for n in range(101, 111):
            num = str(n)
            if num not in existing_room_numbers:
                room = Room(
                    property_id=prop.id,
                    number=num,
                    room_type_id=rt_deluxe.id,
                    floor=1 if int(num) <= 105 else 2,
                    status="AVAILABLE",
                )
                db.add(room)
        db.commit()
        print("  + 10 rooms (101-110)")

        # --- Restaurant tables T-001 to T-020
        existing_tables = {t.table_number for t in db.query(RestaurantTable).all()}
        for i in range(1, 21):
            num = f"T-{i:03d}"
            if num not in existing_tables:
                t = RestaurantTable(
                    property_id=prop.id,
                    table_number=num,
                    capacity=4,
                    is_active=True,
                    location="Main Hall" if i <= 10 else "Garden",
                    status="AVAILABLE",
                )
                db.add(t)
        db.commit()
        print("  + 20 restaurant tables")

        # --- Lake zones
        zone_a = db.query(LakeZone).filter(LakeZone.name == "Zone A").first()
        if not zone_a:
            zone_a = LakeZone(property_id=prop.id, name="Zone A", is_active=True)
            db.add(zone_a)
            db.flush()
        zone_b = db.query(LakeZone).filter(LakeZone.name == "Zone B").first()
        if not zone_b:
            zone_b = LakeZone(property_id=prop.id, name="Zone B", is_active=True)
            db.add(zone_b)
            db.flush()

        # Lake seats
        existing_seats = {(s.zone_id, s.seat_code) for s in db.query(LakeSeat).all()}
        for zone in (zone_a, zone_b):
            letter = zone.name[-1]
            for i in range(1, 11):
                code = f"{letter}{i:02d}"
                if (zone.id, code) not in existing_seats:
                    s = LakeSeat(zone_id=zone.id, seat_code=code, is_active=True)
                    db.add(s)
        db.commit()
        print("  + 2 lake zones + 20 seats")

        # --- Menu categories
        cat_map = {}
        for name, order in CATEGORIES:
            c = db.query(MenuCategory).filter(MenuCategory.name == name).first()
            if not c:
                c = MenuCategory(
                    property_id=prop.id,
                    name=name,
                    display_order=order,
                    is_active=True,
                )
                db.add(c)
                db.flush()
            cat_map[name] = c
        db.commit()
        print("  + Menu categories")

        # --- Menu items
        existing_items = {m.name for m in db.query(MenuItem).all()}
        for cat_name, name, desc, price, prep_time in MENU_ITEMS:
            if name not in existing_items:
                item = MenuItem(
                    property_id=prop.id,
                    category_id=cat_map[cat_name].id,
                    name=name,
                    description=desc,
                    base_price=price,
                    is_available=True,
                    preparation_time=prep_time,
                    tax_rate=5.0,
                )
                db.add(item)
        db.commit()
        print("  + 14 menu items")

        # --- Inventory
        existing_inv = {i.name for i in db.query(InventoryItem).all()}
        for name, category, unit, qty, min_level, cost in INVENTORY:
            if name not in existing_inv:
                inv = InventoryItem(
                    property_id=prop.id,
                    name=name,
                    category=category,
                    unit=unit,
                    quantity=qty,
                    min_level=min_level,
                    cost_per_unit=cost,
                    is_active=True,
                )
                db.add(inv)
        db.commit()
        print("  + 10 inventory items")

        # --- QR codes for all locations
        existing_qr = {q.code for q in db.query(QRCode).all()}
        qr_added = 0

        # Room QRs
        for room in db.query(Room).all():
            code = f"ROOM-{room.number}"
            if code not in existing_qr:
                qr = QRCode(
                    property_id=prop.id,
                    code=code,
                    location_type="ROOM",
                    location_id=room.id,
                    is_active=True,
                )
                db.add(qr)
                qr_added += 1

        # Table QRs
        for table in db.query(RestaurantTable).all():
            code = f"TABLE-{table.table_number}"
            if code not in existing_qr:
                qr = QRCode(
                    property_id=prop.id,
                    code=code,
                    location_type="TABLE",
                    location_id=table.id,
                    is_active=True,
                )
                db.add(qr)
                qr_added += 1

        # Lake seat QRs
        for seat in db.query(LakeSeat).all():
            code = f"LAKE-{seat.seat_code}"
            if code not in existing_qr:
                qr = QRCode(
                    property_id=prop.id,
                    code=code,
                    location_type="LAKE_SEAT",
                    location_id=seat.id,
                    is_active=True,
                )
                db.add(qr)
                qr_added += 1

        db.commit()
        print(f"  + {qr_added} QR codes")

        print()
        print("=" * 60)
        print("SEED COMPLETE — Development Test Users")
        print("=" * 60)
        print()
        print(f"{'ROLE':<20} {'EMAIL':<35} {'PASSWORD':<20}")
        print("-" * 80)
        for email, _, _, _, role, password in USERS:
            print(f"{role:<20} {email:<35} {password:<20}")
        print()
        print("⚠️  Development credentials only. Replace before deployment.")
        print()

    finally:
        db.close()


if __name__ == "__main__":
    seed()
