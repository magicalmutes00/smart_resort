# RBAC Permission Matrix

## Roles

| Role | Description | Users |
|------|-------------|-------|
| SUPER_ADMIN | Full system access | System owner |
| OWNER | Property-level full access | Property owner |
| MANAGER | Property management | Hotel manager |
| RECEPTIONIST | Guest check-in/check-out | Front desk |
| CASHIER | Payment processing | Cashier staff |
| KITCHEN | Kitchen display and updates | Kitchen staff |
| WAITER | Table service and orders | Wait staff |
| DELIVERY_STAFF | Food delivery tasks | Delivery staff |
| HOUSEKEEPING | Room cleaning and inspection | Housekeeping staff |
| MAINTENANCE | Repair and maintenance | Maintenance staff |
| INVENTORY_MANAGER | Stock and supplier management | Inventory staff |

## Permission Categories

### Authentication
- auth.login
- auth.refresh
- auth.logout
- auth.change_password

### Properties
- properties.read
- properties.create
- properties.update
- properties.delete

### Users
- users.read
- users.create
- users.update
- users.delete
- users.assign_role

### Roles & Permissions
- roles.read
- roles.create
- roles.update
- roles.assign_permissions

### Menu
- menu.read
- menu.create
- menu.update
- menu.delete
- menu.categories.read
- menu.categories.create
- menu.categories.update

### Orders
- orders.read
- orders.create
- orders.update
- orders.cancel
- orders.delete (soft delete review)

### Payments
- payments.read
- payments.create
- payments.verify
- payments.refund
- payments.refund_approve

### Tables
- tables.read
- tables.create
- tables.update
- tables.status_update

### Lake Seating
- lake.read
- lake.update
- lake.status_update

### QR Codes
- qr.read
- qr.create
- qr.update
- qr.disable
- qr.generate

### Reservations
- reservations.read
- reservations.create
- reservations.update
- reservations.cancel
- reservations.check_in
- reservations.check_out
- reservations.modify_dates

### Guests
- guests.read
- guests.create
- guests.update
- guests.delete

### Rooms
- rooms.read
- rooms.update
- rooms.status_change
- rooms.assign

### Guest Folios
- folios.read
- folios.create
- folios.charge_add
- folios.payment_record
- folios.checkout

### Room Service
- room_service.read
- room_service.create
- room_service.update

### Housekeeping
- housekeeping.read
- housekeeping.create
- housekeeping.assign
- housekeeping.start
- housekeeping.complete
- housekeeping.inspect

### Maintenance
- maintenance.read
- maintenance.create
- maintenance.assign
- maintenance.update
- maintenance.complete

### Tasks
- tasks.read
- tasks.create
- tasks.assign
- tasks.accept
- tasks.start
- tasks.complete
- tasks.cancel

### Inventory
- inventory.read
- inventory.adjust
- inventory.create
- inventory.update
- inventory.delete

### Recipes
- recipes.read
- recipes.create
- recipes.update
- recipes.delete

### Suppliers
- suppliers.read
- suppliers.create
- suppliers.update

### Purchase Orders
- purchase.read
- purchase.create
- purchase.update
- purchase.receive
- purchase.approve

### Reports
- reports.read
- reports.revenue
- reports.orders
- reports.occupancy
- reports.inventory
- reports.staff_productivity

### Notifications
- notifications.read
- notifications.create
- notifications.read_all
- notifications.mark_read

### Audit Logs
- audit.read

### Settings
- settings.read
- settings.update

## Role → Permission Mapping

```
SUPER_ADMIN    → ALL permissions
OWNER           → All property-level permissions + audit.read
MANAGER         → All property-level permissions except roles.assign_permissions
RECEPTIONIST    → guests.*, reservations.*, rooms.read, rooms.status_change,
                   payments.read, payments.create, folios.read
CASHIER         → orders.*, payments.*, guests.read
KITCHEN         → orders.read, orders.status_update (PREPARING/READY/COMPLETED),
                   menu.read
WAITER          → orders.read, orders.create, orders.update, payments.create,
                   tables.read, guests.read
DELIVERY_STAFF  → tasks.read (assigned), tasks.accept, tasks.start, tasks.complete,
                   orders.read
HOUSEKEEPING    → housekeeping.*, rooms.read, tasks.read (housekeeping)
MAINTENANCE     → maintenance.*, tasks.read (maintenance)
INVENTORY_MGR   → inventory.*, suppliers.*, purchase.*, recipes.read, recipes.update
```

## Enforcement Rules

### Backend Enforcement
```
Every API endpoint must:
1. Verify JWT token
2. Load user role
3. Load role permissions
4. Check endpoint permission
5. Reject if not permitted (403 Forbidden)
```

Frontend restrictions are for UX only. The backend is the source of truth.

### Endpoint Permission Tags

Each API endpoint must declare its required permission:
```
@router.get("/orders", dependencies=[RequirePermission("orders.read")])
```

## Dynamic Assignment Rules

Some roles may have additional permissions assigned dynamically:
- MANAGER can be granted INVENTORY_MANAGER temporary permissions
- All permissions must be explicitly granted, never inherited by default (except SUPER_ADMIN/OWNER)
