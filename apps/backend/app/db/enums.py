from enum import StrEnum

from sqlalchemy import Enum as SqlAlchemyEnum


def sql_enum(enum_class: type[StrEnum]) -> SqlAlchemyEnum:
    return SqlAlchemyEnum(
        enum_class,
        values_callable=lambda values: [item.value for item in values],
        name=enum_class.__name__.lower(),
    )


class AvailabilityType(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


class AbsenceType(StrEnum):
    VACATION = "vacation"
    SICK_LEAVE = "sick_leave"
    TRAINING = "training"
    OTHER = "other"


class SchedulingRunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
