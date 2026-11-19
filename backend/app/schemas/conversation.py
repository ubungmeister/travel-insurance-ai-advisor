from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.policy import PolicySummary


class ConversationCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    policy_id: int | None = Field(default=None, gt=0, strict=True)


class ConversationCreateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["no_policies", "ready", "selection_required"]
    conversation_id: int | None
    selected_policy: PolicySummary | None
    policy_choices: list[PolicySummary]
