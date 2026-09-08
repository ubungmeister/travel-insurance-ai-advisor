from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import (
    CoverageType,
    InsurancePlanVersion,
    InsuredPerson,
    PlanVariant,
    Policy,
    User,
    VariantCoverage,
)


COVERAGE_TYPES = {
    "MEDICAL_EXPENSES": "Medical expenses",
    "DENTAL_TREATMENT": "Emergency dental treatment",
    "PERMANENT_INJURY": "Permanent injury",
    "LIABILITY": "Personal liability",
    "BAGGAGE": "Baggage damage or theft",
    "TRIP_CANCELLATION": "Trip cancellation",
    "FLIGHT_DELAY": "Flight delay",
}


PLAN_VARIANTS = (
    {
        "plan": "Standard",
        "territory": "EUROPE",
        "sport_category": None,
        "coverages": {
            "MEDICAL_EXPENSES": "5000000",
            "DENTAL_TREATMENT": "5000",
        },
    },
    {
        "plan": "Dominant",
        "territory": "EUROPE",
        "sport_category": None,
        "coverages": {
            "MEDICAL_EXPENSES": "15000000",
            "DENTAL_TREATMENT": "10000",
            "PERMANENT_INJURY": "600000",
            "LIABILITY": "15000000",
            "BAGGAGE": "15000",
            "TRIP_CANCELLATION": "10000",
            "FLIGHT_DELAY": "5000",
        },
    },
    {
        "plan": "Premiant",
        "territory": "EUROPE",
        "sport_category": None,
        "coverages": {
            "MEDICAL_EXPENSES": "100000000",
            "DENTAL_TREATMENT": "20000",
            "PERMANENT_INJURY": "800000",
            "LIABILITY": "30000000",
            "BAGGAGE": "50000",
            "TRIP_CANCELLATION": "30000",
            "FLIGHT_DELAY": "15000",
        },
    },
    {
        "plan": "Standard",
        "territory": "WORLD",
        "sport_category": None,
        "coverages": {
            "MEDICAL_EXPENSES": "5000000",
            "DENTAL_TREATMENT": "10000",
        },
    },
    {
        "plan": "Dominant",
        "territory": "WORLD",
        "sport_category": None,
        "coverages": {
            "MEDICAL_EXPENSES": "15000000",
            "DENTAL_TREATMENT": "20000",
            "PERMANENT_INJURY": "600000",
            "LIABILITY": "15000000",
            "BAGGAGE": "15000",
            "TRIP_CANCELLATION": "10000",
            "FLIGHT_DELAY": "5000",
        },
    },
    {
        "plan": "Premiant",
        "territory": "WORLD",
        "sport_category": None,
        "coverages": {
            "MEDICAL_EXPENSES": "100000000",
            "DENTAL_TREATMENT": "40000",
            "PERMANENT_INJURY": "800000",
            "LIABILITY": "30000000",
            "BAGGAGE": "50000",
            "TRIP_CANCELLATION": "30000",
            "FLIGHT_DELAY": "15000",
        },
    },
    {
        "plan": "Domestic",
        "territory": "DOMESTIC",
        "sport_category": "RECREATIONAL",
        "coverages": {
            "PERMANENT_INJURY": "400000",
            "LIABILITY": "5000000",
            "BAGGAGE": "15000",
        },
    },
    {
        "plan": "Domestic",
        "territory": "DOMESTIC",
        "sport_category": "WINTER_OR_RISKY",
        "coverages": {
            "PERMANENT_INJURY": "600000",
            "LIABILITY": "15000000",
            "BAGGAGE": "25000",
        },
    },
)


def _seed_coverage_types(db: Session) -> dict[str, CoverageType]:
    coverage_types: dict[str, CoverageType] = {}
    for code, name in COVERAGE_TYPES.items():
        coverage_type = db.scalar(
            select(CoverageType).where(CoverageType.code == code)
        )
        if coverage_type is None:
            coverage_type = CoverageType(code=code, name=name)
            db.add(coverage_type)
        else:
            coverage_type.name = name
        coverage_types[code] = coverage_type

    db.flush()
    return coverage_types


def _get_or_create_plan(db: Session, name: str) -> InsurancePlanVersion:
    plan = db.scalar(
        select(InsurancePlanVersion).where(
            InsurancePlanVersion.name == name,
            InsurancePlanVersion.version == 1,
        )
    )
    if plan is None:
        plan = InsurancePlanVersion(
            name=name,
            version=1,
            valid_from=date(2026, 1, 1),
            valid_to=None,
        )
        db.add(plan)
        db.flush()
    return plan


