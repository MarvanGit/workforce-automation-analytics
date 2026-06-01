from datetime import date

from fastapi import APIRouter, HTTPException

from app.core.config import get_settings
from app.integrations.google_sheets import GoogleSheetsConfigError, read_sheet_values
from app.schemas.google_sheets import (
    AvailabilityPreviewResponse,
    build_availability_preview_response,
)
from app.services.availability_import import parse_availability_sheet

router = APIRouter(prefix="/google-sheets", tags=["google sheets"])


@router.get("/availability/preview", response_model=AvailabilityPreviewResponse)
def preview_google_sheet_availability(week_start: date) -> AvailabilityPreviewResponse:
    if week_start.weekday() != 0:
        raise HTTPException(status_code=400, detail="week_start must be a Monday.")

    settings = get_settings()

    try:
        values = read_sheet_values(
            spreadsheet_id=settings.google_sheets_spreadsheet_id,
            sheet_range=settings.google_sheets_availability_range,
            credentials_path=settings.google_application_credentials,
        )
    except GoogleSheetsConfigError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    preview = parse_availability_sheet(values, week_start=week_start)
    return build_availability_preview_response(preview)
