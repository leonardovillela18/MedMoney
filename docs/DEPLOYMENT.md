# Deploy

O proxy do frontend usa o nome interno `backend` ao encaminhar chamadas de
`/api/` e preserva o dominio publico em `X-Forwarded-Host`. Mantenha `backend`
em `TRUSTED_HOSTS`; dominios gerados pela plataforma de hospedagem nao precisam
ser duplicados nessa variavel quando a API e acessada pelo proxy do frontend.

O pipeline em `.github/workflows/ci.yml` valida backend, migrações, cobertura, frontend, dependências e imagens Docker. Promova as mesmas imagens por desenvolvimento, homologação e produção, trocando apenas configuração e segredos.

Em produção, termine TLS na borda, execute múltiplas réplicas stateless, mantenha uploads em storage compartilhado e use PostgreSQL/Redis gerenciados. O entrypoint migra antes dos workers; com várias réplicas, use um job único de release.

Faça smoke tests em `/live`, `/ready` e no login. Migrações destrutivas devem seguir expansão/contração.
