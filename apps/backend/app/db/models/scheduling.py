from sqlalchemy import Column, Date, DateTime, ForeignKey, Index, String

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.db.enums import SchedulingRunStatus, sql_enum


class SchedulingRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "scheduling_runs"

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(
        sql_enum(SchedulingRunStatus),
        default=SchedulingRunStatus.PENDING,
        nullable=False,
    )


class ScheduledShift(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "scheduled_shifts"
    __table_args__ = (
        Index("ix_scheduled_shifts_run_date", "scheduling_run_id", "shift_date"),
        Index("ix_scheduled_shifts_employee_date", "employee_id", "shift_date"),
    )

    scheduling_run_id = Column(String(36), ForeignKey("scheduling_runs.id"), nullable=False)
    employee_id = Column(String(36), ForeignKey("employees.id"), nullable=False)
    shift_template_id = Column(String(36), ForeignKey("shift_templates.id"), nullable=False)
    shift_date = Column(Date, nullable=False)
    start_datetime = Column(DateTime(timezone=True), nullable=False)
    end_datetime = Column(DateTime(timezone=True), nullable=False)
