param(
    [string]$BaseUrl = "http://localhost:8000/api/v1",
    [string]$WeekStart = "2026-06-08",
    [string]$ShiftStart = "09:00",
    [string]$ShiftEnd = "17:00",
    [int]$RequiredEmployeeCount = 1,
    [string]$ShiftName = "",
    [switch]$SkipImport
)

$ErrorActionPreference = "Stop"

function Show-Step {
    param([string]$Text)

    Write-Host ""
    Write-Host "== $Text =="
}

function Invoke-ApiJson {
    param(
        [string]$Method,
        [string]$Uri,
        [object]$Body = $null
    )

    if ($null -eq $Body) {
        return Invoke-RestMethod -Method $Method -Uri $Uri
    }

    $JsonBody = $Body | ConvertTo-Json -Depth 10
    return Invoke-RestMethod -Method $Method -Uri $Uri -ContentType "application/json" -Body $JsonBody
}

function Test-ApiRoute {
    param(
        [string]$Path,
        [string]$Method
    )

    $ApiRoot = $BaseUrl.TrimEnd("/") -replace "/api/v1$", ""
    $OpenApi = Invoke-ApiJson -Method "Get" -Uri "$ApiRoot/openapi.json"
    $Route = $OpenApi.paths.PSObject.Properties[$Path].Value
    $RouteMethod = $Route.PSObject.Properties[$Method.ToLower()].Value

    if ($null -eq $Route -or $null -eq $RouteMethod) {
        Write-Host ""
        Write-Host "Missing API route: $($Method.ToUpper()) $Path"
        Write-Host "The Docker backend is probably running an older image."
        Write-Host ""
        Write-Host "Rebuild and restart it from the project root:"
        Write-Host "docker compose --env-file .env -f infra/docker-compose.yml -f infra/docker-compose.google-sheets.yml up -d --build backend"
        Write-Host ""
        Write-Host "Then run this smoke test again."
        exit 1
    }
}

if ([string]::IsNullOrWhiteSpace($ShiftName)) {
    $Timestamp = Get-Date -Format "yyyyMMddHHmmss"
    $ShiftName = "Smoke Shift $Timestamp"
}

Show-Step "Checking backend health"
$Health = Invoke-ApiJson -Method "Get" -Uri "$BaseUrl/health"
$Health | ConvertTo-Json -Depth 10

Show-Step "Checking required scheduling routes"
Test-ApiRoute -Path "/api/v1/shift-templates" -Method "post"
Test-ApiRoute -Path "/api/v1/shift-demand" -Method "post"
Test-ApiRoute -Path "/api/v1/scheduling/preview" -Method "get"
Test-ApiRoute -Path "/api/v1/scheduling/runs" -Method "post"
Write-Host "Required routes are available."

if (-not $SkipImport) {
    Show-Step "Importing availability from Google Sheets"
    $ImportResult = Invoke-ApiJson -Method "Post" -Uri "$BaseUrl/google-sheets/availability/import?week_start=$WeekStart"
    $ImportResult | ConvertTo-Json -Depth 10
}

Show-Step "Creating shift template"
$Template = Invoke-ApiJson -Method "Post" -Uri "$BaseUrl/shift-templates" -Body @{
    name       = $ShiftName
    start_time = $ShiftStart
    end_time   = $ShiftEnd
    active     = $true
}
$Template | ConvertTo-Json -Depth 10

Show-Step "Creating shift demand"
$Demand = Invoke-ApiJson -Method "Post" -Uri "$BaseUrl/shift-demand" -Body @{
    demand_date             = $WeekStart
    shift_template_id       = $Template.id
    required_employee_count = $RequiredEmployeeCount
    notes                   = "Created by scheduling workflow smoke test"
}
$Demand | ConvertTo-Json -Depth 10

Show-Step "Previewing schedule"
$Preview = Invoke-ApiJson -Method "Get" -Uri "$BaseUrl/scheduling/preview?week_start=$WeekStart"
$Preview | ConvertTo-Json -Depth 10

Show-Step "Saving schedule run"
$SavedRun = Invoke-ApiJson -Method "Post" -Uri "$BaseUrl/scheduling/runs?week_start=$WeekStart"
$SavedRun | ConvertTo-Json -Depth 10

Show-Step "Reading saved schedule run"
$ReadRun = Invoke-ApiJson -Method "Get" -Uri "$BaseUrl/scheduling/runs/$($SavedRun.id)"
$ReadRun | ConvertTo-Json -Depth 10

Show-Step "Done"
Write-Host "Saved schedule run id: $($SavedRun.id)"
