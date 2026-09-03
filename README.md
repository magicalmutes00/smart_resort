# SmartResort

A production-grade digital hospitality operating system that reduces waiter dependency through QR self-ordering, automated kitchen workflows, staff task assignment, and centralized operations management.

## Overview

SmartResort unifies the entire hospitality operation — Resort, Hotel, Restaurant, Tea Stall, Lake-Side Seating, Room Service, Housekeeping, Maintenance — into a single digital platform. The system is engineered to be deployed as a real, multi-property SaaS and not as a simple POS.

## Phases Delivered

| # | Phase | Status |
|---|-------|--------|
| 0 | Architecture | ✅ |
| 1 | Project Init (Monorepo) | ✅ |
| 2 | Authentication (JWT + RBAC) | ✅ |
| 3 | Restaurant + Tea Stall | ✅ |
| 4 | QR Ordering | ✅ |
| 5 | Kitchen Display System + Real-time | ✅ |
| 6 | Flutter Staff App | ✅ |
| 7 | Hotel Module (rooms, reservations, folios) | ✅ |
| 8 | Operations (housekeeping, maintenance, tasks) | ✅ |
| 9 | Inventory + Recipes | ✅ |
| 10 | Payments + Refunds | ✅ |
| 11 | Analytics + Reports | ✅ |
| 12 | AI Forecasting (Optional) | ✅ |
| 13 | QA + E2E Tests | ✅ |
| 14 | Deployment + CI/CD | ✅ |

## Quick Start

```bash
# 1. Setup
cp .env.example .env

# 2. Start all services (Postgres, Redis, Backend, Web)
docker compose up -d

# 3. Run migrations
docker compose exec backend alembic upgrade head

# 4. Seed development data
docker compose exec backend python -m app.utils.seed
```

- API docs: http://localhost:8000/docs
- Customer app: http://localhost:5173

## Test Credentials (Development)

| Role | Email | Password |
|------|-------|----------|
| SUPER_ADMIN | admin@lakeview.com | dev_admin_2024 |
| MANAGER | manager@lakeview.com | dev_manager_2024 |
| KITCHEN | kitchen@lakeview.com | dev_kitchen_2024 |
| WAITER | waiter@lakeview.com | dev_waiter_2024 |
| HOUSEKEEPING | housekeeping@lakeview.com | dev_housekeeping_2024 |
| MAINTENANCE | maintenance@lakeview.com | dev_maintenance_2024 |
| DELIVERY | delivery@lakeview.com | dev_delivery_2024 |

⚠️ Replace before production deployment.

## Tech Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic, PostgreSQL 15, Redis 7, JWT
- **Web:** React 18, TypeScript, Vite, Tailwind, React Router, TanStack Query, Zod, Axios
- **Mobile:** Flutter 3.16+, Dart 3, Riverpod, GoRouter, Dio, flutter_secure_storage

## Architecture Highlights

- **Order state machine:** CREATED → CONFIRMED → ACCEPTED → PREPARING → READY → OUT_FOR_DELIVERY → DELIVERED → COMPLETED
- **Reservation state machine:** PENDING → CONFIRMED → CHECKED_IN → CHECKED_OUT (with auto-housekeeping on checkout)
- **Task state machine:** PENDING → ASSIGNED → ACCEPTED → IN_PROGRESS → COMPLETED
- **Auto-task creation:** When order becomes READY for room/lake/delivery types, a delivery task is auto-created
- **WebSocket channels:** `orders:*`, `kitchen:all`, `tasks:delivery`, `notifications:user:*`
- **Idempotency:** Order creation and payment creation both support `Idempotency-Key` header
- **RBAC:** 11 roles × 80+ granular permissions; backend-enforced; `RequirePermission` dependency
- **Payment abstraction:** Provider-agnostic (`CashProvider`, `UPIProvider`); Razorpay-ready via clean interface

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — System architecture
- [DATABASE.md](DATABASE.md) — PostgreSQL schema
- [API.md](API.md) — REST + WebSocket API
- [RBAC.md](RBAC.md) — Roles and permissions matrix
- [DEVELOPMENT.md](DEVELOPMENT.md) — Local dev guide
- [DEPLOYMENT.md](DEPLOYMENT.md) — Production deployment
- [TEST_VERIFICATION.md](TEST_VERIFICATION.md) — QA summary

## License

Proprietary. All rights reserved.
# smart_resort
