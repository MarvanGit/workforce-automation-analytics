from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import configure_mappers

from app.db.enums import AbsenceType, AvailabilityType, SchedulingRunStatus
from app.db.models import Base


def test_metadata_contains_core_retail_planning_tables() -> None:
    assert set(Base.metadata.tables) == {
        "absences",
        "availability_records",
        "employees",
        "scheduled_shifts",
        "scheduling_runs",
        "shift_demand",
        "shift_templates",
    }


def test_core_foreign_keys_are_declared() -> None:
    availability = Base.metadata.tables["availability_records"]
    absences = Base.metadata.tables["absences"]
    scheduled_shifts = Base.metadata.tables["scheduled_shifts"]
    shift_demand = Base.metadata.tables["shift_demand"]

    assert {fk.target_fullname for fk in availability.c.employee_id.foreign_keys} == {
        "employees.id"
    }
    assert {fk.target_fullname for fk in absences.c.employee_id.foreign_keys} == {"employees.id"}
    assert {fk.target_fullname for fk in scheduled_shifts.c.scheduling_run_id.foreign_keys} == {
        "scheduling_runs.id"
    }
    assert {fk.target_fullname for fk in scheduled_shifts.c.employee_id.foreign_keys} == {
        "employees.id"
    }
    assert {fk.target_fullname for fk in shift_demand.c.shift_template_id.foreign_keys} == {
        "shift_templates.id"
    }


def test_retail_domain_enums_use_stable_values() -> None:
    assert AvailabilityType.AVAILABLE == "available"
    assert AbsenceType.VACATION == "vacation"
    assert SchedulingRunStatus.PENDING == "pending"
    assert Base.metadata.tables["availability_records"].c.availability_type.type.enums == [
        "available",
        "unavailable",
    ]


def test_schema_keeps_mvp_employee_fields_simple() -> None:
    employee_columns = set(Base.metadata.tables["employees"].columns.keys())

    assert employee_columns == {
        "id",
        "employee_code",
        "full_name",
        "email",
        "active",
        "employment_type",
        "weekly_hours_target",
        "max_weekly_hours",
        "created_at",
        "updated_at",
    }


def test_mappers_configure_and_schema_can_be_created() -> None:
    configure_mappers()
    engine = create_engine("sqlite+pysqlite:///:memory:")

    Base.metadata.create_all(engine)

    assert set(Base.metadata.tables).issubset(set(inspect(engine).get_table_names()))
