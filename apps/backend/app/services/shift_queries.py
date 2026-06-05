from dataclasses import dataclass
from datetime import date, time, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ShiftDemand, ShiftTemplate


@dataclass(frozen=True)
class ShiftDemandListItem:
    id: str
    demand_date: date
    shift_template_id: str
    shift_template_name: str
    shift_start_time: time
    shift_end_time: time
    required_employee_count: int
    notes: str | None


async def list_shift_templates(session: AsyncSession) -> list[ShiftTemplate]:
    result = await session.execute(
        select(ShiftTemplate).order_by(
            ShiftTemplate.start_time,
            ShiftTemplate.name,
        )
    )
    return list(result.scalars().all())


async def list_week_shift_demand(
    session: AsyncSession,
    week_start: date,
) -> list[ShiftDemandListItem]:
    week_end = week_start + timedelta(days=5)

    result = await session.execute(
        select(ShiftDemand, ShiftTemplate)
        .join(ShiftTemplate, ShiftDemand.shift_template_id == ShiftTemplate.id)
        .where(
            ShiftDemand.demand_date >= week_start,
            ShiftDemand.demand_date <= week_end,
        )
        .order_by(
            ShiftDemand.demand_date,
            ShiftTemplate.start_time,
            ShiftTemplate.name,
        )
    )

    rows = result.all()
    return [_build_shift_demand_item(demand, template) for demand, template in rows]


def _build_shift_demand_item(
    demand: ShiftDemand,
    template: ShiftTemplate,
) -> ShiftDemandListItem:
    return ShiftDemandListItem(
        id=demand.id,
        demand_date=demand.demand_date,
        shift_template_id=template.id,
        shift_template_name=template.name,
        shift_start_time=template.start_time,
        shift_end_time=template.end_time,
        required_employee_count=demand.required_employee_count,
        notes=demand.notes,
    )
