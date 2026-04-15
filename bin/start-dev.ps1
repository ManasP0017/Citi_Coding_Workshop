# ============================================================
# Coding Workshop - Local Development Setup (Windows/PowerShell)
# ============================================================
# Usage: .\bin\start-dev.ps1
#
# Prerequisites:
#   - Docker Desktop installed and running
#   - Terraform >= 1.11 installed
#   - Python 3.11+ with pip
#   - Node.js + npm
# ============================================================

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$InfraDir = Join-Path $ProjectRoot "infra"
$FrontendDir = Join-Path $ProjectRoot "frontend"
$BackendDir = Join-Path $ProjectRoot "backend"

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " Coding Workshop - Local Dev Setup (Windows)" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

# ── Step 1: Verify prerequisites ──────────────────────────────────
Write-Host "[1/7] Checking prerequisites..." -ForegroundColor Yellow

# Docker
try { docker info 2>$null | Out-Null }
catch {
    Write-Host "  ERROR: Docker is not running. Start Docker Desktop first." -ForegroundColor Red
    exit 1
}
Write-Host "  OK Docker is running" -ForegroundColor Green

# Terraform
try { terraform --version 2>$null | Out-Null }
catch {
    Write-Host "  ERROR: Terraform not found. Install from https://terraform.io" -ForegroundColor Red
    exit 1
}
Write-Host "  OK Terraform installed" -ForegroundColor Green

# Python
try { python --version 2>$null | Out-Null }
catch {
    Write-Host "  ERROR: Python not found." -ForegroundColor Red
    exit 1
}
Write-Host "  OK Python installed" -ForegroundColor Green

# Node.js
try { node --version 2>$null | Out-Null }
catch {
    Write-Host "  ERROR: Node.js not found." -ForegroundColor Red
    exit 1
}
Write-Host "  OK Node.js installed" -ForegroundColor Green
Write-Host ""

# ── Step 2: Start PostgreSQL + LocalStack via Docker Compose ──────
Write-Host "[2/7] Starting PostgreSQL + LocalStack (Docker Compose)..." -ForegroundColor Yellow

Set-Location $ProjectRoot
docker compose up -d

# Wait for PostgreSQL to be healthy
Write-Host "  Waiting for PostgreSQL..." -NoNewline
for ($i = 0; $i -lt 30; $i++) {
    $pgReady = docker exec workshop-postgres pg_isready -U postgres 2>$null
    if ($LASTEXITCODE -eq 0) { break }
    Start-Sleep -Seconds 1
    Write-Host "." -NoNewline
}
Write-Host ""
Write-Host "  OK PostgreSQL is ready" -ForegroundColor Green

# Wait for LocalStack to be healthy
Write-Host "  Waiting for LocalStack..." -NoNewline
for ($i = 0; $i -lt 60; $i++) {
    try {
        $health = Invoke-RestMethod -Uri "http://localhost:4566/_localstack/health" -ErrorAction SilentlyContinue
        if ($health) { break }
    } catch {}
    Start-Sleep -Seconds 1
    Write-Host "." -NoNewline
}
Write-Host ""
Write-Host "  OK LocalStack is ready" -ForegroundColor Green
Write-Host ""

# ── Step 3: Install pip dependencies into each Lambda service ─────
Write-Host "[3/7] Installing Lambda service dependencies..." -ForegroundColor Yellow

$services = Get-ChildItem -Path $BackendDir -Directory |
    Where-Object { $_.Name -notlike "_*" -and $_.Name -notlike ".*" -and $_.Name -ne "app" -and $_.Name -ne "alembic" -and $_.Name -ne "db-init" } |
    Where-Object { Test-Path (Join-Path $_.FullName "requirements.txt") }

foreach ($svc in $services) {
    $reqFile = Join-Path $svc.FullName "requirements.txt"
    Write-Host "  Installing deps for $($svc.Name)..."
    pip install --quiet --target $svc.FullName -r $reqFile 2>$null
}
Write-Host "  OK All Lambda deps installed" -ForegroundColor Green
Write-Host ""

# ── Step 4: Deploy backend via Terraform ──────────────────────────
Write-Host "[4/7] Deploying backend with Terraform..." -ForegroundColor Yellow

$env:AWS_ENDPOINT_URL = "http://localhost:4566"
$env:AWS_ENDPOINT_URL_S3 = "http://s3.localhost.localstack.cloud:4566"
$env:AWS_ACCESS_KEY_ID = "test"
$env:AWS_SECRET_ACCESS_KEY = "test"
$env:AWS_REGION = "us-east-1"
$env:AWS_SESSION_TOKEN = $null

# PostgreSQL host — Docker containers reach the Windows host via host.docker.internal
$env:TF_VAR_aws_postgres_host = "host.docker.internal"

