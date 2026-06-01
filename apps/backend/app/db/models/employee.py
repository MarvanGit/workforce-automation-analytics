from sqlalchemy import Boolean, Column, Integer, String

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Employee(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "employees"

    employee_code = Column(String(64), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True)
    active = Column(Boolean, default=True, nullable=False)
    employment_type = Column(String(64))
    weekly_hours_target = Column(Integer)
    max_weekly_hours = Column(Integer)
