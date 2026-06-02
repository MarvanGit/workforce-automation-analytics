from pydantic import BaseModel

from app.db.models import Employee


class EmployeeResponse(BaseModel):
    id: str
    employee_code: str
    full_name: str
    active: bool
    employment_type: str | None
    weekly_hours_target: int | None
    max_weekly_hours: int | None


class EmployeesResponse(BaseModel):
    rows: list[EmployeeResponse]
    row_count: int


def build_employees_response(employees: list[Employee]) -> EmployeesResponse:
    return EmployeesResponse(
        rows=[
            EmployeeResponse.model_validate(employee, from_attributes=True)
            for employee in employees
        ],
        row_count=len(employees),
    )