# Create tfstate bucket in LocalStack S3
try {
    aws s3 mb "s3://coding-workshop-tfstate-abcd1234" --region us-east-1 2>$null | Out-Null
} catch {}

Set-Location $InfraDir

Write-Host "  Running terraform init..."
terraform init -reconfigure `
    -backend-config="bucket=coding-workshop-tfstate-abcd1234" `
    -backend-config="region=us-east-1" 2>$null | Out-Null

Write-Host "  Running terraform apply..."
terraform apply -auto-approve

# Capture Lambda URLs
$lambdaUrls = terraform output -json lambda_urls 2>$null | ConvertFrom-Json
$apiEndpoints = terraform output -json api_endpoints 2>$null | ConvertFrom-Json

Write-Host "  OK Backend deployed!" -ForegroundColor Green
Write-Host ""

# Display Lambda URLs
Write-Host "  Lambda Function URLs:" -ForegroundColor Cyan
if ($lambdaUrls) {
    $lambdaUrls.PSObject.Properties | ForEach-Object {
        Write-Host "    $($_.Name): $($_.Value)"
    }
}
Write-Host ""

# ── Step 5: Generate frontend .env.local ──────────────────────────
Write-Host "[5/7] Generating frontend environment..." -ForegroundColor Yellow

$envContent = @"
# Auto-generated environment file
# Generated on: $(Get-Date)
# Environment: local (LocalStack)
VITE_API_BASE_URL=http://localhost:3001
VITE_API_URL=http://localhost:3001
"@

# Add endpoint mappings
if ($apiEndpoints) {
    $endpointsJson = $apiEndpoints | ConvertTo-Json -Compress
    $envContent += "`nVITE_API_ENDPOINTS='$endpointsJson'"
    $envContent += "`nREACT_APP_API_ENDPOINTS='$endpointsJson'"
}

if ($lambdaUrls) {
    $lambdaJson = $lambdaUrls | ConvertTo-Json -Compress
    $envContent += "`nVITE_LAMBDA_URLS='$lambdaJson'"
    $envContent += "`nREACT_APP_LAMBDA_URLS='$lambdaJson'"
}

$envFile = Join-Path $FrontendDir ".env.local"
$envContent | Out-File -FilePath $envFile -Encoding UTF8 -Force
Write-Host "  OK Created $envFile" -ForegroundColor Green
Write-Host ""

# ── Step 6: Install frontend deps + start proxy ──────────────────
Write-Host "[6/7] Setting up frontend + proxy..." -ForegroundColor Yellow

Set-Location $FrontendDir
if (-not (Test-Path "node_modules")) {
    Write-Host "  Installing frontend npm dependencies..."
    npm install
}
Write-Host "  OK Frontend dependencies ready" -ForegroundColor Green

# Start proxy server in background
Write-Host "  Starting CORS proxy on port 3001..."
$proxyScript = Join-Path $ProjectRoot "bin" "proxy-server.js"
$proxyProcess = Start-Process -FilePath "node" -ArgumentList $proxyScript -PassThru -WindowStyle Hidden
Write-Host "  OK Proxy started (PID: $($proxyProcess.Id))" -ForegroundColor Green
Write-Host ""

# ── Step 7: Summary ──────────────────────────────────────────────
Write-Host "====================================================" -ForegroundColor Green
Write-Host " All services are running!" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  PostgreSQL:  localhost:5432 (user: postgres, pass: postgres123)" -ForegroundColor White
Write-Host "  LocalStack:  localhost:4566" -ForegroundColor White
Write-Host "  CORS Proxy:  localhost:3001 (routes /api/* to Lambda)" -ForegroundColor White
Write-Host ""
Write-Host "  To start the frontend:" -ForegroundColor Yellow
Write-Host "    cd frontend" -ForegroundColor White
Write-Host "    npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "  Frontend will be at: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  API proxy at:        http://localhost:3001" -ForegroundColor Cyan
Write-Host ""
Write-Host "  To redeploy after Lambda code changes:" -ForegroundColor Yellow
Write-Host "    cd infra" -ForegroundColor White
Write-Host '    $env:AWS_ENDPOINT_URL="http://localhost:4566"' -ForegroundColor White
Write-Host '    $env:AWS_ACCESS_KEY_ID="test"' -ForegroundColor White
Write-Host '    $env:AWS_SECRET_ACCESS_KEY="test"' -ForegroundColor White
Write-Host "    terraform apply -auto-approve" -ForegroundColor White
Write-Host ""
Write-Host "  To stop everything:" -ForegroundColor Yellow
Write-Host "    docker compose down" -ForegroundColor White
Write-Host "    Stop-Process -Id $($proxyProcess.Id) -ErrorAction SilentlyContinue" -ForegroundColor White
Write-Host ""
