import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Activity, Clock, Coins, Percent, Stethoscope } from 'lucide-react'
import { AnalyticsCard } from '@/components/analytics/AnalyticsCard'
import { AnalyticsChart } from '@/components/analytics/AnalyticsChart'
import { AnalyticsGrid } from '@/components/analytics/AnalyticsGrid'
import { ExecutiveSummary } from '@/components/analytics/ExecutiveSummary'
import { Heatmap } from '@/components/analytics/Heatmap'
import { KPICard } from '@/components/analytics/KPICard'
import { RankingTable } from '@/components/analytics/RankingTable'
import { ReportCard } from '@/components/analytics/ReportCard'
import { analyticsService } from '@/services/analytics'
import { contractorsService } from '@/services/contractors'
import { expensesService } from '@/services/expenses'
type Tab =
  | 'summary'
  | 'revenue'
  | 'shifts'
  | 'contractors'
  | 'specialties'
  | 'expenses'
  | 'profit'
  | 'tax'
  | 'comparisons'
  | 'export'
const money = (n: number) =>
  n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
const tabs: [Tab, string][] = [
  ['summary', 'Resumo Executivo'],
  ['revenue', 'Receitas'],
  ['shifts', 'Plantões'],
  ['contractors', 'Contratantes'],
  ['specialties', 'Especialidades'],
  ['expenses', 'Despesas'],
  ['profit', 'Lucro'],
  ['tax', 'Tributação'],
  ['comparisons', 'Comparativos'],
  ['export', 'Exportação'],
]
function Skeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-3">
      {[1, 2, 3, 4, 5, 6].map((x) => (
        <div className="h-36 animate-pulse rounded-xl bg-slate-100" key={x} />
      ))}
    </div>
  )
}
export function AnalyticsPage() {
  const [tab, setTab] = useState<Tab>('summary'),
    [from, setFrom] = useState(''),
    [to, setTo] = useState(''),
    [contractor, setContractor] = useState(''),
    [specialty, setSpecialty] = useState(''),
    [city, setCity] = useState(''),
    [shiftType, setShiftType] = useState(''),
    [category, setCategory] = useState(''),
    [status, setStatus] = useState('')
  const params = useMemo(
    () => ({ date_from: from || undefined, date_to: to || undefined, contractor_id: contractor || undefined, specialty: specialty || undefined, city: city || undefined, type: shiftType || undefined, category_id: category || undefined, status: status || undefined }),
    [from, to, contractor, specialty, city, shiftType, category, status]
  )
  const contractorOptions = useQuery({ queryKey: ['contractors', 'analytics-filter'], queryFn: () => contractorsService.list({ page_size: 100 }), staleTime: 300_000 })
  const categoryOptions = useQuery({ queryKey: ['expense-categories'], queryFn: expensesService.categories, staleTime: 300_000 })
  const executive = useQuery({
    queryKey: ['analytics', 'executive', params],
    queryFn: () => analyticsService.executive(params),
    staleTime: 60_000,
  })
  const revenue = useQuery({
    queryKey: ['analytics', 'revenue', params],
    queryFn: () => analyticsService.revenue(params),
    enabled: tab === 'revenue' || tab === 'specialties',
    staleTime: 60_000,
  })
  const shifts = useQuery({
    queryKey: ['analytics', 'shifts', params],
    queryFn: () => analyticsService.shifts(params),
    enabled: tab === 'shifts',
    staleTime: 60_000,
  })
  const expenses = useQuery({
    queryKey: ['analytics', 'expenses', params],
    queryFn: () => analyticsService.expenses(params),
    enabled: tab === 'expenses',
    staleTime: 60_000,
  })
  const profit = useQuery({
    queryKey: ['analytics', 'profit', params],
    queryFn: () => analyticsService.profit(params),
    enabled: tab === 'profit',
    staleTime: 60_000,
  })
  const contractors = useQuery({
    queryKey: ['analytics', 'contractors', params],
    queryFn: () => analyticsService.contractors(params),
    enabled: tab === 'contractors',
    staleTime: 60_000,
  })
  const loading =
    executive.isLoading ||
    (tab === 'revenue' && revenue.isLoading) ||
    (tab === 'shifts' && shifts.isLoading) ||
    (tab === 'expenses' && expenses.isLoading) ||
    (tab === 'profit' && profit.isLoading) ||
    (tab === 'contractors' && contractors.isLoading)
  const e = executive.data
  return (
    <div>
      <header className="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-blue-600">
            Analytics & Business Intelligence
          </p>
          <h1 className="mt-1 text-2xl font-bold">
            Perguntas estratégicas, respondidas pelos seus dados.
          </h1>
          <p className="mt-2 text-sm text-slate-500">
            Indicadores agregados no servidor e sempre restritos ao seu
            histórico financeiro.
          </p>
        </div>
        <div className="flex gap-2">
          <label className="text-xs text-slate-500">
            De
            <input
              className="field block"
              type="date"
              value={from}
              onChange={(x) => setFrom(x.target.value)}
            />
          </label>
          <label className="text-xs text-slate-500">
            Até
            <input
              className="field block"
              type="date"
              value={to}
              onChange={(x) => setTo(x.target.value)}
            />
          </label>
        </div>
      </header>
      <section className="mb-4 grid gap-2 rounded-xl border bg-white p-3 sm:grid-cols-2 lg:grid-cols-6">
        <select className="field mt-0" value={contractor} onChange={(e)=>setContractor(e.target.value)}><option value="">Todos os contratantes</option>{contractorOptions.data?.items.map(x=><option value={x.id} key={x.id}>{x.name}</option>)}</select>
        <input className="field mt-0" placeholder="Especialidade" value={specialty} onChange={(e)=>setSpecialty(e.target.value)}/>
        <input className="field mt-0" placeholder="Cidade" value={city} onChange={(e)=>setCity(e.target.value)}/>
        <input className="field mt-0" placeholder="Tipo de plantão" value={shiftType} onChange={(e)=>setShiftType(e.target.value)}/>
        <select className="field mt-0" value={category} onChange={(e)=>setCategory(e.target.value)}><option value="">Todas as categorias</option>{categoryOptions.data?.map(x=><option value={x.id} key={x.id}>{x.nome}</option>)}</select>
        <select className="field mt-0" value={status} onChange={(e)=>setStatus(e.target.value)}><option value="">Todos os status</option>{['Agendado','Realizado','Recebido','Pendente','Pago','Atrasado','Cancelado'].map(x=><option key={x}>{x}</option>)}</select>
      </section>
      <nav className="mb-6 flex gap-1 overflow-x-auto rounded-xl border bg-white p-1">
        {tabs.map(([k, label]) => (
          <button
            type="button"
            className={`whitespace-nowrap rounded-lg px-3 py-2 text-sm font-medium ${tab === k ? 'bg-blue-600 text-white' : 'text-slate-500 hover:bg-slate-50'}`}
            onClick={() => setTab(k)}
            key={k}
          >
            {label}
          </button>
        ))}
      </nav>
      {loading || !e ? (
        <Skeleton />
      ) : (
        <>
          {tab === 'summary' && (
            <div className="space-y-5">
              <ExecutiveSummary kpis={e.kpis} />
              <AnalyticsGrid>
                <AnalyticsChart
                  title="Receita mensal"
                  question="Como a receita evoluiu ao longo dos meses?"
                  data={e.revenue.monthly}
                  type="area"
                />
                <AnalyticsChart
                  title="Lucro mensal"
                  question="A operação está gerando mais resultado líquido?"
                  data={e.profit.monthly.map((x) => ({
                    label: x.label,
                    value: x.net,
                  }))}
                  type="line"
                />
              </AnalyticsGrid>
              <AnalyticsGrid>
                <RankingTable
                  title="Top 10 hospitais"
                  items={e.revenue.by_hospital}
                  format={money}
                />
                <RankingTable
                  title="Top 10 despesas"
                  items={e.expenses.top}
                  format={money}
                />
              </AnalyticsGrid>
            </div>
          )}
          {tab === 'revenue' && revenue.data && (
            <div className="space-y-5">
              <div className="grid gap-4 sm:grid-cols-3">
                <AnalyticsCard
                  label="Receita prevista"
                  value={money(revenue.data.expected)}
                  icon={Coins}
                />
                <AnalyticsCard
                  label="Receita recebida"
                  value={money(revenue.data.received)}
                  icon={Coins}
                />
                <AnalyticsCard
                  label="Receita atrasada"
                  value={money(revenue.data.overdue)}
                  icon={Activity}
                />
              </div>
              <AnalyticsGrid>
                <AnalyticsChart
                  title="Receita mensal"
                  question="Quais meses geraram mais caixa?"
                  data={revenue.data.monthly}
                  type="area"
                />
                <AnalyticsChart
                  title="Receita acumulada"
                  question="Quanto a receita cresceu no tempo?"
                  data={revenue.data.accumulated}
                  type="line"
                />
                <AnalyticsChart
                  title="Receita anual"
                  question="Como os anos se comparam?"
                  data={revenue.data.annual}
                />
                <AnalyticsChart
                  title="Receita por tipo de plantão"
                  question="Quais formatos geram mais receita?"
                  data={revenue.data.by_type.map((x) => ({
                    label: x.name,
                    value: x.value,
                  }))}
                />
              </AnalyticsGrid>
              <AnalyticsGrid>
                <RankingTable
                  title="Receita por hospital"
                  items={revenue.data.by_hospital}
                  format={money}
                />
                <RankingTable
                  title="Receita por cidade"
                  items={revenue.data.by_city}
                  format={money}
                />
              </AnalyticsGrid>
              <RankingTable
                title="Top 10 recebimentos"
                items={revenue.data.top_receivables}
                format={money}
              />
            </div>
          )}
          {tab === 'shifts' && shifts.data && (
            <div className="space-y-5">
              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <AnalyticsCard
                  label="Quantidade"
                  value={String(shifts.data.count)}
                  icon={Stethoscope}
                />
                <AnalyticsCard
                  label="Horas trabalhadas"
                  value={`${shifts.data.hours.toFixed(1)}h`}
                  icon={Clock}
                />
                <AnalyticsCard
                  label="Diurnos"
                  value={String(shifts.data.day)}
                  icon={Activity}
                />
                <AnalyticsCard
                  label="Noturnos"
                  value={String(shifts.data.night)}
                  icon={Activity}
                />
              </div>
              <Heatmap data={shifts.data.heatmap} />
              <AnalyticsGrid>
                <RankingTable
                  title="Plantões por hospital"
                  items={shifts.data.by_hospital}
                />
                <RankingTable
                  title="Plantões por dia da semana"
                  items={shifts.data.by_weekday}
                />
              </AnalyticsGrid>
            </div>
          )}
          {tab === 'contractors' && contractors.data && (
            <section className="card overflow-x-auto">
              <table className="w-full min-w-[850px] text-sm">
                <thead className="bg-slate-50 text-left text-xs uppercase text-slate-400">
                  <tr>
                    {[
                      'Contratante',
                      'Faturamento',
                      'Plantões',
                      'Ticket médio',
                      'Atraso médio',
                      'Participação',
                    ].map((x) => (
                      <th className="p-3" key={x}>
                        {x}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {contractors.data.ranking.map((x) => (
                    <tr className="border-t" key={x.id}>
                      <td className="p-3 font-medium">{x.name}</td>
                      <td>{money(x.revenue)}</td>
                      <td>{x.shifts}</td>
                      <td>{money(x.average_ticket)}</td>
                      <td>
                        {x.average_delay === null
                          ? 'Sem dados'
                          : `${x.average_delay.toFixed(1)} dias`}
                      </td>
                      <td>{x.share.toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          )}
          {tab === 'specialties' && revenue.data && (
            <AnalyticsGrid>
              <RankingTable
                title="Top 10 especialidades"
                items={revenue.data.by_specialty}
                format={money}
              />
              <AnalyticsChart
                title="Receita por especialidade"
                question="Quais especialidades concentram maior retorno?"
                data={revenue.data.by_specialty.map((x) => ({
                  label: x.name,
                  value: x.value,
                }))}
              />
            </AnalyticsGrid>
          )}
          {tab === 'expenses' && expenses.data && (
            <div className="space-y-5">
              <div className="grid gap-4 sm:grid-cols-3">
                <AnalyticsCard
                  label="Despesas totais"
                  value={money(expenses.data.total)}
                  icon={Coins}
                />
                <AnalyticsCard
                  label="Fixas"
                  value={money(expenses.data.fixed)}
                  icon={Coins}
                />
                <AnalyticsCard
                  label="Variáveis"
                  value={money(expenses.data.variable)}
                  icon={Coins}
                />
              </div>
              <AnalyticsGrid>
                <AnalyticsChart
                  title="Despesas mensais"
                  question="Os custos estão crescendo?"
                  data={expenses.data.monthly}
                  type="area"
                />
                <AnalyticsChart
                  title="Fixas x variáveis"
                  question="Qual estrutura de custo predomina?"
                  data={[
                    { label: 'Fixas', value: expenses.data.fixed },
                    { label: 'Variáveis', value: expenses.data.variable },
                  ]}
                />
                <RankingTable
                  title="Categorias que mais consomem"
                  items={expenses.data.by_category}
                  format={money}
                />
                <RankingTable
                  title="Fornecedores mais caros"
                  items={expenses.data.by_supplier}
                  format={money}
                />
              </AnalyticsGrid>
            </div>
          )}
          {tab === 'profit' && profit.data && (
            <div className="space-y-5">
              <div className="grid gap-4 sm:grid-cols-4">
                <AnalyticsCard
                  label="Lucro bruto"
                  value={money(profit.data.gross)}
                  icon={Coins}
                />
                <AnalyticsCard
                  label="Lucro líquido"
                  value={money(profit.data.net)}
                  icon={Coins}
                />
                <AnalyticsCard
                  label="Margem líquida"
                  value={`${profit.data.net_margin.toFixed(1)}%`}
                  icon={Percent}
                />
                <AnalyticsCard
                  label="Margem operacional"
                  value={`${profit.data.operating_margin.toFixed(1)}%`}
                  icon={Percent}
                />
              </div>
              <AnalyticsChart
                title="Evolução do lucro"
                question="A margem está melhorando ao longo do tempo?"
                data={profit.data.monthly.map((x) => ({
                  label: x.label,
                  value: x.net,
                }))}
                type="area"
              />
            </div>
          )}
          {tab === 'tax' && (
            <div className="space-y-5">
              <div className="grid gap-4 sm:grid-cols-3">
                <AnalyticsCard
                  label="Impostos estimados"
                  value={money(e.tax.estimated)}
                  icon={Coins}
                />
                <AnalyticsCard
                  label="Reserva tributária"
                  value={money(e.tax.reserved)}
                  icon={Coins}
                />
                <AnalyticsCard
                  label="Percentual efetivo"
                  value={`${e.tax.effective_percentage.toFixed(1)}%`}
                  icon={Percent}
                />
              </div>
              <AnalyticsChart
                title="Tributação mensal"
                question="Como a reserva sugerida evolui?"
                data={e.tax.monthly}
                type="line"
              />
            </div>
          )}
          {tab === 'comparisons' && (
            <div className="space-y-5">
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                {e.comparisons.map((x) => (
                  <KPICard
                    key={x.label}
                    label={x.label}
                    value={`${money(x.revenue)} · ${x.shifts} plantões · ${x.hours.toFixed(1)}h`}
                  />
                ))}
              </div>
              <AnalyticsChart
                title="Receita por janela"
                question="Qual período recente teve maior produção?"
                data={e.comparisons.map((x) => ({
                  label: x.label,
                  value: x.revenue,
                }))}
              />
            </div>
          )}
          {tab === 'export' && <ReportCard />}
        </>
      )}
    </div>
  )
}
