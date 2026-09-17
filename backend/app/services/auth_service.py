import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.auth import LoginRequest, LoginResponse, RefreshRequest


def _request_token(
    grant_type: str, payload: dict, *, unauthorized_detail: str
) -> LoginResponse:
    try:
        response = httpx.post(
            f"{settings.supabase_url.rstrip('/')}/auth/v1/token",
            params={"grant_type": grant_type},
            headers={
                "apikey": settings.supabase_publishable_key,
            },
            json=payload,
            timeout=10,
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is unavailable",
        ) from exc

    if response.status_code == 429:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many attempts, please try again later",
        )

    if response.status_code == 400:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=unauthorized_detail,
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Authentication service returned an unexpected error",
        )

    try:
        body = response.json()
        return LoginResponse(
            access_token=body["access_token"],
            refresh_token=body["refresh_token"],
            token_type=body.get("token_type", "bearer"),
            expires_in=body["expires_in"],
            expires_at=body["expires_at"],
        )
    except (ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Authentication service returned an unexpected response",
        ) from exc


def login(request: LoginRequest) -> LoginResponse:
    return _request_token(
        "password",
        request.model_dump(),
        unauthorized_detail="Invalid email or password",
    )


def refresh(request: RefreshRequest) -> LoginResponse:
    return _request_token(
        "refresh_token",
        request.model_dump(),
        unauthorized_detail="Invalid or expired refresh token",
    )


def logout(access_token: str) -> None:
    try:
        response = httpx.post(
            f"{settings.supabase_url.rstrip('/')}/auth/v1/logout",
            headers={
                "apikey": settings.supabase_publishable_key,
                "Authorization": f"Bearer {access_token}",
            },
            timeout=10,
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is unavailable",
        ) from exc

    if response.status_code in (401, 403):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Authentication service returned an unexpected error",
        )
