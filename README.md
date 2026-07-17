# MedMoney

Plataforma financeira para médicos PJ, com módulos de agenda, recebíveis, despesas, impostos, fluxo de caixa, metas, alertas e inteligência financeira.

## Execução local

1. Copie `backend/.env.example` para `backend/.env` e ajuste os valores.
2. Execute `docker compose up --build`.
3. Acesse o frontend em `http://localhost:8082` e a API em `http://localhost:8000/docs`.

Para desenvolvimento sem contêineres, consulte `backend/README.md` e `frontend/README.md`.

## Produção

Use segredos externos, TLS no proxy de borda e execute:

```sh
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Defina `JWT_SECRET_KEY`, `POSTGRES_PASSWORD`, `FRONTEND_ORIGINS` e `TRUSTED_HOSTS`. A configuração recusa JWT fraco e documentação aberta em produção.

Consulte [arquitetura](docs/ARCHITECTURE.md), [deploy](docs/DEPLOYMENT.md), [segurança](docs/SECURITY.md) e [operações](docs/OPERATIONS.md).
