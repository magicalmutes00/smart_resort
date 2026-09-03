"""Auth tests — password hashing, JWT, role permissions."""
import pytest
from app.core.security import (
    get_password_hash, verify_password,
    create_access_token, decode_token,
    create_refresh_token, decode_refresh_token,
)
from app.core.rbac import DEFAULT_ROLE_PERMISSIONS, has_permission, get_user_permissions


def test_password_hash_roundtrip():
    """Hashing and verification should be consistent."""
    password = "test_password_123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)


def test_jwt_roundtrip():
    """JWT tokens should encode and decode payload."""
    payload = {"sub": "user-123", "email": "test@example.com"}
    token = create_access_token(payload)
    decoded = decode_token(token)
    assert decoded["sub"] == "user-123"
    assert decoded["email"] == "test@example.com"
    assert decoded["type"] == "access"


def test_refresh_token_validation():
    """Refresh tokens should be distinct from access tokens."""
    payload = {"sub": "user-123"}
    access = create_access_token(payload)
    refresh = create_refresh_token(payload)

    access_decoded = decode_token(access)
    refresh_decoded = decode_refresh_token(refresh)

    assert access_decoded["type"] == "access"
    assert refresh_decoded["type"] == "refresh"


def test_superadmin_has_wildcard():
    """SUPER_ADMIN should have wildcard permission."""
    perms = get_user_permissions("SUPER_ADMIN")
    assert "*" in perms


def test_kitchen_has_limited_permissions():
    """KITCHEN should have limited but appropriate permissions."""
    perms = get_user_permissions("KITCHEN")
    assert "orders.read" in perms
    assert "orders.status_update" in perms
    assert "*" not in perms
    # Kitchen should not have payment permissions
    assert "payments.create" not in perms


def test_waiter_has_order_permissions():
    """WAITER should be able to create orders but not manage inventory."""
    perms = get_user_permissions("WAITER")
    assert "orders.create" in perms
    assert "orders.update" in perms
    assert "inventory.read" not in perms


def test_housekeeping_limited_scope():
    """HOUSEKEEPING should only have housekeeping and room read."""
    perms = get_user_permissions("HOUSEKEEPING")
    assert "housekeeping.read" in perms
    assert "rooms.read" in perms
    # Should NOT have order permissions
    assert "orders.create" not in perms


def test_has_permission_logic():
    """Verify permission check logic."""
    perms = ["orders.read", "orders.create"]
    assert has_permission(perms, "orders.read") is True
    assert has_permission(perms, "orders.delete") is False
    assert has_permission(["*"], "anything") is True
