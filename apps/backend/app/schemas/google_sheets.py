from datetime import date, time

from pydantic import BaseModel

from app.db.enums import AvailabilityType
from app.services.availability_import import AvailabilitySheetPreview


class AvailabilityPreviewRow(BaseModel):
    row_number: int
    employee_code: str
    employee_name: str | None
    weekday: str
    work_date: date
    start_time: time | None
    end_time: time | None
    availability_type: AvailabilityType
    notes: str | None


class AvailabilityPreviewError(BaseModel):
    row_number: int
    field: str
    message: str


class AvailabilityPreviewResponse(BaseModel):
    rows: list[AvailabilityPreviewRow]
    errors: list[AvailabilityPreviewError]
    row_count: int
    error_count: int


class AvailabilityImportResponse(BaseModel):
    imported_employee_count: int
    imported_availability_count: int


def build_availability_preview_response(
    preview: AvailabilitySheetPreview,
) -> AvailabilityPreviewResponse:
    return AvailabilityPreviewResponse(
        rows=[
            AvailabilityPreviewRow.model_validate(row, from_attributes=True)
            for row in preview.rows
        ],
        errors=[
            AvailabilityPreviewError.model_validate(error, from_attributes=True)
            for error in preview.errors
        ],
        row_count=len(preview.rows),
        error_count=len(preview.errors),
    )


def build_availability_error_details(
    preview: AvailabilitySheetPreview,
) -> list[dict[str, int | str]]:
    return [
        AvailabilityPreviewError.model_validate(error, from_attributes=True).model_dump()
        for error in preview.errors
    ]
