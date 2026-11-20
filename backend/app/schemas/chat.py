from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.common import UtcDatetime

MAX_MESSAGE_LENGTH = 2000


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request_id: UUID
    conversation_id: int | None = Field(default=None, gt=0, strict=True)
    policy_id: int | None = Field(default=None, gt=0, strict=True)
    message: str = Field(min_length=1, max_length=MAX_MESSAGE_LENGTH)

    @model_validator(mode="after")
    def validate_send(self):
        if (self.conversation_id is None) == (self.policy_id is None):
            raise ValueError("Exactly one conversation_id or policy_id is required")
        if not self.message.strip() or "\0" in self.message:
            raise ValueError("Message must contain text and no null characters")
        return self


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: Literal["USER", "ASSISTANT"]
    content: str
    created_at: UtcDatetime


class ChatResponse(BaseModel):
    conversation_id: int
    reply: str
    messages: list[MessageResponse]
