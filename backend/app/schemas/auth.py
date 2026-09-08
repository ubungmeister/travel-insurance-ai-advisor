from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=72)


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class CurrentUserResponse(BaseModel):
    auth_user_id: UUID
    email: str