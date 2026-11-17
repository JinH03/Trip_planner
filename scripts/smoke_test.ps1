
$ErrorActionPreference = "Stop"

Write-Host "=== TripCS Docker Smoke Test ==="

# 1. Docker Compose 설정 검증
Write-Host "[1/4] Checking Compose configuration..."

docker compose config --quiet

if ($LASTEXITCODE -ne 0) {
    throw "Docker Compose configuration failed"
}

# 2. 서비스 시작
Write-Host "[2/4] Starting Docker services..."

docker compose up -d --build

if ($LASTEXITCODE -ne 0) {
    throw "Docker Compose startup failed"
}

# 3. 컨테이너 상태 검사
Write-Host "[3/4] Waiting for healthy containers..."

$services = @("db", "redis", "api")
$maxAttempts = 30
$allHealthy = $false

for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
    $allHealthy = $true

    foreach ($service in $services) {
        $containerId = (
            docker compose ps -q $service
        ).Trim()

        if (-not $containerId) {
            Write-Host "$service : not running"
            $allHealthy = $false
            continue
        }

        $health = (
            docker inspect `
                --format '{{.State.Health.Status}}' `
                $containerId
        ).Trim()

        Write-Host "$service : $health"

        if ($health -ne "healthy") {
            $allHealthy = $false
        }
    }

    if ($allHealthy) {
        break
    }

    Write-Host "Waiting for services..."
    Start-Sleep -Seconds 3
}

if (-not $allHealthy) {
    docker compose ps -a
    throw "Some Docker services are not healthy"
}

# Check migration container exit code
Write-Host "Checking Alembic migration result..."

$migrateContainerId = [string](
    docker compose ps -a -q migrate
)

$migrateContainerId = $migrateContainerId.Trim()

if (-not $migrateContainerId) {
    throw "Migration container not found"
}

$migrateStatus = (
    docker inspect `
        --format '{{.State.Status}}' `
        $migrateContainerId
).Trim()

$migrateExitCode = (
    docker inspect `
        --format '{{.State.ExitCode}}' `
        $migrateContainerId
).Trim()

Write-Host "migrate : $migrateStatus (exit $migrateExitCode)"

if (
    $migrateStatus -ne "exited" -or
    $migrateExitCode -ne "0"
) {
    throw "Alembic migration failed"
}

# 4. HTTP Health Check
Write-Host "[4/4] Checking API endpoints..."

$baseUrl = "http://127.0.0.1:8000"

$live = Invoke-RestMethod `
    -Uri "$baseUrl/health/live" `
    -TimeoutSec 5

if ($live.status -ne "ok") {
    throw "Liveness check failed"
}

$ready = Invoke-RestMethod `
    -Uri "$baseUrl/health/ready" `
    -TimeoutSec 5

if (
    $ready.status -ne "ok" -or
    $ready.services.database -ne "up" -or
    $ready.services.redis -ne "up"
) {
    throw "Readiness check failed"
}

Write-Host ""
Write-Host "=================================="
Write-Host "TripCS Smoke Test PASSED!"
Write-Host "=================================="
