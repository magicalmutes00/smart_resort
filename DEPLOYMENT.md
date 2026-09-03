# SmartResort — Deployment Guide

This document covers production deployment, environment setup, and operational practices for SmartResort.

---

## 1. Production Environment Variables

Copy `.env.example` to `.env` and populate real secrets:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `JWT_SECRET` | Strong random secret (min 32 chars) |
| `JWT_REFRESH_SECRET` | Separate secret for refresh tokens |
| `CORS_ORIGINS` | Comma-separated allowed origins |
| `PAYMENT_PROVIDER_KEY` | Razorpay/UPI provider key |
| `PAYMENT_PROVIDER_SECRET` | Provider secret |
| `FIREBASE_*` | FCM push notification config |
| `SMTP_*` | Email notification settings |

**Security rules:**
- Never commit `.env` or secrets to Git.
- Rotate `JWT_SECRET` every 90 days.
- Store `.env` with `chmod 600`.
- Use a secret manager (AWS Secrets Manager, HashiCorp Vault) in production.

---

## 2. Docker Production Build

Build the backend image:

```bash
cd smartresort
# Build from Dockerfile in backend/
docker build -t smartresort-backend:1.0.0 -f backend/Dockerfile .
```

Run production services:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 3. Database Migration Strategy

Before deploying:

```bash
# 1. Backup current DB
pg_dump -h $DB_HOST -U $DB_USER -d smartresort > backup_$(date +%F).sql

# 2. Run migrations in a safe sequence
alembic upgrade head
```

Rollback procedure (if needed):

```bash
# Roll back one revision
alembic downgrade -1
```

---

## 4. Monitoring

- **Health endpoint:** `/api/v1/health`
- **Database health:** Check connection pool and query latency
- **Redis health:** Monitor pub/sub message rates
- **WebSocket health:** Monitor connection count and disconnect rate

---

## 5. Logging

The backend uses Python standard logging. Configure log aggregation via:
- Docker Compose logs: `docker compose logs -f backend`
- Log rotation with `logrotate`
- Centralized logging (ELK, CloudWatch, or Datadog) recommended

---

## 6. CI/CD Pipeline

Reference `.github/workflows/ci.yml`. Key stages:
- Install Python dependencies
- Start PostgreSQL service
- Apply database migrations
- Run pytest with coverage
- Fail if coverage drops below 70% or tests fail

---

## 7. Deployment Checklist

Before deploying to production:

- [ ] All `.env` secrets are real (not placeholder)
- [ ] `JWT_SECRET` changed from development value
- [ ] Database migrations applied (`alembic upgrade head`)
- [ ] Seed data cleared from production (`DELETE FROM users WHERE email LIKE '%dev%'`)
- [ ] CORS configured for production domains
- [ ] SSL certificate configured (Nginx/Traefik)
- [ ] Rate limiting enabled (Redis-based)
- [ ] Monitoring and alerting configured
- [ ] Backup schedule configured (daily DB dumps)
- [ ] Payment provider webhook URLs configured
- [ ] Push notification (FCM) project configured

---

## 8. Security Review Points

- Input validation enforced via Pydantic on every endpoint
- SQL injection prevented by SQLAlchemy ORM
- Rate limiting via Redis for auth endpoints
- JWT tokens rotate (access + refresh)
- Secure headers via middleware (`X-Content-Type-Options`, `X-Frame-Options`, etc.)
- No secrets in frontend/mobile code
- Flutter tokens stored in `flutter_secure_storage` (encrypted keystore/keychain)
- Audit logs record significant actions (not secrets)

---

## 9. Scaling Considerations

- **Backend:** Stateless — scale horizontally with load balancer
- **WebSocket:** Use Redis pub/sub for multi-instance real-time event distribution
- **PostgreSQL:** Read replicas for analytics; sharding future consideration
- **Redis:** Cluster mode for high availability
- **Static assets:** Serve via CDN for React frontend
