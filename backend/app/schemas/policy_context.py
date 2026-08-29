from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CoverageContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=150)
    limit_amount: Decimal = Field(ge=0)
    currency: str = Field(min_length=3, max_length=3)


class InsuredPersonContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    age: int = Field(ge=0, le=130)


class PolicyContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    policy_id: int = Field(gt=0)
    plan_name: str = Field(min_length=1, max_length=50)
    plan_version: int = Field(gt=0)
    territory: str = Field(min_length=1, max_length=30)
    trip_purpose: str = Field(min_length=1, max_length=50)
    sport_category: str = Field(min_length=1, max_length=50)
    start_date: date
    end_date: date
    insured_people: list[InsuredPersonContext]
    coverages: list[CoverageContext]
