"""Users routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from uuid import UUID

from app.core.database import get_db
from app.models.user import User
from app.models.role import Role

router = APIRouter()


class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class UserMe(BaseModel):
    id: UUID
    email: str
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: str
    permissions: list[str]

    class Config:
        from_attributes = True


@router.get("/me", response_model=UserMe)
def get_current_user(db: Session = Depends(get_db)):
    """Get current authenticated user."""
    # Placeholder - in real implementation, get from JWT
    return UserMe(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        email="admin@lakeview.com",
        username="admin",
        first_name="Admin",
        last_name="User",
        role="ADMIN",
        permissions=["*"]
    )


@router.get("/", response_model=dict)
def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all users."""
    query = db.query(User)
    if search:
        query = query.filter(
            (User.email.ilike(f"%{search}%")) |
            (User.username.ilike(f"%{search}%"))
        )

    total = query.count()
    users = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "data": [UserResponse.model_validate(u) for u in users],
        "meta": {"total": total, "page": page, "per_page": limit}
    }
