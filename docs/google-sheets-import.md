# Google Sheets Import Design

## Source Role

Google Sheets is used for simple availability data entry. Imported rows are validated and stored in PostgreSQL before the scheduler or analytics use them.

## MVP Authentication

Use a Google Cloud service account:

1. Create a service account in Google Cloud.
2. Enable the Google Sheets API.
3. Share the target spreadsheet with the service account email.
4. Provide credentials to the backend through an environment variable or mounted secret.

Do not commit service account JSON files.

## Expected Sheet Columns

```text
employee_code | employee_name | monday | tuesday | wednesday | thursday | friday | saturday
```

The default range is:

```text
Availability!A:H
```

Each employee has one row per week. Each weekday cell should contain either:

```text
12:00 - 20:00
```

or:

```text
N/A
```

`N/A` means the employee is not available that day.

## Import Flow

1. Read configured spreadsheet range.
2. Parse raw rows.
3. Expand each employee row into Monday-Saturday availability rows.
4. Validate employee codes and weekday cell values.
5. Persist valid records.
6. Return a simple summary of imported rows and validation errors.

Persisted import history and detailed validation reporting are deferred until after the basic import, analysis, and weekly scheduling flow works.

## MVP Preview Endpoint

This endpoint reads the configured sheet range and returns parsed rows without writing to the database:

```text
GET /api/v1/google-sheets/availability/preview?week_start=2026-06-08
```

`week_start` must be the Monday date for the displayed sheet week. The backend uses it to convert weekday columns into real dates.

## MVP Import Endpoint

This endpoint reads the same configured sheet range, validates it, and stores the rows in PostgreSQL:

```text
POST /api/v1/google-sheets/availability/import?week_start=2026-06-08
```

If the sheet contains validation errors, the endpoint returns `400` and does not write anything.

When the sheet is valid, the backend:

1. Creates missing employees from `employee_code` and `employee_name`.
2. Updates the employee name when the sheet provides one.
3. Deletes the existing Monday-Saturday availability for those employees.
4. Inserts the newly imported availability records.

This endpoint needs:

```env
GOOGLE_SHEETS_SPREADSHEET_ID=
GOOGLE_SHEETS_AVAILABILITY_RANGE=Availability!A:H
GOOGLE_APPLICATION_CREDENTIALS=
```
