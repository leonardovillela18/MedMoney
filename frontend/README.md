# Frontend

Requer Node 22. Copie `.env.example` para `.env` e execute `npm ci` e `npm run dev`. Valide com `npm run lint` e `npm run build`.

O cliente renova tokens de forma centralizada, serializa tentativas concorrentes, exibe estado offline e possui limite global de erros. Em produção, é servido pelo Nginx com cache de assets e fallback de SPA.
