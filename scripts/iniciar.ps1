param(
    [switch]$Build
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot

try {
    docker info *> $null
    if ($LASTEXITCODE -ne 0) {
        throw @'
O Docker Desktop nao esta em execucao.
Abra o Docker Desktop, aguarde aparecer "Engine running" e tente novamente.
'@
    }

    $composeArgs = @('compose', 'up', '-d')
    if ($Build) {
        $composeArgs += '--build'
    }

    docker @composeArgs
    if ($LASTEXITCODE -ne 0) {
        throw 'Nao foi possivel iniciar o CRMoney. Execute "docker compose logs" para consultar os erros.'
    }

    Write-Host ''
    Write-Host 'CRMoney iniciado em segundo plano.' -ForegroundColor Green
    Write-Host 'Aplicacao: http://localhost:8082'
    Write-Host 'API:       http://localhost:8000/docs'
    Write-Host 'Login:     admin@crmoney.com / Admin@123'
    Write-Host ''
    Write-Host 'Para consultar o estado: docker compose ps'
    Write-Host 'Para acompanhar os logs: docker compose logs -f'
    Write-Host 'Para parar: .\scripts\parar.ps1'
} finally {
    Pop-Location
}
