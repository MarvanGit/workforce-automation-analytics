from datetime import date, time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ShiftDemand, ShiftTemplate
from app.services.shift_queries import ShiftDemandListItem


async def create_shift_template(
    session: AsyncSession,
    name: str,
    start_time: time,
    end_time: time,
    active: bool,
) -> ShiftTemplate:
    clean_name = name.strip()

    if clean_name == "":
        raise ValueError("name is required.")

    if start_time == end_time:
        raise ValueError("start_time and end_time must be different.")

    existing_template = await _find_shift_template_by_name(session, clean_name)
    if existing_template is not None:
        raise ValueError("shift template name already exists.")

    template = ShiftTemplate(
        name=clean_name,
        start_time=start_time,
        end_time=end_time,
        duration_minutes=_duration_minutes(start_time, end_time),
        is_overnight=end_time < start_time,
        active=active,
    )

    session.add(template)
    await session.commit()
    await session.refresh(template)
    return template


async def create_shift_demand(
    session: AsyncSession,
    demand_date: date,
    shift_template_id: str,
    required_employee_count: int,
    notes: str | None,
) -> ShiftDemandListItem:
    if required_employee_count <= 0:
        raise ValueError("required_employee_count must be greater than 0.")

    template = await session.get(ShiftTemplate, shift_template_id)
    if template is None:
        raise ValueError("shift_template_id was not found.")

    existing_demand = await _find_shift_demand(
        session,
        demand_date,
        shift_template_id,
    )
    if existing_demand is not None:
        raise ValueError("shift demand already exists for this date and template.")

    demand = ShiftDemand(
        demand_date=demand_date,
        shift_template_id=shift_template_id,
        required_employee_count=required_employee_count,
        notes=notes,
    )

    session.add(demand)
    await session.commit()
    await session.refresh(demand)

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


async def delete_shift_demand(
    session: AsyncSession,
    demand_id: str,
) -> bool:
    demand = await session.get(ShiftDemand, demand_id)

    if demand is None:
        return False

    await session.delete(demand)
    await session.commit()
    return True


async def _find_shift_template_by_name(
    session: AsyncSession,
    name: str,
) -> ShiftTemplate | None:
    result = await session.execute(
        select(ShiftTemplate).where(ShiftTemplate.name == name)
    )
    return result.scalar_one_or_none()


async def _find_shift_demand(
    session: AsyncSession,
    demand_date: date,
    shift_template_id: str,
) -> ShiftDemand | None:
    result = await session.execute(
        select(ShiftDemand).where(
            ShiftDemand.demand_date == demand_date,
            ShiftDemand.shift_template_id == shift_template_id,
        )
    )
    return result.scalar_one_or_none()


def _duration_minutes(start_time: time, end_time: time) -> int:
    start_minutes = (start_time.hour * 60) + start_time.minute
    end_minutes = (end_time.hour * 60) + end_time.minute

    if end_minutes < start_minutes:
        end_minutes += 24 * 60

    return end_minutes - start_minutes
