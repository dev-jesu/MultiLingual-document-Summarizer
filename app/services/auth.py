"""
JWT Authentication Service — local HS256 tokens, no Supabase auth.

Token payload structure:
  { "sub": "<user_id>", "username": "<username>", "role": "<role>", "exp": <epoch> }
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, Request, status

from app.config import settings

# ─── JWT Config ──────────────────────────────────────────────────────────────
JWT_SECRET: str = settings.JWT_SECRET or os.getenv("JWT_SECRET", "ecourt-local-jwt-secret-change-me")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 hours


def create_access_token(user_id: str, username: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "username": username,
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


# ─── CurrentUser ─────────────────────────────────────────────────────────────

class CurrentUser:
    def __init__(self, user_id: str, username: str, role: str):
        self.id = user_id
        self.username = username
        # Keep .email as alias for username for backwards compatibility
        self.email = username
        self.role = role

    def __repr__(self) -> str:
        return f"CurrentUser(id={self.id}, username={self.username}, role={self.role})"


# ─── FastAPI Dependencies ─────────────────────────────────────────────────────

async def get_current_user(request: Request) -> CurrentUser:
    auth_header: str = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )
    token = auth_header.removeprefix("Bearer ").strip()
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))

    user_id: Optional[str] = payload.get("sub")
    username: str = payload.get("username", "")
    role: str = payload.get("role", "advocate")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload: missing sub",
        )

    return CurrentUser(user_id=user_id, username=username, role=role)


def require_role(*allowed_roles: str):
    """Dependency enforcing that the current user has one of the allowed roles."""
    async def dependency(current_user: CurrentUser = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return dependency
