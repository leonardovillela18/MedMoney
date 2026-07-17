# Operações

Monitore disponibilidade, latência p95/p99, 5xx, workers, conexões do banco, Redis, storage e jobs. Logs JSON usam `X-Request-ID` para correlação.

Execute `scripts/backup.sh` diariamente com `DATABASE_URL`, `BACKUP_DIR` e `BACKUP_RETENTION_DAYS`. Mantenha cópia criptografada fora da região e teste `scripts/restore.sh` em ambiente isolado. Versione também comprovantes.

Alertas mínimos: `/ready` indisponível, 5xx sustentado, latência elevada, backup ausente e recursos próximos do limite. `/metrics` é mínimo; conecte a porta de observabilidade ao provedor adotado para métricas e tracing detalhados.
