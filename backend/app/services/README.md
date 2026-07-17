# Serviços da API

## Inteligência Tributária

`TaxService` concentra projeções não oficiais, configuração percentual, sincronização automática, simulações e indicadores. `sync` é idempotente por plantão/origem: eventos posteriores de recebimento ou nota atualizam a mesma estimativa quando ligados ao mesmo plantão.

- `estimated`: cálculo decimal da projeção, com arredondamento monetário.
- `sync`: cria ou atualiza estimativas abertas após plantões, recebimentos e notas.
- `dashboard`: agrega estimado, reservado, pendente, lucro líquido projetado, séries e insights.
- `save_setting`: altera o percentual padrão e recalcula apenas estimativas abertas.

Os status `Reservado` e `Pago` preservam o valor projetado já aceito pelo usuário. Nenhum método produz valor fiscal oficial ou guia de recolhimento. A separação entre rota, serviço, repositório e modelo permite integrar futuramente provedores fiscais por novos adaptadores sem alterar a interface atual.

## Fluxo de Caixa Inteligente

`CashflowService` mantém uma projeção somente leitura derivada dos módulos de origem. `sync_source` é o ponto de integração para eventos atuais e futuros; `reconcile` cobre registros históricos de plantões, recebimentos e reservas tributárias sem duplicação pela chave de origem.

- `projection`: calcula saldos, horizontes, séries, insights e alertas.
- `calendar`: agrupa movimentações por dia para o calendário financeiro.
- `simulate`: aplica cenários temporários sem persistir lançamentos.
- `recalculate`: atualiza os saldos projetados em ordem cronológica.

Uma futura integração bancária deverá implementar um adaptador que envie eventos confirmados a `sync_source`. Assim, Open Finance, Pix ou contas bancárias não precisarão alterar Plantões, Recebimentos ou Impostos.

## Gestão Inteligente de Despesas

`ExpenseService` aplica regras de propriedade, categorias, recorrência, indicadores e integração financeira. Toda criação, edição, pagamento, cancelamento ou exclusão sincroniza uma movimentação derivada no `CashflowService`, que recalcula os saldos e o lucro disponível.

- `create`, `update`, `delete`: CRUD com validação, propriedade por usuário e soft delete.
- `categories`: inicializa categorias padrão isoladas por usuário e aceita extensões personalizadas.
- `generate_recurrence`: cria doze ocorrências futuras, vinculadas ao lançamento de origem.
- `dashboard`: agrega despesas fixas/variáveis, categorias, fornecedores, economia e tendências.
- `sync`: publica a despesa prevista ou paga no fluxo de caixa sem duplicação.

Comprovantes são aceitos apenas como PDF, JPG/JPEG ou PNG, até 5 MB, e servidos por endpoint autenticado com validação de propriedade no nome do arquivo. A resposta inclui um estado reservado para OCR futuro, mas nenhuma leitura automática é executada.

### Endpoints

- `GET/POST /api/v1/expenses`
- `GET/PUT/DELETE /api/v1/expenses/{id}`
- `GET /api/v1/expenses/dashboard`
- `GET/POST /api/v1/expenses/categories`
- `POST /api/v1/expenses/upload`
- `GET /api/v1/expenses/receipts/{name}`

## Meu Dia

`TodayService` produz um briefing financeiro determinístico em uma única leitura de API. Ele agrega Plantões, Recebimentos, Notas Fiscais, Despesas, Impostos e Fluxo de Caixa sem persistir números derivados ou executar inteligência artificial.

- `build`: retorna resumo, indicadores, agenda, pagamentos, ações, alertas, insights, comparativos, referência mensal, calendário, gráficos e atividade recente.
- `period_net`: mantém o mesmo critério de receita menos impostos e despesas nos períodos comparados.
- `insights`: aplica apenas regras explicáveis sobre variação de receita, concentração e resultado líquido.
- `message`: seleciona uma mensagem contextual usando resultado, progresso e alertas reais.

Endpoint: `GET /api/v1/today`. A resposta é isolada pelo usuário autenticado e está preparada para cache curto no cliente.

## Financial Intelligence Engine

`FinancialInsightsService` coordena estratégias determinísticas registradas em `ANALYZERS`. Cada estratégia recebe um `InsightContext` compartilhado, produz candidatos explicáveis e não conhece persistência ou interface HTTP. Novas regras exigem apenas uma implementação de `InsightAnalyzer` e seu registro no engine.

