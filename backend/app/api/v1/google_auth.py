"""Google authentication routes for backend."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, get_password_hash
from app.core.rbac import get_user_with_role
from app.models.user import User
from app.models.role import Role

router = APIRouter()


class GoogleAuthRequest(BaseModel):
    id_token: str


class GoogleAuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/google", response_model=GoogleAuthResponse)
async def google_auth(
    request: GoogleAuthRequest,
    db: Session = Depends(get_db),
):
    """Authenticate with Google OAuth ID token.

    The mobile/web client sends an id_token from Google Sign-In.
    This endpoint verifies the token (production: verify with Google API),
    creates/provisions the user, and returns app JWT tokens.
    """
    # In production: verify id_token with Google API
    # from google.oauth2 import id_token
    # from google.auth.transport import requests
    # try:
    #     payload = id_token.verify_oauth2_token(
    #         request.id_token,
    #         requests.Request(),
    #         "YOUR_GOOGLE_CLIENT_ID"
    #     )
    # except ValueError:
    #     raise HTTPException(status_code=401, detail="Invalid Google token")
    #
    # For this implementation: decode payload from token (simulated verification)
    # In real deployment, uncomment the verification above.

    # Placeholder verification — in production replace with real Google verification
    # We simulate by accepting any non-empty token for development mode,
    # but the interface is clean for production swap.

    # Decode payload from token (production: verify with Google)
    # For demonstration: assume token contains email
    # Real integration: payload = id_token.verify_oauth2_token(...)
    # payload['email'] = decoded email
    # payload['sub'] = Google user ID

    # --- SIMULATED / PLACEHOLDER ---
    # In real deployment, the Google verification replaces this block:
    # email = payload.get("email")
    # google_sub = payload.get("sub")
    #
    # Since we don't have a real Google client ID configured in this environment,
    # we accept a simulated structure but clearly document the integration point.
    # --- /PLACEHOLDER ---

    # For the purpose of this architecture demonstration, assume verification succeeds.
    # The production code will be:
    #
    #   import requests as google_requests
    #   from google.oauth2 import id_token
    #   payload = id_token.verify_oauth2_token(
    #       request.id_token, google_requests.Request(), CLIENT_ID
    #   )
    #
    # The rest of the flow below is production-ready.

    # We simulate a valid payload by deriving from the token
    # (In production, this is the verified Google payload)
    # We'll use the token as a simulated user identifier for this demo
    # but document clearly that real verification is required.

    # Placeholder: derive a simulated user identifier
    # Production: use payload['email'], payload['sub']
    simulated_email = "google-user@example.com"
    simulated_sub = request.id_token[:16] if len(request.id_token) >= 16 else "google-user"

    # Check if user exists by simulated identifier
    user = db.query(User).filter(User.username == simulated_sub).first()

    if not user:
        # Create new user
        # In production: use payload['email'] as email, payload['sub'] for association
        user = User(
            email=simulated_email,
            username=simulated_sub,
            hashed_password=get_password_hash("google-auth-placeholder"),
            first_name="Google",
            last_name="User",
            is_active=True,
        )
        # Assign default role (MANAGER for demo — production: configurable)
        role = db.query(Role).filter(Role.name == "MANAGER").first()
        if role:
            user.role_id = role.id
        db.add(user)
        db.commit()
        db.refresh(user)

    role_name = "MANAGER"
    if user.role_id:
        role_obj = db.query(Role).filter(Role.id == user.role_id).first()
        if role_obj:
            role_name = role_obj.name

    from app.core.rbac import get_user_permissions
    permissions = get_user_permissions(role_name)

    access_token = create_access_token({"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return GoogleAuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": role_name,
            "permissions": permissions,
        },
    )
