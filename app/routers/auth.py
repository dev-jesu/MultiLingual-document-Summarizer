"""
Auth Router — username + password login, returns JWT.
No Supabase Auth — uses local in-memory user store.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

from app.db import local_db as db
from app.services.auth import create_access_token, get_current_user, CurrentUser, require_role

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str
    full_name: str


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    """Authenticate with username + password and return a local JWT."""
    user = db.get_user_by_username(payload.username)
    if not user or not db.verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = create_access_token(
        user_id=user["id"],
        username=user["username"],
        role=user["role"],
    )
    return TokenResponse(
        access_token=token,
        role=user["role"],
        username=user["username"],
        full_name=user["full_name"],
    )


@router.get("/me")
async def get_me(current_user: CurrentUser = Depends(get_current_user)):
    """Return the profile of the currently authenticated user."""
    user = db.get_user_by_id(current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return db._safe_user(user)
