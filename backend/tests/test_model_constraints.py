from sqlalchemy import UniqueConstraint

from app.models import InsurancePlanVersion, PlanVariant


def _unique_constraint(model: type, name: str) -> UniqueConstraint:
    constraint = next(
        item
        for item in model.__table__.constraints
        if isinstance(item, UniqueConstraint) and item.name == name
    )
    return constraint


def test_plan_version_has_natural_key_constraint() -> None:
    constraint = _unique_constraint(
        InsurancePlanVersion,
        "uq_insurance_plan_version",
    )

    assert list(constraint.columns.keys()) == ["name", "version"]


def test_plan_variant_has_null_safe_natural_key_constraint() -> None:
    constraint = _unique_constraint(
        PlanVariant,
        "uq_plan_variant_identity",
    )

    assert list(constraint.columns.keys()) == [
        "plan_version_id",
        "territory",
        "sport_category",
    ]
    assert (
        constraint.dialect_options["postgresql"]["nulls_not_distinct"]
        is True
    )
