# CRMoney

Plataforma financeira para médicos PJ, com módulos de agenda, recebíveis, despesas, impostos, fluxo de caixa, metas, alertas e inteligência financeira.

## Execução local

No PowerShell, execute a partir da raiz do projeto:

```powershell
.\scripts\iniciar.ps1
```

O comando inicia os contêineres em segundo plano. Acesse o frontend em `http://localhost:8082` e a API em `http://localhost:8000/docs`.

Use `.\scripts\iniciar.ps1 -Build` somente no primeiro uso ou após alterar dependências/Dockerfiles. Para encerrar:

```powershell
.\scripts\parar.ps1
```

Se o PowerShell bloquear scripts locais, use diretamente `docker compose up -d` para iniciar e `docker compose down` para parar.

Para desenvolvimento sem contêineres, consulte `backend/README.md` e `frontend/README.md`.

## Produção

Use segredos externos, TLS no proxy de borda e execute:

```sh
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Defina `JWT_SECRET_KEY`, `POSTGRES_PASSWORD`, `FRONTEND_ORIGINS` e `TRUSTED_HOSTS`. A configuração recusa JWT fraco e documentação aberta em produção.

Consulte [arquitetura](docs/ARCHITECTURE.md), [deploy](docs/DEPLOYMENT.md), [segurança](docs/SECURITY.md) e [operações](docs/OPERATIONS.md).
