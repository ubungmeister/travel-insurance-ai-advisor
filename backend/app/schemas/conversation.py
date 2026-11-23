from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.policy import PolicySummary
from app.schemas.chat import MessageResponse
from app.schemas.common import UtcDatetime


class ConversationCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    policy_id: int | None = Field(default=None, gt=0, strict=True)


class ConversationCreateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["no_policies", "ready", "selection_required"]
    conversation_id: int | None
    selected_policy: PolicySummary | None
    policy_choices: list[PolicySummary]


class ConversationSummary(BaseModel):
    conversation_id: int
    selected_policy: PolicySummary | None
    created_at: UtcDatetime
    last_activity_at: UtcDatetime


class ConversationDetail(BaseModel):
    conversation_id: int
    selected_policy: PolicySummary | None
    created_at: UtcDatetime
    messages: list[MessageResponse]
