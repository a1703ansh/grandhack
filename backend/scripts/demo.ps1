# One-command demo: build the frontend as a static export and serve it
# together with the API on a single port (http://localhost:8000).
#
#   powershell -ExecutionPolicy Bypass -File backend\scripts\demo.ps1
#
# Safe to re-run: dependencies are only installed when missing; the seed graph
# is regenerated every time so the demo always reflects build_seed.py.

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot  = Resolve-Path (Join-Path $scriptDir "..\..")
Set-Location $repoRoot

$venvPython = Join-Path $repoRoot "backend\.venv\Scripts\python.exe"

Write-Host "[1/4] Python environment" -ForegroundColor Cyan
if (-not (Test-Path $venvPython)) {
    Write-Host "      creating backend\.venv ..."
    python -m venv (Join-Path $repoRoot "backend\.venv")
}
& $venvPython -m pip install --quiet --disable-pip-version-check -r (Join-Path $repoRoot "backend\requirements.txt")

Write-Host "[2/4] Building curated seed graph" -ForegroundColor Cyan
& $venvPython (Join-Path $repoRoot "backend\scripts\build_seed.py")

Write-Host "[3/4] Building frontend (static export, same-origin API)" -ForegroundColor Cyan
Push-Location (Join-Path $repoRoot "frontend")
try {
    if (-not (Test-Path "node_modules")) {
        Write-Host "      npm install ..."
        npm install
    }
    # No NEXT_PUBLIC_API_URL: the app auto-detects same-origin when not on :3000.
    npm run build
} finally {
    Pop-Location
}

Write-Host "[4/4] Starting server on http://localhost:8000" -ForegroundColor Cyan
if ($env:GEMINI_API_KEY) {
    Write-Host "      GEMINI_API_KEY detected - narratives will be LLM-enhanced." -ForegroundColor Green
} else {
    Write-Host "      No GEMINI_API_KEY - using offline template narratives (fully functional)." -ForegroundColor Yellow
}
Start-Process "http://localhost:8000"
Set-Location (Join-Path $repoRoot "backend")
& $venvPython -m uvicorn app.main:app --host 127.0.0.1 --port 8000
