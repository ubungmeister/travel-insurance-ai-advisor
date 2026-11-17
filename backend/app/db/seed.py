from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import (
    CoverageType,
    InsurancePlan,
    InsurancePlanVersion,
    InsuranceTermsVersion,
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
        "coverages": {
            "MEDICAL_EXPENSES": "5000000",
            "DENTAL_TREATMENT": "5000",
        },
    },
    {
        "plan": "Dominant",
        "territory": "EUROPE",
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
        "coverages": {
            "MEDICAL_EXPENSES": "5000000",
            "DENTAL_TREATMENT": "10000",
        },
    },
    {
        "plan": "Dominant",
        "territory": "WORLD",
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
        "territory": "CZECH_REPUBLIC",
        "coverages": {
            "PERMANENT_INJURY": "400000",
            "LIABILITY": "5000000",
            "BAGGAGE": "15000",
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


def _get_or_create_insurance_plan(db: Session, name: str) -> InsurancePlan:
    plan = db.scalar(select(InsurancePlan).where(InsurancePlan.name == name))
    if plan is None:
        plan = InsurancePlan(name=name)
        db.add(plan)
        db.flush()
    return plan


def _get_or_create_terms_version(db: Session, code: str) -> InsuranceTermsVersion:
    terms_version = db.scalar(
        select(InsuranceTermsVersion).where(InsuranceTermsVersion.code == code)
    )
    if terms_version is None:
        terms_version = InsuranceTermsVersion(
            code=code,
            valid_from=date(2021, 4, 1),
            valid_to=None,
        )
        db.add(terms_version)
        db.flush()
    return terms_version


def _get_or_create_plan_version(
    db: Session, plan: InsurancePlan
) -> InsurancePlanVersion:
    plan_version = db.scalar(
        select(InsurancePlanVersion).where(
            InsurancePlanVersion.plan_id == plan.id,
            InsurancePlanVersion.version == 1,
        )
    )
    if plan_version is None:
        plan_version = InsurancePlanVersion(
            plan_id=plan.id,
            version=1,
            available_from=date(2026, 1, 1),
            available_to=None,
        )
        db.add(plan_version)
        db.flush()
    return plan_version


def _get_or_create_variant(
    db: Session,
    plan_version: InsurancePlanVersion,
    territory: str,
) -> PlanVariant:
    variant = db.scalar(
        select(PlanVariant).where(
            PlanVariant.plan_version_id == plan_version.id,
            PlanVariant.territory == territory,
        )
    )
    if variant is None:
        variant = PlanVariant(
            plan_version_id=plan_version.id,
            territory=territory,
        )
        db.add(variant)
        db.flush()
    return variant


def _seed_product_catalogue(
    db: Session,
) -> tuple[dict[tuple[str, str], PlanVariant], InsuranceTermsVersion]:
    coverage_types = _seed_coverage_types(db)
    terms_version = _get_or_create_terms_version(db, "VPP_CP_2021")
    variants: dict[tuple[str, str], PlanVariant] = {}

    for definition in PLAN_VARIANTS:
        plan_name = str(definition["plan"])
        territory = str(definition["territory"])

        insurance_plan = _get_or_create_insurance_plan(db, plan_name)
        plan_version = _get_or_create_plan_version(db, insurance_plan)
        variant = _get_or_create_variant(db, plan_version, territory)
        variants[(plan_name, territory)] = variant

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
                db.add(
                    VariantCoverage(
                        plan_variant_id=variant.id,
                        coverage_type_id=coverage_type.id,
                        limit_amount=Decimal(amount),
                        currency="CZK",
                    )
                )

    db.flush()
    return variants, terms_version


def _seed_demo_policy(
    db: Session,
    variants: dict[tuple[str, str], PlanVariant],
    terms_version: InsuranceTermsVersion,
) -> None:
    email = "demo@example.com"
    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        user = User(email=email)
        db.add(user)
        db.flush()

    variant = variants[("Dominant", "EUROPE")]
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
            terms_version_id=terms_version.id,
            trip_purpose="VACATION",
            declared_sport_category="RECREATIONAL",
            start_date=date(2026, 8, 26),
            end_date=date(2026, 9, 5),
            status="ISSUED",
            price_paid=Decimal("45.00"),
            currency="CZK",
        )
        db.add(policy)
        db.flush()
    else:
        policy.policy_number = "POL-2026-000001"
        policy.terms_version_id = terms_version.id
        policy.trip_purpose = "VACATION"
        policy.declared_sport_category = "RECREATIONAL"
        policy.status = "ISSUED"
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
    variants, terms_version = _seed_product_catalogue(db)
    _seed_demo_policy(db, variants, terms_version)


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
