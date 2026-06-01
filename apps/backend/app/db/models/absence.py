from sqlalchemy import Column, Date, ForeignKey, Index, String

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.db.enums import AbsenceType, sql_enum


class Absence(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "absences"
    __table_args__ = (
        Index("ix_absences_employee_period", "employee_id", "start_date", "end_date"),
    )

    employee_id = Column(String(36), ForeignKey("employees.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    absence_type = Column(sql_enum(AbsenceType), nullable=False)
    notes = Column(String(500))
