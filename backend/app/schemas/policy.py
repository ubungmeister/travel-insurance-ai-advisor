from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.policy import PolicyStatus


class PolicySummary(BaseModel):
    """Customer-facing policy list item."""

    model_config = ConfigDict(extra="forbid")

    policy_id: int
    policy_number: str
    plan_name: str
    plan_version: int
    territory: str
    trip_purpose: str
    sport_category: str
    start_date: date
    end_date: date
    status: PolicyStatus
