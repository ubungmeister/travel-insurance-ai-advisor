from sqlalchemy import CheckConstraint, Index, UniqueConstraint

from app.models import (
    InsurancePlanVersion,
    InsuredPerson,
    PlanVariant,
    Policy,
    VariantCoverage,
)


def _unique_constraint(model: type, name: str) -> UniqueConstraint:
    constraint = next(
        item
        for item in model.__table__.constraints
        if isinstance(item, UniqueConstraint) and item.name == name
    )
    return constraint


def _check_constraint(model: type, name: str) -> CheckConstraint:
    return next(
        item
        for item in model.__table__.constraints
        if isinstance(item, CheckConstraint) and item.name == name
    )


def _index(model: type, name: str) -> Index:
    return next(item for item in model.__table__.indexes if item.name == name)


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


def test_plan_version_rejects_invalid_version_and_dates() -> None:
    assert _check_constraint(
        InsurancePlanVersion,
        "ck_insurance_plan_version_positive",
    ).sqltext.text == "version > 0"
    assert _check_constraint(
        InsurancePlanVersion,
        "ck_insurance_plan_version_valid_dates",
    ).sqltext.text == "valid_to IS NULL OR valid_to >= valid_from"


def test_policy_has_business_constraints_and_lookup_indexes() -> None:
    assert _unique_constraint(Policy, "uq_policies_policy_number")
    assert _check_constraint(
        Policy,
        "ck_policy_valid_date_range",
    ) is not None
    assert _check_constraint(
        Policy,
        "ck_policy_non_negative_price",
    ) is not None
    assert _check_constraint(
        Policy,
        "ck_policy_valid_status",
    ) is not None
    assert list(
        _index(Policy, "ix_policies_user_status_dates").columns.keys()
    ) == ["user_id", "status", "start_date", "end_date"]
    assert list(
        _index(Policy, "ix_policies_plan_variant_id").columns.keys()
    ) == ["plan_variant_id"]


def test_variant_coverage_rejects_negative_limits() -> None:
    assert _check_constraint(
        VariantCoverage,
        "ck_variant_coverage_non_negative_limit",
    ) is not None
    assert list(
        _index(
            VariantCoverage,
            "ix_variant_coverages_coverage_type_id",
        ).columns.keys()
    ) == ["coverage_type_id"]


def test_insured_person_is_deleted_with_its_policy() -> None:
    foreign_key = next(iter(InsuredPerson.__table__.c.policy_id.foreign_keys))

    assert foreign_key.ondelete == "CASCADE"
    assert InsuredPerson.__table__.c.policy_id.index is True
    assert Policy.insured_people.property.cascade.delete_orphan is True
