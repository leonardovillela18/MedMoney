param(
    [switch]$Build
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot

try {
    $composeArgs = @('compose', 'up', '-d')
    if ($Build) {
        $composeArgs += '--build'
    }

    docker @composeArgs
    if ($LASTEXITCODE -ne 0) {
        throw 'Não foi possível iniciar o MedFinance.'
    }

    Write-Host ''
    Write-Host 'MedFinance iniciado em segundo plano.' -ForegroundColor Green
    Write-Host 'Aplicação: http://localhost:8082'
    Write-Host 'API:       http://localhost:8000/docs'
    Write-Host 'Login:     admin@medmoney.com / Admin@123'
    Write-Host ''
    Write-Host 'Para consultar o estado: docker compose ps'
    Write-Host 'Para acompanhar os logs: docker compose logs -f'
    Write-Host 'Para parar: .\scripts\parar.ps1'
} finally {
    Pop-Location
}

