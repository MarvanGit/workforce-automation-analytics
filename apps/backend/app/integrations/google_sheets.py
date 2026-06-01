from typing import Any

from google.oauth2 import service_account
from googleapiclient.discovery import build

SHEETS_READONLY_SCOPE = "https://www.googleapis.com/auth/spreadsheets.readonly"


class GoogleSheetsConfigError(ValueError):
    pass


def build_sheets_service(credentials_path: str) -> Any:
    if not credentials_path:
        raise GoogleSheetsConfigError("GOOGLE_APPLICATION_CREDENTIALS must be configured.")

    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=[SHEETS_READONLY_SCOPE],
    )
    return build("sheets", "v4", credentials=credentials, cache_discovery=False)


def read_sheet_values(
    spreadsheet_id: str,
    sheet_range: str,
    credentials_path: str,
    service: Any | None = None,
) -> list[list[str]]:
    if not spreadsheet_id:
        raise GoogleSheetsConfigError("GOOGLE_SHEETS_SPREADSHEET_ID must be configured.")
    if not sheet_range:
        raise GoogleSheetsConfigError("GOOGLE_SHEETS_AVAILABILITY_RANGE must be configured.")

    sheets_service = service or build_sheets_service(credentials_path)
    result = (
        sheets_service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=sheet_range)
        .execute()
    )
    return result.get("values", [])
