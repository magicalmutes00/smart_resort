# SmartResort Database Schema

## Overview

PostgreSQL is the primary source of truth. All entities use UUID primary keys where appropriate.

## Schema Design Principles

1. **UUID Identifiers**: All primary keys use UUID v4
2. **Audit Trails**: All significant changes tracked via audit_logs table
3. **Soft Deletes**: Where appropriate (deleted_at timestamp)
4. **Foreign Keys**: Proper constraints for data integrity
5. **Indexes**: Performance indexes on query patterns
6. **Normalization**: Third normal form for transactional data

## Tables

### properties
```
CREATE TABLE properties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    address TEXT,
    phone VARCHAR(50),
    email VARCHAR(255),
    timezone VARCHAR(50) DEFAULT 'UTC',
    is_active BOOLEAN DEFAULT TRUE,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### users
```
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role_id UUID REFERENCES roles(id),
    property_id UUID REFERENCES properties(id),
    is_active BOOLEAN DEFAULT TRUE,
    phone VARCHAR(20),
    avatar_url VARCHAR(500),
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### roles & permissions
```
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE role_permissions (
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);
```

### staff
```
CREATE TABLE staff (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    employee_id VARCHAR(50) UNIQUE,
    department VARCHAR(100),
    hire_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    phone VARCHAR(20),
    emergency_contact VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### guests
```
CREATE TABLE guests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    identity_type VARCHAR(50),
    identity_number VARCHAR(100),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### room_types & rooms
```
CREATE TABLE room_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    base_price DECIMAL(12,2) NOT NULL,
    max_occupancy INTEGER DEFAULT 2,
    amenities TEXT[] DEFAULT ARRAY[]::TEXT[]
);

CREATE TABLE rooms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    number VARCHAR(20) NOT NULL,
    room_type_id UUID REFERENCES room_types(id),
    floor INTEGER,
    status VARCHAR(20) DEFAULT 'AVAILABLE', -- AVAILABLE, OCCUPIED, CLEANING, MAINTENANCE, OUT_OF_SERVICE
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(property_id, number)
);
```

### reservations & room_stays
```
CREATE TABLE reservations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES properties(id),
    guest_id UUID REFERENCES guests(id),
    room_id UUID REFERENCES rooms(id),
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    status VARCHAR(30) DEFAULT 'PENDING', -- PENDING, CONFIRMED, CHECKED_IN, CHECKED_OUT, CANCELLED, NO_SHOW
    total_amount DECIMAL(12,2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE room_stays (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reservation_id UUID REFERENCES reservations(id),
    room_id UUID REFERENCES rooms(id),
    check_in_time TIMESTAMP,
    check_out_time TIMESTAMP,
    room_charge DECIMAL(12,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### restaurant_tables & lake_zones
```
CREATE TABLE restaurant_tables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES properties(id),
    table_number VARCHAR(20) NOT NULL,
    capacity INTEGER DEFAULT 4,
    is_active BOOLEAN DEFAULT TRUE,
    location VARCHAR(100),
    UNIQUE(property_id, table_number)
);

CREATE TABLE lake_zones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    property_id UUID REFERENCES properties(id),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE lake_seats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    zone_id UUID REFERENCES lake_zones(id),
    seat_code VARCHAR(20) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(zone_id, seat_code)
);
```

### qr_codes
```
CREATE TABLE qr_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES properties(id),
    code VARCHAR(100) UNIQUE NOT NULL,
    location_type VARCHAR(50) NOT NULL, -- ROOM, TABLE, LAKE_SEAT
    location_id UUID NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### menu
```
CREATE TABLE menu_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES properties(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE menu_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES properties(id),
    category_id UUID REFERENCES menu_categories(id),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    base_price DECIMAL(10,2) NOT NULL,
    image_url VARCHAR(500),
    is_available BOOLEAN DEFAULT TRUE,
    preparation_time INTEGER DEFAULT 15, -- minutes
    tax_rate DECIMAL(5,2) DEFAULT 5.00
);

CREATE TABLE menu_item_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    menu_item_id UUID REFERENCES menu_items(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    price_modifier DECIMAL(10,2) DEFAULT 0
);

CREATE TABLE menu_item_addons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    menu_item_id UUID REFERENCES menu_items(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) DEFAULT 0
);
```

