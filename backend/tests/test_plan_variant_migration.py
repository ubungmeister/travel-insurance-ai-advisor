import importlib.util
from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import Connection, create_engine, text


_migration_path = (
    Path(__file__).resolve().parents[1]
    / "alembic"
    / "versions"
    / "e91a6c4b7d20_pin_policy_terms_and_versioned_benefits.py"
)
_spec = importlib.util.spec_from_file_location("plan_variant_migration", _migration_path)
assert _spec is not None and _spec.loader is not None
migration = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(migration)


@pytest.fixture
def legacy_connection() -> Iterator[Connection]:
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "CREATE TABLE plan_variants (id INTEGER, sport_category TEXT)"
        )
        connection.exec_driver_sql(
            "CREATE TABLE variant_coverages (plan_variant_id INTEGER, "
            "coverage_type_id INTEGER, limit_amount NUMERIC, currency TEXT)"
        )
        connection.exec_driver_sql(
            "CREATE TABLE policies (id INTEGER, plan_variant_id INTEGER)"
        )
        connection.exec_driver_sql(
            "CREATE TABLE plan_variant_merge_map (old_id INTEGER, keep_id INTEGER)"
        )
        connection.exec_driver_sql(
            "INSERT INTO plan_variants VALUES "
            "(1, 'RECREATIONAL'), (2, 'WINTER'), (3, 'RISKY')"
        )
        connection.exec_driver_sql(
            "INSERT INTO plan_variant_merge_map VALUES (1, 1), (2, 1), (3, 1)"
        )
        yield connection
    engine.dispose()


@pytest.mark.parametrize(
    ("coverages", "policy_variants", "affected_ids"),
    [
        ([(1, 1, 5000000, "CZK"), (2, 1, 5000000, "CZK")], [1, 2], []),
        ([(1, 1, 5000000, "CZK"), (2, 1, 15000000, "CZK")], [1, 2], [2]),
        ([(1, 1, 5000, "CZK"), (2, 1, 5000, "EUR")], [2], [1]),
        (
            [(1, 1, 5000, "CZK"), (1, 2, 1000, "CZK"), (2, 1, 5000, "CZK")],
            [2],
            [1],
        ),
        (
            [(1, 1, 5000, "CZK"), (2, 1, 5000, "CZK"), (2, 2, 1000, "CZK")],
            [1, 2],
            [1],
        ),
        ([(1, 1, 5000000, "CZK"), (2, 1, 15000000, "CZK")], [1], []),
        ([(2, 1, 5000, "CZK"), (3, 1, 10000, "CZK")], [2, 3], [2]),
        ([], [1, 2], []),
    ],
    ids=[
        "identical-schedules",
        "different-amount",
        "different-currency",
        "coverage-added-to-moved-policy",
        "coverage-added-to-retained-policy",
        "unreferenced-different-schedule",
        "missing-coverage-uses-winter-before-risky",
        "empty-schedules",
    ],
)
def test_consolidation_identifies_changed_policy_benefits(
    legacy_connection: Connection,
    coverages: list[tuple[int, int, int, str]],
    policy_variants: list[int],
    affected_ids: list[int],
) -> None:
    if coverages:
        legacy_connection.exec_driver_sql(
            "INSERT INTO variant_coverages VALUES (?, ?, ?, ?)", coverages
        )
    legacy_connection.exec_driver_sql(
        "INSERT INTO policies VALUES (?, ?)",
        list(enumerate(policy_variants, start=1)),
    )
    legacy_connection.exec_driver_sql(
        "CREATE TEMPORARY TABLE plan_variant_merged_coverages AS "
        + migration._MERGED_COVERAGES_QUERY
    )

    result = legacy_connection.execute(
        text(migration._CHANGED_POLICY_BENEFITS_QUERY + " ORDER BY p.id")
    )

    assert list(result.scalars()) == affected_ids
