"""SmartResort Backend — FastAPI Application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1 import (
    auth, users, properties,
    menu, orders, tasks, tables,
    qr, inventory, housekeeping, maintenance,
    reports, payments, ai, google_auth,
)
from app.websocket.gateway import router as ws_router

app = FastAPI(
    title="SmartResort API",
    description="Digital hospitality operating system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket
app.include_router(ws_router, tags=["WebSocket"])

# API v1
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(google_auth.router, prefix="/api/v1/auth", tags=["Auth (Google)"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(properties.router, prefix="/api/v1/properties", tags=["Properties"])
app.include_router(menu.router, prefix="/api/v1/menu", tags=["Menu"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["Orders"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])
app.include_router(tables.router, prefix="/api/v1/dining", tags=["Dining"])
app.include_router(qr.router, prefix="/api/v1/qr", tags=["QR Codes"])
app.include_router(inventory.router, prefix="/api/v1/inventory", tags=["Inventory"])
app.include_router(housekeeping.router, prefix="/api/v1/housekeeping", tags=["Housekeeping"])
app.include_router(maintenance.router, prefix="/api/v1/maintenance", tags=["Maintenance"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI"])


@app.get("/api/v1/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "SmartResort API",
    }


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "name": "SmartResort API",
        "version": "1.0.0",
        "docs": "/docs",
    }
