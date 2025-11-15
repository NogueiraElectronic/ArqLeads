"""
Admin Dashboard Routes.
Serves admin dashboard for lead management with JWT authentication.
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasicCredentials
from pydantic import BaseModel
import os

from app.core.auth import (
    authenticate_user,
    create_access_token,
    get_current_user
)
from app.core.config import settings

router = APIRouter(prefix="/admin", tags=["admin"])


class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """
    Authenticate admin user and return JWT token.

    Default credentials:
    - Username: admin
    - Password: admin123
    """
    user = authenticate_user(credentials.username, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires
    )

    return TokenResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/login")
async def login_page():
    """Serve the admin login page."""
    template_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "templates",
        "admin_login.html"
    )
    return FileResponse(template_path)


@router.get("/dashboard")
async def admin_dashboard(current_user: dict = Depends(get_current_user)):
    """
    Serve the admin dashboard HTML (protected endpoint).
    Requires valid JWT token.
    """
    template_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "templates",
        "admin_dashboard.html"
    )
    return FileResponse(template_path)


@router.get("/verify")
async def verify_token(current_user: dict = Depends(get_current_user)):
    """Verify if the current token is valid."""
    return {
        "valid": True,
        "user": current_user
    }
