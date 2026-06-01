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
employee_code | employee_name | date | start_time | end_time | availability | notes
```

## Import Flow

1. Read configured spreadsheet range.
2. Parse raw rows.
3. Map rows to internal availability input objects.
4. Validate employee codes, dates, time windows, availability values, and duplicates.
5. Persist valid records.
6. Return a simple summary of imported rows and validation errors.

Persisted import history and detailed validation reporting are deferred until after the basic import, analysis, and weekly scheduling flow works.
