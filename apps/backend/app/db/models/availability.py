from sqlalchemy import Column, Date, ForeignKey, Index, String, Time, UniqueConstraint

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.db.enums import AvailabilityType, sql_enum


class AvailabilityRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "availability_records"
    __table_args__ = (
        UniqueConstraint(
            "employee_id",
            "work_date",
            "start_time",
            "end_time",
            name="uq_availability_records_employee_window",
        ),
        Index("ix_availability_records_employee_date", "employee_id", "work_date"),
    )

    employee_id = Column(String(36), ForeignKey("employees.id"), nullable=False)
    work_date = Column(Date, nullable=False)
    start_time = Column(Time)
    end_time = Column(Time)
    availability_type = Column(
        sql_enum(AvailabilityType),
        default=AvailabilityType.AVAILABLE,
        nullable=False,
    )
    notes = Column(String(500))
