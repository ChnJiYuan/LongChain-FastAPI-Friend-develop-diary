@echo off
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$apiKey = "qsnnb666"
$desktopExe = Join-Path $repoRoot "frontend\release\Membot.exe"
$healthUrls = @(
  "http://localhost:8000/health",
  "http://localhost:8000/api/v1/memory/health",
  "http://localhost:8000/api/v1/image/health"
)

function Require-Docker {
  try { docker info | Out-Null }
  catch {
    Write-Error "Docker Desktop 未运行或未安装，请先启动 Docker 后再重试。"
    exit 1
  }
}

function Wait-Health {
  param([int]$Retries = 30, [int]$DelaySeconds = 2)
  Write-Host "等待后端健康检查通过..." -ForegroundColor Cyan
  for ($i = 0; $i -lt $Retries; $i++) {
    $allOk = $true
    foreach ($url in $healthUrls) {
      try {
        $resp = Invoke-RestMethod -UseBasicParsing -Headers @{ "X-API-Key" = $apiKey } -Uri $url -TimeoutSec 5
        Write-Host "$url => OK" -ForegroundColor Green
      } catch {
        $allOk = $false
        Write-Host "$url => 未就绪" -ForegroundColor Yellow
      }
    }
    if ($allOk) { return }
    Start-Sleep -Seconds $DelaySeconds
  }
  Write-Warning "健康检查未全部通过，继续启动前端（可稍后再重试）。"
}

Write-Host "定位仓库目录: $repoRoot" -ForegroundColor Cyan
Set-Location $repoRoot

Require-Docker

Write-Host "启动 Docker Compose (backend + frontend + DB + Milvus)..." -ForegroundColor Cyan
docker-compose up -d --build

Wait-Health

if (Test-Path $desktopExe) {
  Write-Host "启动桌面端 (生产包)..." -ForegroundColor Cyan
  Start-Process -FilePath $desktopExe | Out-Null
} else {
  Write-Warning "未找到生产版 exe：$desktopExe`n请先在 frontend/ 运行 npm run build && npm run electron:build"
}

Write-Host "`n全部启动完成：" -ForegroundColor Green
Write-Host "  前端（浏览器）: http://localhost:5173"
Write-Host "  API           : http://localhost:8000"
Write-Host "  桌面端        : " -NoNewline
if (Test-Path $desktopExe) { Write-Host "已启动生产版 exe ($desktopExe)" }
else { Write-Host "未启动（缺少 exe）" }
