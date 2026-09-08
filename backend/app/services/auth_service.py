import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.auth import LoginRequest, LoginResponse


def login(request: LoginRequest) -> LoginResponse:
     response = httpx.post(
        f"{settings.supabase_url.rstrip('/')}/auth/v1/token",
        params={"grant_type": "password"},
        headers={
            "apikey": settings.supabase_publishable_key,
        },
        json=request.model_dump(),
        timeout=10,
    )
     if response.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
     body = response.json()
      
     return LoginResponse(
        access_token=body["access_token"],
        refresh_token=body["refresh_token"],
        token_type=body.get("token_type", "bearer"),
    )