O engine faz upsert pela referência estável da regra, arquiva resultados que deixaram de ser verdadeiros e preserva insights visualizados ou arquivados. O banco funciona como cache persistente; o recálculo ocorre após eventos de Plantões, Recebimentos, Despesas e Notas Fiscais. A leitura só aquece o cache quando um usuário com histórico ainda não possui nenhum resultado.

Estratégias atuais:

- tendências de receita e lucro;
- concentração de contratantes nos patamares de 30% a 70%;
- rentabilidade por plantão, contratante, especialidade, dia, semana e horário;
- mês recorde;
- tempo e pontualidade de pagamentos;
- crescimento, concentração, fornecedores e recorrência de despesas.

Endpoints: `GET /api/v1/insights`, `GET /api/v1/insights/{id}`, `GET /api/v1/insights/dashboard` e `POST /api/v1/insights/recalculate`. O endpoint de recálculo existe para operação/diagnóstico; a experiência normal não exibe botão manual.

## Analytics e Business Intelligence

`AnalyticsService` é uma camada somente leitura separada dos serviços operacionais. Ela aplica filtros antes das agregações, restringe todas as consultas ao usuário autenticado e entrega séries, KPIs, rankings, heatmap e comparativos já calculados para o frontend.

O cache em memória possui chave composta por usuário, endpoint e filtros, TTL de 60 segundos e invalidação imediata nos eventos que também atualizam o Financial Intelligence Engine. Em uma futura implantação distribuída, o mesmo contrato pode ser implementado sobre Redis sem alterar rotas ou componentes.

Endpoints especializados:

- `GET /api/v1/analytics`
- `GET /api/v1/analytics/revenue`
- `GET /api/v1/analytics/shifts`
- `GET /api/v1/analytics/expenses`
- `GET /api/v1/analytics/profit`
- `GET /api/v1/analytics/contractors`
- `GET /api/v1/analytics/export?format=csv|xlsx|pdf|svg`

As exportações são produzidas no backend: CSV UTF-8, workbook Excel, relatório executivo PDF com KPIs/insights/comparativos e imagem SVG. `openpyxl` e `reportlab` são carregados somente quando seus respectivos formatos são solicitados.

## Metas Financeiras Inteligentes

`GoalEngine` centraliza cálculo, progresso, status, previsão, insights e comparativos. Cada tipo de meta é uma estratégia registrada em `STRATEGIES`; adicionar novos tipos não exige alterações nos módulos operacionais.

As metas usam um único `GoalContext` por atualização em lote e gravam no máximo um snapshot diário. Plantões, Recebimentos, Despesas e Reservas acionam o motor pelo mesmo coordenador de eventos que invalida Analytics e atualiza Insights.

Regras de segurança e consistência:

- somente `Meta Personalizada` aceita `valor_atual` informado pelo usuário;
- os demais valores são recalculados exclusivamente com dados persistidos;
- simulações nunca são gravadas;
- todas as consultas validam `user_id`;
- exclusões usam soft delete.

Endpoints: `GET/POST /api/v1/goals`, `GET/PUT/DELETE /api/v1/goals/{id}`, `GET /api/v1/goals/dashboard` e `POST /api/v1/goals/simulate`.

## Central Inteligente de Alertas

`AlertEngine` coordena estratégias determinísticas registradas em `RULES`. Cada regra recebe um `AlertContext` isolado por usuário e produz candidatos com contexto, impacto, prioridade, ação e destino. A chave UUID determinística de cada regra permite upsert sem duplicação e resolução automática quando a condição deixa de existir.

O banco é o cache persistente da central. Leituras não reprocessam alertas, exceto pelo aquecimento único de usuários com histórico anterior. O coordenador financeiro executa o motor somente depois de alterações em dados relacionados. Alertas resolvidos podem reabrir após um dia se o problema continuar verdadeiro.

Regras atuais incluem atrasos e vencimentos, notas pendentes ou sem recebimento, inconsistências de plantões, reserva tributária, fluxo negativo, metas, despesas, dependência e atraso de contratantes, cadastro incompleto e adaptação dos insights financeiros já calculados.

`AlertChannel` define a interface de entrega. Apenas `InternalAlertChannel` está ativo; futuros canais Push, e-mail, WhatsApp e SMS podem ser registrados sem alterar o engine.

Endpoints: `GET /api/v1/alerts`, `GET /api/v1/alerts/{id}`, `GET /api/v1/alerts/dashboard`, `PATCH /api/v1/alerts/{id}/read`, `PATCH /api/v1/alerts/{id}/resolve` e `POST /api/v1/alerts/recalculate`.
