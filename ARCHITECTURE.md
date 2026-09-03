# SmartResort Architecture

## Overview

SmartResort is a digital hospitality operating system designed to reduce waiter dependency through QR self-ordering, automated kitchen workflows, staff task assignment, and centralized operations management.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           SMARTRESORT SYSTEM                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Customer   │  │     POS      │  │     KDS       │  │    Admin    │ │
│  │   (React)    │  │   (React)    │  │   (React)     │  │   (React)   │ │
│  │              │  │              │  │               │  │             │ │
│  │  • QR Menu    │  │  • Counter   │  │  • Kitchen    │  │  • Dashboard│ │
│  │  • Ordering   │  │  • Tables    │  │    Display    │  │  • Reports  │ │
│  │  • Payment    │  │  • Payments  │  │  • Token Disp │  │  • Config   │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
│         │                 │                  │                  │         │
│         └─────────────────┼──────────────────┼──────────────────┘         │
│                           │                  │                              │
│                           ▼                  ▼                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                    FASTAPI BACKEND (Python)                          │ │
│  │                                                                       │ │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │ │
│  │   │   REST API   │  │  WebSocket   │  │   Workers    │  │  Services  │ │ │
│  │   │   (v1/*)     │  │  Gateway     │  │  (Celery)    │  │            │ │ │
│  │   └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │ │
│  │                                                                       │ │
│  │   ┌───────────────────────────────────────────────────────────────┐ │ │
│  │   │                     SERVICE LAYER                             │ │ │
│  │   │                                                               │ │ │
│  │   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │ │ │
│  │   │  │  Order   │ │  Kitchen  │ │  Payment  │ │   Task   │        │ │ │
│  │   │  │ Service  │ │ Service  │ │ Service  │ │ Service  │        │ │ │
│  │   │  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │ │ │
│  │   │                                                               │ │ │
│  │   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │ │ │
│  │   │  │  Room    │ │ Inventory│ │ Housekeep│ │  Staff   │        │ │ │
│  │   │  │ Service  │ │ Service  │ │ Service  │ │ Service  │        │ │ │
│  │   │  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │ │ │
│  │   └───────────────────────────────────────────────────────────────┘ │ │
│  │                                                                       │ │
│  │   ┌───────────────────────────────────────────────────────────────┐ │ │
│  │   │                   REPOSITORY LAYER                             │ │ │
│  │   │         (SQLAlchemy + PostgreSQL)                             │ │ │
│  │   └───────────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                    │                                     │
│                    ┌───────────────┼───────────────┐                     │
│                    ▼               ▼               ▼                     │
│             ┌──────────┐    ┌──────────┐    ┌──────────┐                │
│             │PostgreSQL│    │   Redis  │    │ Firebase  │                │
│             │ (Primary)│    │ (Cache)  │    │ (Push)    │                │
│             └──────────┘    └──────────┘    └──────────┘                │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                    FLUTTER STAFF APP                                │ │
│  │                                                                      │ │
│  │   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐             │ │
│  │   │ Dashboard│ │  Tasks   │ │  Orders   │ │  Profile  │             │ │
│  │   │  Screen   │ │  Screen  │ │  Screen   │ │  Screen   │             │ │
│  │   └──────────┘ └──────────┘ └──────────┘ └──────────┘             │ │
│  │                                                                      │ │
│  │   ┌────────────────────────────────────────────────────────────┐    │ │
│  │   │               STATE MANAGEMENT (Riverpod)                 │    │ │
│  │   └────────────────────────────────────────────────────────────┘    │ │
│  │                                                                      │ │
│  │   ┌──────────┐ ┌──────────┐ ┌──────────┐                         │ │
│  │   │   API     │ │ WebSocket│ │  Push    │                         │ │
│  │   │  Client   │ │  Client  │ │ Notifs   │                         │ │
│  │   └──────────┘ └──────────┘ └──────────┘                         │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Cache/PubSub**: Redis 7
- **Auth**: JWT with refresh tokens
- **Validation**: Pydantic v2
- **WebSocket**: FastAPI WebSocket

### Frontend (Web)
- **Framework**: React 18
- **Build Tool**: Vite
- **Language**: TypeScript
- **Routing**: React Router v6
- **State**: TanStack Query
- **Styling**: Tailwind CSS
- **HTTP**: Axios
- **Forms**: React Hook Form + Zod

### Mobile (Flutter)
- **Framework**: Flutter 3.16+
- **Language**: Dart 3
- **State**: Riverpod
- **Navigation**: GoRouter
- **HTTP**: Dio
- **Storage**: flutter_secure_storage
- **WebSocket**: web_socket_channel
- **Notifications**: firebase_messaging

## Data Flow

### Order Creation Flow
```
Customer scans QR
        ↓
Customer Web App (Menu Display)
        ↓
POST /api/v1/orders (REST)
        ↓
Backend validates & saves to PostgreSQL
        ↓
Domain Event: OrderCreated
        ↓
Redis Pub/Sub (order:new)
        ↓
WebSocket Gateway broadcasts to:
  - Kitchen (relevant station)
  - Admin Dashboard
  - Token Display
  - Staff App (if delivery)
        ↓
Push notification to relevant staff
```

### Real-time Architecture
```
                    ┌─────────────────┐
                    │   WebSocket     │
                    │   Gateway       │
                    │                 │
                    │  /ws/{token}   │
                    └────────┬────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
           ▼                 ▼                 ▼
    ┌────────────┐    ┌────────────┐    ┌────────────┐
    │  Kitchen   │    │   Staff    │    │   Admin    │
    │    KDS     │    │    App     │    │ Dashboard  │
    └────────────┘    └────────────┘    └────────────┘

WebSocket Events:
- order:created    - task:assigned    - notification:new
- order:updated    - task:updated     - room:status_changed
- order:ready      - inventory:low    - payment:received
- order:completed  - maintenance:new  - analytics:updated
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      REQUEST FLOW                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Client                                                      │
│    │                                                        │
│    ▼                                                        │
│  HTTPS ─────────────────────────────────────────────────▶   │
│                                                              │
│  FastAPI Middleware                                         │
│    │                                                        │
│    ├── CORS Middleware                                       │
│    ├── Rate Limiter (Redis-based)                           │
│    ├── Request Logger                                        │
│    └── Security Headers                                      │
│    │                                                        │
│    ▼                                                        │
│  Authentication (JWT)                                        │
│    │                                                        │
│    ├── Verify Access Token                                  │
│    ├── Check Token Expiry                                   │
│    └── If expired → Refresh Token Flow                     │
│    │                                                        │
│    ▼                                                        │
│  RBAC Permission Check                                      │
│    │                                                        │
│    ├── Load User Role                                       │
│    ├── Load Role Permissions                                │
│    └── Validate Endpoint Permission                        │
│    │                                                        │
│    ▼                                                        │
│  Route Handler                                              │
│    │                                                        │
│    ├── Validate Request (Pydantic)                         │
│    ├── Execute Service Layer                                │
│    └── Return Response                                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRODUCTION SETUP                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                      NGINX                               │ │
│  │                                                         │ │
│  │   /api/*        → Backend (FastAPI)                    │ │
│  │   /admin/*      → Admin Frontend                       │ │
│  │   /customer/*   → Customer Frontend                   │ │
│  │   /pos/*        → POS Frontend                        │ │
│  │   /kitchen/*    → Kitchen Display                      │ │
│  │   /ws           → WebSocket Gateway                    │ │
│  └─────────────────────────────────────────────────────────┘ │
│                            │                                 │
│         ┌──────────────────┼──────────────────┐              │
│         │                  │                  │              │
│         ▼                  ▼                  ▼              │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐      │
│  │   Backend   │   │  Frontend   │   │   Redis     │      │
│  │  (FastAPI)  │   │   (React)   │   │   Server    │      │
│  │   [x3]      │   │   [x2]      │   │             │      │
│  └─────────────┘   └─────────────┘   └─────────────┘      │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────┐   ┌─────────────┐                         │
│  │ PostgreSQL  │   │  Firebase   │                         │
│  │   [x1]     │   │  Cloud Msg   │                         │
│  └─────────────┘   └─────────────┘                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## State Machines

### Order State Machine
```
CREATED → CONFIRMED → ACCEPTED → PREPARING → READY → OUT_FOR_DELIVERY → DELIVERED → COMPLETED
   │         │          │          │          │              │            │           │
   └─────────┴──────────┴──────────┴──────────┴──────────────┴────────────┴───────────┘
   (CANCELLED allowed from CREATED, CONFIRMED, ACCEPTED states)
```

### Reservation State Machine
```
PENDING → CONFIRMED → CHECKED_IN → CHECKED_OUT
   │         │           │
   └─────────┴───────────┴──────────→ CANCELLED / NO_SHOW
```

### Task State Machine
```
PENDING → ASSIGNED → ACCEPTED → IN_PROGRESS → COMPLETED
   │                                              │
   └──────────────────────────────────────────────┴──→ CANCELLED
```

## Environment Configuration

### Development
- Local PostgreSQL on port 5432
- Local Redis on port 6379
- Backend on port 8000
- React dev server on port 5173
- Flutter on device/emulator

### Production
- PostgreSQL managed service (RDS/Cloud SQL)
- Redis managed service (ElastiCache/Redis Cloud)
- Backend containerized, scalable
- CDN for static assets
- Load balancer for frontend

## Scalability Considerations

1. **Horizontal Scaling**: Backend instances stateless, Redis for session state
2. **Database**: Read replicas for analytics, sharding future consideration
3. **Caching**: Redis for menu data, session data, rate limiting
4. **CDN**: Static assets served via CDN
5. **WebSocket**: Redis Pub/Sub for multi-instance WebSocket support

## Future Considerations

1. **Multi-Property Support**: Property ID on all entities
2. **AI Layer**: Optional demand forecasting, anomaly detection
3. **Offline Support**: PWA with service workers for customer app
4. **Analytics Pipeline**: Real-time analytics with ClickHouse/Redshift
5. **Payment Gateway**: Integration-ready payment abstraction
