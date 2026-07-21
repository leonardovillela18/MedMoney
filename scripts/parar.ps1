$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot

try {
    docker compose down
    if ($LASTEXITCODE -ne 0) {
        throw 'Não foi possível parar o MedFinance.'
    }
    Write-Host 'MedFinance encerrado.' -ForegroundColor Green
} finally {
    Pop-Location
}

