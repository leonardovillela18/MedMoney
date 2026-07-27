$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot

try {
    docker compose down
    if ($LASTEXITCODE -ne 0) {
        throw 'Nao foi possivel parar o CRMoney.'
    }
    Write-Host 'CRMoney encerrado.' -ForegroundColor Green
} finally {
    Pop-Location
}
