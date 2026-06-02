from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.employees import EmployeesResponse, build_employees_response
from app.services.availability_queries import list_employees

router = APIRouter(prefix="/employees", tags=["employees"])
DB_SESSION = Depends(get_db)


@router.get("", response_model=EmployeesResponse)
async def get_employees(db: AsyncSession = DB_SESSION) -> EmployeesResponse:
    employees = await list_employees(db)
    return build_employees_response(employees)
