# Development Guide

## Local Setup (Full Stack)

```bash
# 1. Clone
git clone <repo>
cd smartresort

# 2. Environment
cp .env.example .env
# Edit .env with your local secrets

# 3. Start services
docker compose up -d

# 4. Run migrations (first time)
docker compose exec backend alembic upgrade head

# 5. Seed data (development)
docker compose exec backend python -m app.utils.seed
```

## Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

API: http://localhost:8000
Docs: http://localhost:8000/docs

## Web (Customer)

```bash
cd apps/web/customer
npm install
npm run dev
```

http://localhost:5173

## Flutter Mobile

```bash
cd apps/mobile
flutter pub get
flutter run
```

## Database Migrations

Create new migration:
```bash
alembic revision --autogenerate -m "add new table"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback:
```bash
alembic downgrade -1
```

## Seed Data

Development seed creates:
- Property: Lake View Resort
- 10 rooms (101-110)
- 20 restaurant tables
- 2 lake zones × 10 seats each
- Menu items: Tea, Coffee, Masala Tea, Vada, Samosa, Parotta, Chicken Biryani, etc.
- Test users for every role

Run:
```bash
cd backend
python -m app.utils.seed
```

## Test Users (Development Only)

| Role | Email | Password |
|------|-------|----------|
| SUPER_ADMIN | admin@lakeview.com | dev_admin_2024 |
| MANAGER | manager@lakeview.com | dev_manager_2024 |
| KITCHEN | kitchen@lakeview.com | dev_kitchen_2024 |
| WAITER | waiter@lakeview.com | dev_waiter_2024 |
| HOUSEKEEPING | housekeeping@lakeview.com | dev_housekeeping_2024 |
| MAINTENANCE | maintenance@lakeview.com | dev_maintenance_2024 |
| DELIVERY | delivery@lakeview.com | dev_delivery_2024 |

⚠️ These are development credentials only. Replace before deployment.

## Common Tasks

### Reset database
```bash
docker compose down -v
docker compose up -d
```

### View logs
```bash
docker compose logs -f backend
```

### Run tests
```bash
# Backend
cd backend && pytest

# Web
cd apps/web/customer && npm test

# Flutter
cd apps/mobile && flutter test
```

## Code Style

### Python
- Black formatter
- Type hints required
- Service layer for business logic
- Repository pattern for data access

### TypeScript
- ESLint + Prettier
- Strict TypeScript
- No `any` types
- Hooks + functional components

### Dart
- flutter_lints
- Effective Dart style
- Riverpod for state
- GoRouter for navigation