### orders
```
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    property_id UUID REFERENCES properties(id),
    customer_id UUID REFERENCES guests(id),
    table_id UUID REFERENCES restaurant_tables(id),
    room_id UUID REFERENCES rooms(id),
    lake_seat_id UUID REFERENCES lake_seats(id),
    staff_id UUID REFERENCES staff(id), -- waiter who placed if POS
    status VARCHAR(30) DEFAULT 'CREATED', -- CREATED, CONFIRMED, ACCEPTED, PREPARING, READY, OUT_FOR_DELIVERY, DELIVERED, COMPLETED, CANCELLED
    order_type VARCHAR(30) DEFAULT 'DINE_IN', -- DINE_IN, ROOM_SERVICE, LAKE, TAKEOUT, DELIVERY
    total_amount DECIMAL(12,2) DEFAULT 0,
    notes TEXT,
    special_instructions TEXT,
    idempotency_key VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    menu_item_id UUID REFERENCES menu_items(id),
    variant_id UUID REFERENCES menu_item_variants(id),
    quantity INTEGER DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    notes TEXT
);

CREATE TABLE order_addons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_item_id UUID REFERENCES order_items(id) ON DELETE CASCADE,
    addon_id UUID REFERENCES menu_item_addons(id)
);

CREATE TABLE order_status_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES orders(id),
    status VARCHAR(30) NOT NULL,
    notes TEXT,
    changed_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### payments
```
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES orders(id),
    amount DECIMAL(12,2) NOT NULL,
    method VARCHAR(30) NOT NULL, -- CASH, UPI, CARD, ONLINE
    status VARCHAR(30) DEFAULT 'PENDING', -- PENDING, COMPLETED, FAILED, REFUNDED
    transaction_reference VARCHAR(200),
    provider VARCHAR(50),
    receipt_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### guest_folios
```
CREATE TABLE guest_folios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reservation_id UUID REFERENCES reservations(id),
    guest_id UUID REFERENCES guests(id),
    room_id UUID REFERENCES rooms(id),
    total_charges DECIMAL(12,2) DEFAULT 0,
    paid_amount DECIMAL(12,2) DEFAULT 0,
    status VARCHAR(30) DEFAULT 'OPEN', -- OPEN, CLOSED, SETTLED
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE folio_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    folio_id UUID REFERENCES guest_folios(id) ON DELETE CASCADE,
    item_type VARCHAR(50) NOT NULL, -- ACCOMMODATION, RESTAURANT, ROOM_SERVICE, LAUNDRY, OTHER
    description VARCHAR(250) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    reference_id UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### tasks & assignments
```
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES properties(id),
    type VARCHAR(50) NOT NULL, -- DELIVERY, HOUSEKEEPING, MAINTENANCE, SERVICE, KITCHEN
    location_type VARCHAR(50), -- ROOM, TABLE, LAKE, GENERAL
    location_id UUID,
    priority VARCHAR(20) DEFAULT 'NORMAL', -- LOW, NORMAL, HIGH, URGENT
    status VARCHAR(30) DEFAULT 'PENDING',
    notes TEXT,
    created_by UUID REFERENCES users(id),
    assigned_staff_id UUID REFERENCES staff(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE task_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(id),
    staff_id UUID REFERENCES staff(id),
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by UUID REFERENCES users(id)
);
```

### housekeeping
```
CREATE TABLE housekeeping_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES properties(id),
    room_id UUID REFERENCES rooms(id),
    task_type VARCHAR(50) NOT NULL, -- CLEANING, INSPECTION, LINEN, TOWELS, TOILETRIES
    status VARCHAR(30) DEFAULT 'PENDING',
    assigned_staff_id UUID REFERENCES staff(id),
    priority VARCHAR(20) DEFAULT 'NORMAL',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
