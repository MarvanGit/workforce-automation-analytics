from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db
from app.integrations.google_sheets import GoogleSheetsConfigError, read_sheet_values
from app.schemas.google_sheets import (
    AvailabilityImportResponse,
    AvailabilityPreviewResponse,
    build_availability_error_details,
    build_availability_preview_response,
)
from app.services.availability_import import parse_availability_sheet
from app.services.availability_storage import save_availability_preview

router = APIRouter(prefix="/google-sheets", tags=["google sheets"])
DB_SESSION = Depends(get_db)


@router.get("/availability/preview", response_model=AvailabilityPreviewResponse)
def preview_google_sheet_availability(week_start: date) -> AvailabilityPreviewResponse:
    _validate_week_start(week_start)

    values = _read_configured_sheet_values()
    preview = parse_availability_sheet(values, week_start=week_start)
    return build_availability_preview_response(preview)


@router.post("/availability/import", response_model=AvailabilityImportResponse)
async def import_google_sheet_availability(
    week_start: date,
    db: AsyncSession = DB_SESSION,
) -> AvailabilityImportResponse:
    _validate_week_start(week_start)

    values = _read_configured_sheet_values()
    preview = parse_availability_sheet(values, week_start=week_start)

    if preview.errors:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Sheet has validation errors.",
                "errors": build_availability_error_details(preview),
            },
        )

    result = await save_availability_preview(db, preview, week_start)
    return AvailabilityImportResponse(
        imported_employee_count=result.employee_count,
        imported_availability_count=result.availability_count,
    )


def _validate_week_start(week_start: date) -> None:
    if week_start.weekday() != 0:
        raise HTTPException(status_code=400, detail="week_start must be a Monday.")


def _read_configured_sheet_values() -> list[list[str]]:
    settings = get_settings()

    try:
        return read_sheet_values(
            spreadsheet_id=settings.google_sheets_spreadsheet_id,
            sheet_range=settings.google_sheets_availability_range,
            credentials_path=settings.google_application_credentials,
        )
    except GoogleSheetsConfigError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
