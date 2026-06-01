"""Create core retail scheduling schema.

Revision ID: 0001_core_retail_schema
Revises:
Create Date: 2026-06-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_core_retail_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    ]


def uuid_primary_key_column() -> sa.Column:
    return sa.Column("id", sa.String(length=36), nullable=False)


def upgrade() -> None:
    op.create_table(
        "employees",
        uuid_primary_key_column(),
        sa.Column("employee_code", sa.String(length=64), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("employment_type", sa.String(length=64), nullable=True),
        sa.Column("weekly_hours_target", sa.Integer(), nullable=True),
        sa.Column("max_weekly_hours", sa.Integer(), nullable=True),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_employees")),
        sa.UniqueConstraint("email", name=op.f("uq_employees_email")),
    )
    op.create_index(
        op.f("ix_employees_employee_code"),
        "employees",
        ["employee_code"],
        unique=True,
    )

    op.create_table(
        "scheduling_runs",
        uuid_primary_key_column(),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "running",
                "completed",
                "failed",
                name="schedulingrunstatus",
            ),
            nullable=False,
        ),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_scheduling_runs")),
    )

    op.create_table(
        "shift_templates",
        uuid_primary_key_column(),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("is_overnight", sa.Boolean(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_shift_templates")),
        sa.UniqueConstraint("name", name=op.f("uq_shift_templates_name")),
    )

    op.create_table(
        "absences",
        uuid_primary_key_column(),
        sa.Column("employee_id", sa.String(length=36), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column(
            "absence_type",
            sa.Enum("vacation", "sick_leave", "training", "other", name="absencetype"),
            nullable=False,
        ),
        sa.Column("notes", sa.String(length=500), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(
            ["employee_id"],
            ["employees.id"],
            name=op.f("fk_absences_employee_id_employees"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_absences")),
    )
    op.create_index(
        "ix_absences_employee_period",
        "absences",
        ["employee_id", "start_date", "end_date"],
        unique=False,
    )

    op.create_table(
        "scheduled_shifts",
        uuid_primary_key_column(),
        sa.Column("scheduling_run_id", sa.String(length=36), nullable=False),
        sa.Column("employee_id", sa.String(length=36), nullable=False),
        sa.Column("shift_template_id", sa.String(length=36), nullable=False),
        sa.Column("shift_date", sa.Date(), nullable=False),
        sa.Column("start_datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_datetime", sa.DateTime(timezone=True), nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(
            ["employee_id"],
            ["employees.id"],
            name=op.f("fk_scheduled_shifts_employee_id_employees"),
        ),
        sa.ForeignKeyConstraint(
            ["scheduling_run_id"],
            ["scheduling_runs.id"],
            name=op.f("fk_scheduled_shifts_scheduling_run_id_scheduling_runs"),
        ),
        sa.ForeignKeyConstraint(
            ["shift_template_id"],
            ["shift_templates.id"],
            name=op.f("fk_scheduled_shifts_shift_template_id_shift_templates"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_scheduled_shifts")),
    )
    op.create_index(
        "ix_scheduled_shifts_employee_date",
        "scheduled_shifts",
        ["employee_id", "shift_date"],
        unique=False,
    )
    op.create_index(
        "ix_scheduled_shifts_run_date",
        "scheduled_shifts",
        ["scheduling_run_id", "shift_date"],
        unique=False,
    )

    op.create_table(
        "shift_demand",
        uuid_primary_key_column(),
        sa.Column("demand_date", sa.Date(), nullable=False),
        sa.Column("shift_template_id", sa.String(length=36), nullable=False),
        sa.Column("required_employee_count", sa.Integer(), nullable=False),
        sa.Column("notes", sa.String(length=500), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(
            ["shift_template_id"],
            ["shift_templates.id"],
            name=op.f("fk_shift_demand_shift_template_id_shift_templates"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_shift_demand")),
        sa.UniqueConstraint(
            "demand_date",
            "shift_template_id",
            name="uq_shift_demand_date_template",
        ),
    )
    op.create_index("ix_shift_demand_date", "shift_demand", ["demand_date"], unique=False)

    op.create_table(
        "availability_records",
        uuid_primary_key_column(),
        sa.Column("employee_id", sa.String(length=36), nullable=False),
        sa.Column("work_date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=True),
        sa.Column("end_time", sa.Time(), nullable=True),
        sa.Column(
            "availability_type",
            sa.Enum("available", "unavailable", name="availabilitytype"),
            nullable=False,
        ),
        sa.Column("notes", sa.String(length=500), nullable=True),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(
            ["employee_id"],
            ["employees.id"],
            name=op.f("fk_availability_records_employee_id_employees"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_availability_records")),
        sa.UniqueConstraint(
            "employee_id",
            "work_date",
            "start_time",
            "end_time",
            name="uq_availability_records_employee_window",
        ),
    )
    op.create_index(
        "ix_availability_records_employee_date",
        "availability_records",
        ["employee_id", "work_date"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_availability_records_employee_date", table_name="availability_records")
    op.drop_table("availability_records")
    op.drop_index("ix_shift_demand_date", table_name="shift_demand")
    op.drop_table("shift_demand")
    op.drop_index("ix_scheduled_shifts_run_date", table_name="scheduled_shifts")
    op.drop_index("ix_scheduled_shifts_employee_date", table_name="scheduled_shifts")
    op.drop_table("scheduled_shifts")
    op.drop_index("ix_absences_employee_period", table_name="absences")
    op.drop_table("absences")
    op.drop_table("shift_templates")
    op.drop_table("scheduling_runs")
    op.drop_index(op.f("ix_employees_employee_code"), table_name="employees")
    op.drop_table("employees")

    sa.Enum("available", "unavailable", name="availabilitytype").drop(op.get_bind())
    sa.Enum("vacation", "sick_leave", "training", "other", name="absencetype").drop(
        op.get_bind()
    )
    sa.Enum(
        "pending",
        "running",
        "completed",
        "failed",
        name="schedulingrunstatus",
    ).drop(op.get_bind())
