# API Specification

## Base Configuration

- Base URL: `https://api.smartresort.local/api/v1`
- Protocol: HTTPS (production)
- Format: JSON
- Auth: Bearer JWT Token
- Rate Limit: 100 req/min per client

## Authentication

### POST /auth/login
```
Request:
{
  "email": "admin@lakeview.com",
  "password": "dev_password_2024"
}

Response (200):
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "email": "...",
    "username": "admin",
    "first_name": "Admin",
    "last_name": "User",
    "role": "SUPER_ADMIN",
    "permissions": ["orders.read", "orders.create", ...]
  }
}
```

### POST /auth/refresh
```
Request:
{
  "refresh_token": "..."
}

Response (200):
{
  "access_token": "new_token",
  "refresh_token": "new_refresh"
}
```

### POST /auth/logout
```
Response (204): No Content
```

## Properties

### GET /properties
```
Query: ?page=1&limit=20
Response (200):
{
  "data": [{
    "id": "uuid",
    "name": "Lake View Resort",
    "address": "...",
    "phone": "...",
    "timezone": "Asia/Kolkata",
    "is_active": true,
    "settings": {...}
  }],
  "meta": { "total": 1, "page": 1, "per_page": 20 }
}
```

### POST /properties
```
Request:
{
  "name": "Lake View Resort",
  "address": "...",
  "timezone": "Asia/Kolkata"
}
```

## Users

### GET /users/me
```
Response (200):
{
  "id": "...",
  "email": "...",
  "username": "...",
  "first_name": "...",
  "last_name": "...",
  "role": "MANAGER",
  "property_id": "...",
  "permissions": [...]
}
```

### GET /users
```
Response (200):
{
  "data": [{...}],
  "meta": {...}
}
```

## Menu

### GET /menu/categories
```
Response (200):
{
  "data": [{
    "id": "...",
    "name": "Main Course",
    "description": "...",
    "items": [...]
  }]
}
```

### GET /menu/items
```
Query: ?category=uuid&available=true
Response (200):
{
  "data": [{
    "id": "...",
    "name": "Chicken Biryani",
    "base_price": 180.00,
    "variants": [{"name": "Spicy", "modifier": 0}],
    "addons": [{"name": "Extra Gravy", "price": 30}],
    "preparation_time": 20
  }]
}
```

## Tables & Lake

### GET /restaurant-tables
```
Response (200):
{
  "data": [{
    "id": "...",
    "table_number": "T-001",
    "capacity": 4,
    "is_active": true,
    "location": "Main Hall"
  }]
}
```

### GET /lake-zones
```
Response (200):
{
  "data": [{
    "id": "...",
    "name": "Zone A",
    "seats": [{"code": "A01", "seat_code": "A01"}]
  }]
}
```

### GET /qr-codes
```
Response (200):
{
  "data": [{
    "id": "...",
    "code": "ROOM-101",
    "location_type": "ROOM",
    "location_id": "...",
    "is_active": true
  }]
}
```

### POST /qr-codes
```
Request:
{
  "code": "TABLE-001",
  "location_type": "TABLE",
  "location_id": "...",
  "is_active": true
}
```

## Orders (Critical)

### POST /orders
```
Request:
{
  "idempotency_key": "key-123-unique",
  "table_id": "...",
  "room_id": "...",
  "lake_seat_id": "...",
  "items": [{
    "menu_item_id": "...",
    "variant_id": "...",
    "quantity": 2,
    "notes": "Less spicy",
    "addons": [{"addon_id": "..."}]
  }],
  "notes": "...",
  "special_instructions": "..."
}

Response (201):
{
  "id": "...",
  "order_number": "782",
  "status": "CREATED",
  "items": [...],
  "total_amount": 420.00,
  "created_at": "..."
}
```

### GET /orders
```
Query: ?status=PENDING&property=...
Response (200):
{
  "data": [{...}],
  "meta": {...}
}
```

### GET /orders/{id}
```
Response (200):
{
  "id": "...",
  "order_number": "782",
  "status": "PREPARING",
  "table": {...},
  "items": [...],
  "status_history": [...]
}
```

### PATCH /orders/{id}/status
```
Request:
{
  "status": "ACCEPTED",
  "notes": "Kitchen started preparing"
}
```

