param(
    [switch]$NoBrowser,
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$webRoot = Join-Path $root "apps\web"
$python = "E:\anaconda\envs\Quant1.0\python.exe"
$stateDir = Join-Path $env:TEMP "volbacktest-launcher"
$apiUrl = "http://127.0.0.1:9000/api/v1/catalog"
$webUrl = "http://127.0.0.1:5173"

function Test-Endpoint {
    param(
        [string]$Url,
        [string]$ExpectedText
    )

    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 2
        return $response.StatusCode -eq 200 -and $response.Content.Contains($ExpectedText)
    }
    catch {
        return $false
    }
}

function Wait-Endpoint {
    param(
        [string]$Url,
        [string]$ExpectedText,
        [string]$Name
    )

    for ($attempt = 0; $attempt -lt 60; $attempt++) {
        if (Test-Endpoint -Url $Url -ExpectedText $ExpectedText) {
            return
        }
        Start-Sleep -Milliseconds 500
    }
    throw "$Name did not become ready. Logs: $stateDir"
}

if (-not (Test-Path -LiteralPath $python)) {
    throw "Quant1.0 Python was not found at $python"
}

$node = (Get-Command node.exe -ErrorAction SilentlyContinue).Source
if (-not $node) {
    throw "Node.js was not found. Install Node.js 24 and retry."
}

New-Item -ItemType Directory -Path $stateDir -Force | Out-Null

if (-not $SkipInstall) {
    & $python -c "import fastapi, matplotlib, pandas, volbacktest" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing Python dependencies into Quant1.0..."
        & $python -m pip install -e "${root}[dev]"
        if ($LASTEXITCODE -ne 0) {
            throw "Python dependency installation failed."
        }
    }

    if (-not (Test-Path -LiteralPath (Join-Path $webRoot "node_modules"))) {
        Write-Host "Installing frontend dependencies..."
        & npm.cmd install --prefix $webRoot
        if ($LASTEXITCODE -ne 0) {
            throw "Frontend dependency installation failed."
        }
    }
}

if (-not (Test-Endpoint -Url $apiUrl -ExpectedText "short_strangle")) {
    if (Get-NetTCPConnection -LocalPort 9000 -State Listen -ErrorAction SilentlyContinue) {
        throw "Port 9000 is already used by another application."
    }
    $apiProcess = Start-Process `
        -FilePath $python `
        -ArgumentList "-m", "uvicorn", "apps.api.main:app", "--host", "127.0.0.1", "--port", "9000" `
        -WorkingDirectory $root `
        -RedirectStandardOutput (Join-Path $stateDir "api-out.log") `
        -RedirectStandardError (Join-Path $stateDir "api-err.log") `
        -WindowStyle Hidden `
        -PassThru
    Set-Content -LiteralPath (Join-Path $stateDir "api.pid") -Value $apiProcess.Id
}

$viteScript = Join-Path $webRoot "node_modules\vite\bin\vite.js"
if (-not (Test-Endpoint -Url $webUrl -ExpectedText "Vol Backtester")) {
    if (Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue) {
        throw "Port 5173 is already used by another application."
    }
    if (-not (Test-Path -LiteralPath $viteScript)) {
        throw "Vite is missing. Run npm install in apps\web."
    }
    $webProcess = Start-Process `
        -FilePath $node `
        -ArgumentList $viteScript, "--host", "127.0.0.1", "--port", "5173" `
        -WorkingDirectory $webRoot `
        -RedirectStandardOutput (Join-Path $stateDir "web-out.log") `
        -RedirectStandardError (Join-Path $stateDir "web-err.log") `
        -WindowStyle Hidden `
        -PassThru
    Set-Content -LiteralPath (Join-Path $stateDir "web.pid") -Value $webProcess.Id
}

Wait-Endpoint -Url $apiUrl -ExpectedText "short_strangle" -Name "Backtest API"
Wait-Endpoint -Url $webUrl -ExpectedText "Vol Backtester" -Name "Trading Command Center"

Write-Host ""
Write-Host "Volatility Trading Backtest is running:" -ForegroundColor Green
Write-Host $webUrl -ForegroundColor Cyan
Write-Host "Run stop.bat to stop the local services."

if (-not $NoBrowser) {
    Start-Process $webUrl
}
