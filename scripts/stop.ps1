$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$stateDir = Join-Path $env:TEMP "volbacktest-launcher"

function Stop-LauncherProcess {
    param(
        [string]$PidFile,
        [string]$ExpectedCommand
    )

    if (-not (Test-Path -LiteralPath $PidFile)) {
        return
    }

    $processId = Get-Content -LiteralPath $PidFile -ErrorAction SilentlyContinue
    if ($processId -and $processId -match "^\d+$") {
        $process = Get-CimInstance Win32_Process -Filter "ProcessId = $processId" -ErrorAction SilentlyContinue
        if ($process -and $process.CommandLine -like "*$ExpectedCommand*") {
            Stop-Process -Id ([int]$processId) -Force
        }
    }
    Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
}

function Wait-PortReleased {
    param([int]$Port)

    for ($attempt = 0; $attempt -lt 20; $attempt++) {
        if (-not (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)) {
            return
        }
        Start-Sleep -Milliseconds 250
    }
    throw "Port $Port is still in use."
}

Stop-LauncherProcess `
    -PidFile (Join-Path $stateDir "api.pid") `
    -ExpectedCommand "uvicorn apps.api.main:app"
Stop-LauncherProcess `
    -PidFile (Join-Path $stateDir "web.pid") `
    -ExpectedCommand "Volatility-Trading-Backtest"

Wait-PortReleased -Port 9000
Wait-PortReleased -Port 5173

Write-Host "Volatility Trading Backtest services stopped." -ForegroundColor Green
