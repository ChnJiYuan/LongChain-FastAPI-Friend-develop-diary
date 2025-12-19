$ErrorActionPreference = "Stop"

# Paths and ports (override via env vars if needed)
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$apiKey   = "qsnnb666"
$apiPort  = if ($env:API_PORT) { $env:API_PORT } else { 8000 }
$sdRoot   = if ($env:SD_WEBUI_ROOT) { $env:SD_WEBUI_ROOT } else { "D:\UniWorkSpace\WorkPlace4Future\Stable-diffussion\stable-diffusion-webui" }
$sdPort   = if ($env:SD_PORT) { $env:SD_PORT } else { 7860 }
$sdBase   = if ($env:SD_BASE_URL) { $env:SD_BASE_URL } else { "http://localhost:$sdPort" }
$desktopExe = Join-Path $repoRoot "frontend\release\Membot.exe"
$healthUrls = @(
  "http://localhost:$apiPort/health",
  "http://localhost:$apiPort/api/v1/memory/health",
  "http://localhost:$apiPort/api/v1/image/health"
)

function Test-SdHealth {
  param([string]$BaseUrl)
  try {
    $resp = Invoke-RestMethod -UseBasicParsing -Uri "$BaseUrl/sdapi/v1/sd-models" -TimeoutSec 5
    return $resp -ne $null
  } catch {
    return $false
  }
}

function Require-Docker {
  try { docker info | Out-Null }
  catch {
    Write-Error "Docker Desktop is not running. Please start Docker Desktop and retry."
    exit 1
  }
}

function Wait-BackendHealth {
  param([int]$Retries = 30, [int]$DelaySeconds = 2)
  Write-Host "Waiting for backend health checks..." -ForegroundColor Cyan
  for ($i = 0; $i -lt $Retries; $i++) {
    $allOk = $true
    foreach ($url in $healthUrls) {
      try {
        $null = Invoke-RestMethod -UseBasicParsing -Headers @{ "X-API-Key" = $apiKey } -Uri $url -TimeoutSec 5
        Write-Host "$url => OK" -ForegroundColor Green
      } catch {
        $allOk = $false
        Write-Host "$url => waiting" -ForegroundColor Yellow
      }
    }
    if ($allOk) { return }
    Start-Sleep -Seconds $DelaySeconds
  }
  Write-Warning "Backend health checks did not pass in time. The app may still be initializing."
}

function Ensure-LocalSd {
  param(
    [string]$BaseUrl,
    [string]$Root,
    [int]$Port = 7860,
    [int]$Retries = 20,
    [int]$DelaySeconds = 3
  )

  if (Test-SdHealth $BaseUrl) {
    Write-Host "Stable Diffusion already running at $BaseUrl" -ForegroundColor Green
    return
  }

  if (-not (Test-Path $Root)) {
    Write-Warning "Stable Diffusion path not found: $Root. Skipping auto-start."
    return
  }

  Write-Host "Starting Stable Diffusion WebUI ($Root) on port $Port..." -ForegroundColor Cyan
  $env:COMMANDLINE_ARGS="--api --listen --port $Port"
  Start-Process -FilePath (Join-Path $Root 'webui-user.bat') -WorkingDirectory $Root -WindowStyle Minimized | Out-Null

  for ($i = 0; $i -lt $Retries; $i++) {
    if (Test-SdHealth $BaseUrl) {
      Write-Host "Stable Diffusion is ready at $BaseUrl" -ForegroundColor Green
      return
    }
    Start-Sleep -Seconds $DelaySeconds
  }

  Write-Warning "Stable Diffusion did not become healthy within timeout; image API may fail."
}

Write-Host "Workspace: $repoRoot" -ForegroundColor Cyan
Set-Location $repoRoot

# Start SD first (best-effort)
Ensure-LocalSd -BaseUrl $sdBase -Root $sdRoot -Port $sdPort

Require-Docker

Write-Host "Starting Docker Compose (backend + frontend + DB + Milvus)..." -ForegroundColor Cyan
docker-compose up -d --build

Wait-BackendHealth

if (Test-Path $desktopExe) {
  Write-Host "Launching desktop app (if built)..." -ForegroundColor Cyan
  Start-Process -FilePath $desktopExe | Out-Null
} else {
  Write-Warning "Desktop exe not found: $desktopExe`nBuild it via frontend/ npm run build && npm run electron:build"
}

Write-Host "`nReady to use" -ForegroundColor Green
Write-Host "  Web UI        : http://localhost:5173"
Write-Host "  API           : http://localhost:$apiPort"
Write-Host "  SD (expected) : $sdBase"
Write-Host "  Desktop       : " -NoNewline
if (Test-Path $desktopExe) { Write-Host "launched (if built) at $desktopExe" }
else { Write-Host "not built" }