```

### maintenance
```
CREATE TABLE maintenance_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES properties(id),
    room_id UUID REFERENCES rooms(id),
    requested_by UUID REFERENCES users(id),
    description TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'NORMAL',
    status VARCHAR(30) DEFAULT 'PENDING',
    image_urls TEXT[],
    assigned_staff_id UUID REFERENCES staff(id),
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
```

### inventory
```
CREATE TABLE inventory_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES properties(id),
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    quantity DECIMAL(10,3) DEFAULT 0,
    min_level DECIMAL(10,3) DEFAULT 0,
    max_level DECIMAL(10,3),
    cost_per_unit DECIMAL(10,2) DEFAULT 0,
    supplier_id UUID REFERENCES suppliers(id),
    batch_number VARCHAR(100),
    expiry_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inventory_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_id UUID REFERENCES inventory_items(id),
    transaction_type VARCHAR(30) NOT NULL, -- PURCHASE, SALE, ADJUSTMENT, WASTE, RECIPE_CONSUMPTION
    quantity DECIMAL(10,3) NOT NULL,
    reference_id UUID,
    notes TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE recipes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    menu_item_id UUID REFERENCES menu_items(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    yield_quantity INTEGER DEFAULT 1
);

CREATE TABLE recipe_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipe_id UUID REFERENCES recipes(id) ON DELETE CASCADE,
    inventory_item_id UUID REFERENCES inventory_items(id),
    quantity DECIMAL(10,3) NOT NULL,
    unit VARCHAR(20) NOT NULL
);
```

### suppliers & purchases
```
CREATE TABLE suppliers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    contact_person VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(20),
    address TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE purchase_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES properties(id),
    supplier_id UUID REFERENCES suppliers(id),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(30) DEFAULT 'DRAFT', -- DRAFT, SUBMITTED, RECEIVED, PARTIALLY_RECEIVED, COMPLETED, CANCELLED
    total_amount DECIMAL(12,2) DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE purchase_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    purchase_order_id UUID REFERENCES purchase_orders(id) ON DELETE CASCADE,
    inventory_item_id UUID REFERENCES inventory_items(id),
    quantity DECIMAL(10,3) NOT NULL,
    unit_price DECIMAL(10,2),
    received_quantity DECIMAL(10,3) DEFAULT 0
);
```

### notifications
```
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    staff_id UUID REFERENCES staff(id),
    property_id UUID REFERENCES properties(id),
    title VARCHAR(255) NOT NULL,
    body TEXT,
    type VARCHAR(50) NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    data JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### audit_logs
```
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity VARCHAR(50) NOT NULL,
    entity_id UUID,
    old_value JSONB,
    new_value JSONB,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### settings
```
CREATE TABLE settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES properties(id),
    key VARCHAR(100) NOT NULL,
    value JSONB,
    UNIQUE(property_id, key)
);
```

## Indexes

```
CREATE INDEX idx_orders_property ON orders(property_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_created ON orders(created_at DESC);

CREATE INDEX idx_tasks_property ON tasks(property_id);
CREATE INDEX idx_tasks_assigned ON tasks(assigned_staff_id);
CREATE INDEX idx_tasks_status ON tasks(status);

CREATE INDEX idx_inventory_property ON inventory_items(property_id);
CREATE INDEX idx_inventory_category ON inventory_items(category);

CREATE INDEX idx_reservations_guest ON reservations(guest_id);
CREATE INDEX idx_reservations_status ON reservations(status);
CREATE INDEX idx_reservations_dates ON reservations(check_in, check_out);
```

## Constraints

- All UUID references use `ON DELETE RESTRICT` or `ON DELETE CASCADE` as appropriate
- Status fields are validated via check constraints
- Price fields use `DECIMAL(12,2)` for monetary precision
- Email fields validated via regex

## Migrations

Use Alembic for all schema changes. Each table change must include:
- Forward migration script
- Rollback script
- Index changes
- Constraint updates