def _get_or_create_variant(
    db: Session,
    plan: InsurancePlanVersion,
    territory: str,
    sport_category: str | None,
) -> PlanVariant:
    sport_filter = (
        PlanVariant.sport_category.is_(None)
        if sport_category is None
        else PlanVariant.sport_category == sport_category
    )
    variant = db.scalar(
        select(PlanVariant).where(
            PlanVariant.plan_version_id == plan.id,
            PlanVariant.territory == territory,
            sport_filter,
        )
    )
    if variant is None:
        variant = PlanVariant(
            plan_version_id=plan.id,
            territory=territory,
            sport_category=sport_category,
        )
        db.add(variant)
        db.flush()
    return variant


def _seed_product_catalogue(
    db: Session,
) -> dict[tuple[str, str, str | None], PlanVariant]:
    coverage_types = _seed_coverage_types(db)
    variants: dict[tuple[str, str, str | None], PlanVariant] = {}

    for definition in PLAN_VARIANTS:
        plan_name = str(definition["plan"])
        territory = str(definition["territory"])
        sport_category = definition["sport_category"]
        assert sport_category is None or isinstance(sport_category, str)

        plan = _get_or_create_plan(db, plan_name)
        variant = _get_or_create_variant(
            db,
            plan,
            territory,
            sport_category,
        )
        variants[(plan_name, territory, sport_category)] = variant

        coverages = definition["coverages"]
        assert isinstance(coverages, dict)
        for code, amount in coverages.items():
            coverage_type = coverage_types[code]
            variant_coverage = db.scalar(
                select(VariantCoverage).where(
                    VariantCoverage.plan_variant_id == variant.id,
                    VariantCoverage.coverage_type_id == coverage_type.id,
                )
            )
            if variant_coverage is None:
                variant_coverage = VariantCoverage(
                    plan_variant_id=variant.id,
                    coverage_type_id=coverage_type.id,
                    limit_amount=Decimal(amount),
                    currency="CZK",
                )
                db.add(variant_coverage)
            else:
                variant_coverage.limit_amount = Decimal(amount)
                variant_coverage.currency = "CZK"

    db.flush()
    return variants


def _seed_demo_policy(
    db: Session,
    variants: dict[tuple[str, str, str | None], PlanVariant],
) -> None:
    email = "demo@example.com"
    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        user = User(email=email)
        db.add(user)
        db.flush()

    variant = variants[("Dominant", "EUROPE", None)]
    policy = db.scalar(
        select(Policy).where(
            Policy.user_id == user.id,
            Policy.plan_variant_id == variant.id,
            Policy.start_date == date(2026, 8, 26),
            Policy.end_date == date(2026, 9, 5),
        )
    )
    if policy is None:
        policy = Policy(
            policy_number="POL-2026-000001",
            user_id=user.id,
            plan_variant_id=variant.id,
            trip_purpose="VACATION",
            declared_sport_category="RECREATIONAL",
            start_date=date(2026, 8, 26),
            end_date=date(2026, 9, 5),
            status="ACTIVE",
            price_paid=Decimal("45.00"),
            currency="CZK",
        )
        db.add(policy)
        db.flush()
    else:
        policy.policy_number = "POL-2026-000001"
        policy.trip_purpose = "VACATION"
        policy.declared_sport_category = "RECREATIONAL"
        policy.status = "ACTIVE"
        policy.price_paid = Decimal("45.00")
        policy.currency = "CZK"

    insured_person = db.scalar(
        select(InsuredPerson).where(
            InsuredPerson.policy_id == policy.id,
            InsuredPerson.name == "Demo User",
            InsuredPerson.date_of_birth == date(1990, 5, 15),
        )
    )
    if insured_person is None:
        db.add(
            InsuredPerson(
                policy_id=policy.id,
                name="Demo User",
                date_of_birth=date(1990, 5, 15),
            )
        )


def seed_database(db: Session) -> None:
    variants = _seed_product_catalogue(db)
    _seed_demo_policy(db, variants)


def main() -> None:
    with SessionLocal() as db:
        try:
            seed_database(db)
            db.commit()
        except Exception:
            db.rollback()
            raise

    print("Seed completed successfully.")


if __name__ == "__main__":
    main()
