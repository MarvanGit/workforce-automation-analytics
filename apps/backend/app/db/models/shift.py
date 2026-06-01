from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Index,
    Integer,
    String,
    Time,
    UniqueConstraint,
)

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ShiftTemplate(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "shift_templates"

    name = Column(String(100), unique=True, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    is_overnight = Column(Boolean, default=False, nullable=False)
    active = Column(Boolean, default=True, nullable=False)


class ShiftDemand(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "shift_demand"
    __table_args__ = (
        UniqueConstraint(
            "demand_date",
            "shift_template_id",
            name="uq_shift_demand_date_template",
        ),
        Index("ix_shift_demand_date", "demand_date"),
    )

    demand_date = Column(Date, nullable=False)
    shift_template_id = Column(String(36), ForeignKey("shift_templates.id"), nullable=False)
    required_employee_count = Column(Integer, nullable=False)
    notes = Column(String(500))
