"""RBAC permission dependencies."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.models.role import Role

security = HTTPBearer(auto_error=False)


# Permission constants
class Permission:
    # Auth
    AUTH_LOGIN = "auth.login"
    AUTH_REFRESH = "auth.refresh"

    # Orders
    ORDERS_READ = "orders.read"
    ORDERS_CREATE = "orders.create"
    ORDERS_UPDATE = "orders.update"
    ORDERS_CANCEL = "orders.cancel"
    ORDERS_STATUS_UPDATE = "orders.status_update"

    # Menu
    MENU_READ = "menu.read"
    MENU_CREATE = "menu.create"
    MENU_UPDATE = "menu.update"
    MENU_DELETE = "menu.delete"

    # Tasks
    TASKS_READ = "tasks.read"
    TASKS_CREATE = "tasks.create"
    TASKS_ASSIGN = "tasks.assign"
    TASKS_ACCEPT = "tasks.accept"
    TASKS_START = "tasks.start"
    TASKS_COMPLETE = "tasks.complete"

    # Payments
    PAYMENTS_READ = "payments.read"
    PAYMENTS_CREATE = "payments.create"
    PAYMENTS_REFUND = "payments.refund"

    # Rooms
    ROOMS_READ = "rooms.read"
    ROOMS_UPDATE = "rooms.update"
    ROOMS_STATUS_CHANGE = "rooms.status_change"

    # Reservations
    RESERVATIONS_READ = "reservations.read"
    RESERVATIONS_CREATE = "reservations.create"
    RESERVATIONS_UPDATE = "reservations.update"
    RESERVATIONS_CHECKIN = "reservations.check_in"
    RESERVATIONS_CHECKOUT = "reservations.check_out"

    # Housekeeping
    HOUSEKEEPING_READ = "housekeeping.read"
    HOUSEKEEPING_CREATE = "housekeeping.create"
    HOUSEKEEPING_UPDATE = "housekeeping.update"

    # Maintenance
    MAINTENANCE_READ = "maintenance.read"
    MAINTENANCE_CREATE = "maintenance.create"
    MAINTENANCE_UPDATE = "maintenance.update"

    # Inventory
    INVENTORY_READ = "inventory.read"
    INVENTORY_ADJUST = "inventory.adjust"
    INVENTORY_UPDATE = "inventory.update"

    # Reports
    REPORTS_READ = "reports.read"

    # Users
    USERS_READ = "users.read"
    USERS_CREATE = "users.create"
    USERS_UPDATE = "users.update"

    # Properties
    PROPERTIES_READ = "properties.read"
    PROPERTIES_UPDATE = "properties.update"


# Default role permission mapping
DEFAULT_ROLE_PERMISSIONS = {
    "SUPER_ADMIN": ["*"],  # All permissions
    "OWNER": [
        Permission.ORDERS_READ, Permission.ORDERS_UPDATE,
        Permission.MENU_READ, Permission.MENU_CREATE, Permission.MENU_UPDATE,
        Permission.TASKS_READ, Permission.TASKS_CREATE, Permission.TASKS_ASSIGN,
        Permission.PAYMENTS_READ, Permission.PAYMENTS_REFUND,
        Permission.ROOMS_READ, Permission.ROOMS_UPDATE, Permission.ROOMS_STATUS_CHANGE,
        Permission.RESERVATIONS_READ, Permission.RESERVATIONS_CREATE, Permission.RESERVATIONS_UPDATE,
        Permission.RESERVATIONS_CHECKIN, Permission.RESERVATIONS_CHECKOUT,
        Permission.HOUSEKEEPING_READ, Permission.HOUSEKEEPING_CREATE, Permission.HOUSEKEEPING_UPDATE,
        Permission.MAINTENANCE_READ, Permission.MAINTENANCE_CREATE, Permission.MAINTENANCE_UPDATE,
        Permission.INVENTORY_READ, Permission.INVENTORY_ADJUST, Permission.INVENTORY_UPDATE,
        Permission.REPORTS_READ, Permission.USERS_READ, Permission.USERS_CREATE,
        Permission.PROPERTIES_READ, Permission.PROPERTIES_UPDATE,
    ],
    "MANAGER": [
        Permission.ORDERS_READ, Permission.ORDERS_UPDATE, Permission.ORDERS_CANCEL,
        Permission.MENU_READ, Permission.MENU_UPDATE,
        Permission.TASKS_READ, Permission.TASKS_CREATE, Permission.TASKS_ASSIGN,
        Permission.PAYMENTS_READ, Permission.PAYMENTS_REFUND,
        Permission.ROOMS_READ, Permission.ROOMS_UPDATE, Permission.ROOMS_STATUS_CHANGE,
        Permission.RESERVATIONS_READ, Permission.RESERVATIONS_CREATE, Permission.RESERVATIONS_UPDATE,
        Permission.RESERVATIONS_CHECKIN, Permission.RESERVATIONS_CHECKOUT,
        Permission.HOUSEKEEPING_READ, Permission.HOUSEKEEPING_CREATE, Permission.HOUSEKEEPING_UPDATE,
        Permission.MAINTENANCE_READ, Permission.MAINTENANCE_CREATE, Permission.MAINTENANCE_UPDATE,
        Permission.INVENTORY_READ, Permission.INVENTORY_ADJUST,
        Permission.REPORTS_READ, Permission.USERS_READ,
        Permission.PROPERTIES_READ,
    ],
    "RECEPTIONIST": [
        Permission.ROOMS_READ, Permission.ROOMS_STATUS_CHANGE,
        Permission.RESERVATIONS_READ, Permission.RESERVATIONS_CREATE,
        Permission.RESERVATIONS_UPDATE, Permission.RESERVATIONS_CHECKIN,
        Permission.RESERVATIONS_CHECKOUT, Permission.PAYMENTS_READ,
    ],
    "CASHIER": [
        Permission.ORDERS_READ, Permission.ORDERS_CREATE,
        Permission.PAYMENTS_READ, Permission.PAYMENTS_CREATE,
    ],
    "KITCHEN": [
        Permission.ORDERS_READ, Permission.ORDERS_STATUS_UPDATE,
        Permission.MENU_READ, Permission.TASKS_READ,
    ],
    "WAITER": [
        Permission.ORDERS_READ, Permission.ORDERS_CREATE, Permission.ORDERS_UPDATE,
        Permission.PAYMENTS_CREATE, Permission.MENU_READ,
    ],
    "DELIVERY_STAFF": [
        Permission.TASKS_READ, Permission.TASKS_ACCEPT,
        Permission.TASKS_START, Permission.TASKS_COMPLETE,
        Permission.ORDERS_READ,
    ],
    "HOUSEKEEPING": [
        Permission.HOUSEKEEPING_READ, Permission.HOUSEKEEPING_CREATE,
        Permission.HOUSEKEEPING_UPDATE, Permission.ROOMS_READ,
    ],
    "MAINTENANCE": [
        Permission.MAINTENANCE_READ, Permission.MAINTENANCE_CREATE,
        Permission.MAINTENANCE_UPDATE, Permission.ROOMS_READ,
    ],
    "INVENTORY_MANAGER": [
        Permission.INVENTORY_READ, Permission.INVENTORY_ADJUST,
        Permission.INVENTORY_UPDATE, Permission.MENU_READ,
    ],
}


def get_user_permissions(role_name: str) -> list[str]:
    """Get permissions for a role."""
    return DEFAULT_ROLE_PERMISSIONS.get(role_name, [])


def has_permission(permissions: list[str], required: str) -> bool:
    """Check if permissions list includes the required one or wildcard."""
    if "*" in permissions:
        return True
    return required in permissions


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Get the current authenticated user from JWT."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    try:
        user_uuid = UUID(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user id",
        )

    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )

    return user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Get current user without raising on missing token."""
    if not credentials:
        return None

    payload = decode_token(credentials.credentials)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    try:
        user_uuid = UUID(user_id)
    except (ValueError, TypeError):
        return None

    return db.query(User).filter(User.id == user_uuid, User.is_active == True).first()


def get_user_role_name(user: User) -> str:
    """Get role name for user."""
    if not user.role_id:
        return ""
    # The role name lookup is done in get_user_with_role below
    return user._role_name_cache if hasattr(user, "_role_name_cache") else ""


def get_user_with_role(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Get user with their role name and permissions."""
    role_name = ""
    if user.role_id:
        role = db.query(Role).filter(Role.id == user.role_id).first()
        if role:
            role_name = role.name

    permissions = get_user_permissions(role_name)

    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": role_name,
        "property_id": str(user.property_id) if user.property_id else None,
        "permissions": permissions,
    }


class RequirePermission:
    """Dependency class to enforce permissions."""

    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    def __call__(self, current: dict = Depends(get_user_with_role)) -> dict:
        if not has_permission(current.get("permissions", []), self.required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {self.required_permission}",
            )
        return current
