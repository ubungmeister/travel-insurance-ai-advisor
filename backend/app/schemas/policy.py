from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.plan_variant import Territory
from app.models.policy import PolicyStatus, SportCategory, TripPurpose


class PolicySummary(BaseModel):
    """Customer-facing policy list item."""

    model_config = ConfigDict(extra="forbid")

    policy_id: int
    policy_number: str
    plan_name: str
    plan_version: int
    territory: Territory
    trip_purpose: TripPurpose
    sport_category: SportCategory
    start_date: date
    end_date: date
    status: PolicyStatus
