from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.schemas.policy import PolicySummary


class ConversationCreateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["no_policies", "ready", "selection_required"]
    conversation_id: int | None
    selected_policy: PolicySummary | None
    policy_choices: list[PolicySummary]
