# Segurança

Use secret manager, rotação e credenciais separadas por ambiente. Restrinja CORS/hosts, publique apenas por HTTPS e mantenha banco/Redis privados.

Refresh tokens são rotacionados e armazenados por hash; reutilização revoga sessões ativas. RBAC inicia em `USER`; rotas administrativas devem usar `require_roles` ou `require_permission`.

Restrinja e exporte auditoria para armazenamento imutável conforme a política LGPD. Nunca registre tokens, senhas, conteúdo financeiro sensível ou Authorization.
