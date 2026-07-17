# Arquitetura

O frontend React/Vite consome uma API FastAPI versionada em `/api/v1`. PostgreSQL é a fonte durável; Redis implementa cache distribuído. Arquivos e filas são expostos por portas, hoje com implementações local e síncrona, prontas para S3/Azure Blob e Celery/RQ.

Autenticação usa access JWT curto e refresh token opaco armazenado apenas como hash, com rotação, detecção de reutilização, revogação por sessão e global. RBAC associa usuários, perfis e permissões. Auditoria registra mutações autenticadas.

Hooks neutros em `app/infrastructure/observability.py` permitem OpenTelemetry, Sentry ou Datadog sem acoplar regras de negócio.
