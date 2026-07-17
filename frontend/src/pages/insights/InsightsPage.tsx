import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { AlertTriangle, Info, ShieldAlert, TrendingUp } from 'lucide-react'
import { ExpenseCard } from '@/components/expenses/ExpenseCard'
import { InsightList } from '@/components/insights/InsightList'
import { InsightTimeline } from '@/components/insights/InsightTimeline'
import { insightsService } from '@/services/insights'
type View = 'panel' | 'list' | 'history'
const money = (n: number) =>
  n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
export function InsightsPage() {
  const [view, setView] = useState<View>('panel'),
    [category, setCategory] = useState(''),
    [severity, setSeverity] = useState(''),
    [status, setStatus] = useState('')
  const dashboard = useQuery({
      queryKey: ['insights-dashboard'],
      queryFn: insightsService.dashboard,
      staleTime: 60_000,
    }),
    list = useQuery({
      queryKey: ['insights', category, severity, status],
      queryFn: () =>
        insightsService.list({
          page_size: 100,
          categoria: category || undefined,
          severidade: severity || undefined,
          status: status || undefined,
        }),
      staleTime: 60_000,
    })
  if (dashboard.isLoading || list.isLoading)
    return (
      <div className="grid gap-4 sm:grid-cols-3">
        {[1, 2, 3, 4].map((x) => (
          <div className="h-32 animate-pulse rounded-xl bg-slate-100" key={x} />
        ))}
      </div>
    )
  const d = dashboard.data!,
    items = list.data?.items ?? []
  return (
    <div>
      <header className="mb-6">
        <p className="text-sm font-medium text-blue-600">
          Financial Intelligence Engine
        </p>
        <h1 className="mt-1 text-2xl font-bold">
          Insights que ajudam você a decidir.
        </h1>
        <p className="mt-2 max-w-3xl text-sm text-slate-500">
          Análises determinísticas geradas automaticamente quando seus dados
          mudam. Sem chatbot e sem IA generativa.
        </p>
      </header>
      <nav className="mb-6 flex gap-1 rounded-xl border bg-white p-1">
        {(
          [
            ['panel', 'Painel'],
            ['list', 'Lista de Insights'],
            ['history', 'Histórico'],
          ] as [View, string][]
        ).map(([k, label]) => (
          <button
            className={`rounded-lg px-4 py-2 text-sm font-medium ${view === k ? 'bg-blue-600 text-white' : 'text-slate-500'}`}
            onClick={() => setView(k)}
            key={k}
          >
            {label}
          </button>
        ))}
      </nav>
      {view === 'panel' && (
        <div className="space-y-5">
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <ExpenseCard
              label="Insights ativos"
              value={String(d.total)}
              icon={TrendingUp}
            />
            <ExpenseCard
              label="Informativos"
              value={String(d.counts.Informativo ?? 0)}
              icon={Info}
            />
            <ExpenseCard
              label="Atenção"
              value={String(d.counts.Atenção ?? 0)}
              icon={AlertTriangle}
              tone="amber"
            />
            <ExpenseCard
              label="Críticos"
              value={String(d.counts.Crítico ?? 0)}
              icon={ShieldAlert}
              tone="red"
            />
          </div>
          <section className="card p-5">
            <h2 className="font-semibold">Projeções históricas do mês</h2>
            <p className="mt-1 text-xs text-slate-400">
              Ritmo observado até hoje, sem dados inventados.
            </p>
            <div className="mt-5 grid gap-4 sm:grid-cols-3 xl:grid-cols-5">
              <div>
                <small>Receita projetada</small>
                <p className="mt-1 text-xl font-bold">
                  {money(d.projections.month_revenue)}
                </p>
              </div>
              <div>
                <small>Lucro projetado</small>
                <p className="mt-1 text-xl font-bold">
                  {money(d.projections.month_profit)}
                </p>
              </div>
              <div>
                <small>Impostos estimados</small>
                <p className="mt-1 text-xl font-bold">
                  {money(d.projections.taxes)}
                </p>
              </div>
              <div>
                <small>Fluxo projetado</small>
                <p className="mt-1 text-xl font-bold">{money(d.projections.cashflow)}</p>
              </div>
              <div>
                <small>Meta de referência</small>
                <p className="mt-1 text-xl font-bold">{d.projections.goal_progress.toFixed(0)}%</p>
              </div>
            </div>
          </section>
          <h2 className="font-semibold">Maior prioridade</h2>
          <InsightList items={d.highlights} />
        </div>
      )}
      {view === 'list' && (
        <>
          <div className="mb-4 flex flex-wrap gap-2">
            <select
              className="field mt-0 w-auto"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              <option value="">Todas as categorias</option>
              {[
                'Receita',
                'Lucro',
                'Impostos',
                'Contratantes',
                'Plantões',
                'Despesas',
                'Fluxo de Caixa',
                'Metas',
                'Recebimentos',
                'Notas Fiscais',
              ].map((x) => (
                <option key={x}>{x}</option>
              ))}
            </select>
            <select
              className="field mt-0 w-auto"
              value={severity}
              onChange={(e) => setSeverity(e.target.value)}
            >
              <option value="">Todas as severidades</option>
              {['Informativo', 'Atenção', 'Crítico'].map((x) => (
                <option key={x}>{x}</option>
              ))}
            </select>
            <select
              className="field mt-0 w-auto"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
            >
              <option value="">Todos os status</option>
              {['Novo', 'Visualizado', 'Arquivado'].map((x) => (
                <option key={x}>{x}</option>
              ))}
            </select>
          </div>
          <InsightList items={items} />
        </>
      )}
      {view === 'history' && (
        <section className="card p-6">
          <InsightTimeline items={items} />
        </section>
      )}
    </div>
  )
}