### POST /orders/{id}/cancel
```
Response (200):
{
  "status": "CANCELLED",
  "cancelled_at": "..."
}
```

## Payments

### POST /payments
```
Request:
{
  "order_id": "...",
  "amount": 420.00,
  "method": "UPI",
  "transaction_reference": "upi_ref_001"
}
```

## Tasks

### GET /tasks
```
Query: ?assigned_to=...&status=PENDING
Response (200):
{
  "data": [{
    "id": "...",
    "type": "DELIVERY",
    "priority": "NORMAL",
    "status": "PENDING",
    "location": {"type": "ROOM", "id": "...", "number": "204"},
    "notes": "2 Tea, 1 Sandwich",
    "assigned_staff": {...}
  }]
}
```

### PATCH /tasks/{id}/status
```
Request:
{
  "status": "IN_PROGRESS",
  "notes": "Started delivery"
}
```

## Room Service

### GET /rooms/{id}/service-menu
```
Response (200): Shows available service categories
```

## Housekeeping

### GET /housekeeping/tasks
```
Query: ?room_id=...&status=PENDING
```

### POST /housekeeping/tasks
```
Request:
{
  "room_id": "...",
  "task_type": "CLEANING",
  "priority": "NORMAL",
  "notes": "Standard checkout cleaning"
}
```

## Maintenance

### POST /maintenance/requests
```
Request:
{
  "room_id": "...",
  "description": "AC not cooling",
  "priority": "NORMAL",
  "image_urls": ["https://..."]
}
```

### PATCH /maintenance/requests/{id}/status
```
Request:
{
  "status": "COMPLETED",
  "resolution_notes": "Fixed AC filter"
}
```

## Inventory

### GET /inventory
```
Query: ?category=FOOD&low_stock=true
Response (200):
{
  "data": [{
    "id": "...",
    "name": "Milk",
    "current_quantity": 8.0,
    "min_level": 10.0,
    "unit": "L"
  }]
}
```

### POST /inventory/transactions
```
Request:
{
  "item_id": "...",
  "type": "PURCHASE",
  "quantity": 20.0,
  "notes": "Weekly restock"
}
```

## Reports

### GET /reports/revenue
```
Query: ?date_from=...&date_to=...&group_by=day
Response (200):
{
  "data": [{
    "date": "2024-01-01",
    "hotel_revenue": 4500.00,
    "restaurant_revenue": 1250.00,
    "tea_stall_revenue": 180.00,
    "total": 5930.00
  }]
}
```

### GET /reports/orders
```
Query: ?period=today
```

### GET /reports/inventory-consumption
```
Response: Recipe-based consumption tracking
```

## Notifications

### GET /notifications
```
Response (200):
{
  "data": [{
    "id": "...",
    "title": "New Order",
    "body": "Table T-001 ordered 2 Chicken Biryani",
    "type": "NEW_ORDER",
    "is_read": false,
    "created_at": "..."
  }]
}
```

### PATCH /notifications/{id}/read
```
Response (204): No Content
```

## WebSocket Events (Event Spec)

Connection: `wss://api.smartresort.local/ws`

### Subscribe Pattern
```json
{
  "action": "subscribe",
  "channel": "kitchen:main",
  "token": "..."
}
```

### Event Types
```json
{
  "event": "order:created",
  "data": { ... }
}
```

Channels:
- `orders:all`
- `orders:kitchen:main`
- `orders:kitchen:tea`
- `tasks:delivery`
- `tasks:housekeeping`
- `tasks:maintenance`
- `inventory:low`
- `notifications:user:{user_id}`
- `dashboard:property:{property_id}`

## Error Format
```
Response (400):
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [{"field": "email", "message": "Invalid email format"}]
  }
}

Response (401):
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token"
  }
}

Response (403):
{
  "error": {
    "code": "FORBIDDEN",
    "message": "Insufficient permissions"
  }
}
```

## Rate Limiting

Headers:
- `X-RateLimit-Limit`: 100
- `X-RateLimit-Remaining`: 95
- `X-RateLimit-Reset`: 1712345678

## Idempotency

For POST /orders:
- `Idempotency-Key` header required
- Key must be unique per request
- Duplicate key returns same response (200/201)
- Key expires after 24 hours
