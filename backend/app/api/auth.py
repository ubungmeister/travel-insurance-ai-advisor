from fastapi import APIRouter, Depends

from app.dependencies.authentication import CurrentUser, get_current_user
from app.schemas.auth import (
    CurrentUserResponse,
    LoginRequest,
    LoginResponse,
)
from app.services import auth_service


router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
)

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    return auth_service.login(request)

@router.get("/me", response_model=CurrentUserResponse)
def get_me(
    current_user: CurrentUser = Depends(get_current_user),
):
    return CurrentUserResponse(
        auth_user_id=current_user.auth_user_id,
        email=current_user.email,
    )